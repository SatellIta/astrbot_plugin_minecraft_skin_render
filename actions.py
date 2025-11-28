import aiohttp
from astrbot.api import logger
import astrbot.api.message_components as Comp
import json
from urllib.parse import urlencode
import re
import asyncio

from . import utils, config

async def process_skin_command(session: aiohttp.ClientSession, username: str, rendertype: str) -> list | str:
    """处理 /skin 命令的核心逻辑"""
    # 1. 验证渲染类型
    rendertype_lower = rendertype.lower()
    is_valid, error_msg = utils.validate_rendertype(rendertype_lower)
    if not is_valid:
        return error_msg

    # 2. 获取玩家 UUID
    uuid, error_msg = await utils.get_player_uuid(session, username)
    if error_msg:
        return error_msg

    # 3. 构建渲染 URL
    render_url = utils.build_render_url(rendertype_lower, uuid)
    logger.info(f"为 {username} 生成渲染 URL: {render_url}")

    # 4. 准备结果
    render_desc = f"'{rendertype_lower}' 渲染"
    chain = [
        Comp.Plain(f"这是 {username} 的 {render_desc}：\n"),
        Comp.Image.fromURL(url=render_url)
    ]
    return chain


async def process_randomskin_command(session: aiohttp.ClientSession) -> list | str:
    """
    从 NameMC 随机皮肤页面获取一个随机皮肤，解析第一个玩家名称，获取 UUID 并返回默认皮肤渲染链。

    使用 curl_cffi 的同步请求包装在线程中运行以绕过 Cloudflare。
    """
    try:
        # 延迟导入，避免没有依赖时启动失败
        from curl_cffi import requests
    except Exception as e:
        logger.error(f"缺少 curl_cffi 库或导入失败: {e}")
        return "错误：服务器未安装或无法加载 'curl_cffi' 库，无法访问 NameMC 随机皮肤页面。"

    headers = config.DEFAULT_HEADER

    def fetch_text(url: str) -> str:
        # 使用 chrome120 指纹
        resp = requests.get(url, headers=headers, impersonate="chrome120", timeout=20)
        resp.raise_for_status()
        text = resp.text
        if "<title>Just a moment...</title>" in text:
            raise Exception("被 Cloudflare 5秒盾拦截")
        return text

    # 获取随机皮肤页面
    try:
        html = await asyncio.to_thread(fetch_text, config.NAMEMC_RAMDOM)
    except Exception as e:
        logger.error(f"从 NameMC 获取随机页面失败: {e}")
        return f"错误：无法从 NameMC 获取随机皮肤，请稍后再试。({e})"

    # 解析 skin id
    m = re.search(r'href="/skin/([A-Za-z0-9_-]+)"', html)
    if not m:
        logger.error("在 NameMC 随机页面中未找到 skin id")
        return "错误：未能从 NameMC 随机页面解析出皮肤 ID。"
    skinid = m.group(1)
    skin_url = config.NAMEMC_SKIN.format(skinid=skinid)

    # 请求皮肤页面并解析第一个玩家名
    try:
        skin_html = await asyncio.to_thread(fetch_text, skin_url)
    except Exception as e:
        logger.error(f"获取 NameMC 皮肤页面失败 ({skin_url}): {e}")
        return f"错误：无法访问 NameMC 的皮肤页面，请稍后再试。({e})"

    # 尝试解析玩家名
    player = None
    m2 = re.search(r'/profile/([A-Za-z0-9_]{1,16})', skin_html)
    if m2:
        player = m2.group(1)

    if not player:
        logger.error("未能从皮肤页面解析出玩家名称")
        return "错误：未能从 NameMC 的皮肤页面解析出玩家名称。"

    logger.info(f"从 NameMC 解析到玩家: {player} (skinid={skinid})")

    # 4) 使用默认渲染类型生成结果
    return await process_skin_command(session, player, 'default')

async def upload_and_render_custom_skin(
    session: aiohttp.ClientSession,
    uuid: str,
    model_url: str,
    username: str,
    camera_position: dict | None = None,
    camera_focal_point: dict | None = None,
) -> list:
    """通过模型 URL 构建渲染 URL，使用 urlencode 确保参数正确编码。"""
    endpoint = config.CUSTOM_RENDER_API_ENDPOINT.format(uuid=uuid)

    # 1. 模型 URL 添加欺骗后缀
    tricked_model_url = f"{model_url}#.obj"

    # 2. 准备所有查询参数
    params = {
        "wideModel": tricked_model_url,
        "slimModel": tricked_model_url,
    }

    # 3. 添加相机和焦点参数（转为紧凑的 JSON 字符串）
    cam = camera_position or config.DEFAULT_CAMERA_POSITION
    params["cameraPosition"] = json.dumps(cam, separators=(",", ":"))

    focal = camera_focal_point or config.DEFAULT_CAMERA_FOCAL_POINT
    if focal:
        params["cameraFocalPoint"] = json.dumps(focal, separators=(",", ":"))

    # 4. 使用 urlencode 构建查询字符串
    query_string = urlencode(params)

    # 5. 拼接最终的 URL
    final_url = f"{endpoint}?{query_string}"

    logger.info(f"为 {username} 构建的自定义渲染 URL: {final_url}")

    chain = [
        Comp.Plain(f"这是为 {username} 使用自定义模型生成的渲染图：\n⚠️ 如果是空白图片，请检查上传的模型与渲染皮肤的类型是否一致（标准或纤细）\n"),
        Comp.Image.fromURL(url=final_url),
    ]
    return chain

async def process_wallpaper_command(session: aiohttp.ClientSession, wallpaper_id: str, usernames: list[str]) -> list | str:
    """处理 /wallpaper 命令的核心逻辑"""
    # 1. 验证壁纸ID
    wallpaper_lower = wallpaper_id.lower()
    is_valid, error_msg, max_players = utils.validate_wallpaper(wallpaper_lower)
    if not is_valid:
        return error_msg

    # 2. 检查玩家参数
    if not usernames:
        return (
            f"错误：壁纸 '{wallpaper_lower}' 至少需要1个玩家名称。\n"
            f"用法：/wallpaper {wallpaper_lower} <玩家名1> [玩家名2] ...\n"
            f"该壁纸最多支持 {max_players} 个玩家。"
        )

    # 3. 检查玩家数量上限
    actual_usernames = usernames
    warning_msg = ""
    if len(actual_usernames) > max_players:
        warning_msg = f"⚠️ 注意：壁纸 '{wallpaper_lower}' 最多支持 {max_players} 个玩家，已自动截取前 {max_players} 个。\n\n"
        actual_usernames = actual_usernames[:max_players]

    # 4. 将所有玩家名称转换为UUID
    player_uuids = []
    failed_players = []

    for username in actual_usernames:
        uuid, error_msg_uuid = await utils.get_player_uuid(session, username)
        if error_msg_uuid:
            failed_players.append(username)
            logger.warning(f"无法获取玩家 {username} 的 UUID，跳过该玩家")
        else:
            player_uuids.append(uuid)

    # 5. 检查是否有成功获取的UUID
    if not player_uuids:
        error_list = "\n".join([f"• {player}" for player in failed_players])
        return (
            f"错误：无法获取任何玩家的 UUID。\n"
            f"失败的玩家：\n{error_list}"
        )

    # 6. 如果有部分玩家失败，添加警告信息
    if failed_players:
        failed_list = ", ".join(failed_players)
        warning_msg += f"⚠️ 以下玩家未找到，已跳过：{failed_list}\n\n"

    # 7. 构建壁纸URL
    player_uuids_path = ",".join(player_uuids)
    wallpaper_url = config.WALLPAPER_API_URL.format(
        wallpaper_id=wallpaper_lower,
        playernames=player_uuids_path
    )

    logger.info(f"为壁纸 '{wallpaper_lower}' 生成 URL（{len(player_uuids)} 个玩家）: {wallpaper_url}")

    # 8. 准备结果
    success_players = [name for name in actual_usernames if name not in failed_players]
    players_desc = ", ".join(success_players)
    chain = [
        Comp.Plain(f"{warning_msg}这是壁纸 '{wallpaper_lower}' (玩家: {players_desc})：\n"),
        Comp.Image.fromURL(url=wallpaper_url)
    ]
    return chain

