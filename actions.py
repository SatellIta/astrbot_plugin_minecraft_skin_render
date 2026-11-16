import aiohttp
from astrbot.api import logger
import astrbot.api.message_components as Comp
import re
import asyncio

from . import utils, config

async def process_skin_command(session: aiohttp.ClientSession, username: str, rendertype: str) -> list | str:
    """处理 /skin 命令的核心逻辑（使用 nmsr API）"""
    # 1. 验证渲染类型
    rendertype_lower = rendertype.lower()
    is_valid, error_msg = utils.validate_rendertype(rendertype_lower)
    if not is_valid:
        return error_msg

    # 2. 验证玩家是否存在（通过 Mojang API）
    uuid, error_msg = await utils.get_player_uuid(session, username)
    if error_msg:
        return error_msg

    # 3. 构建 nmsr 渲染 URL（nmsr 支持用户名直接作为 identifier）
    resolved_type = utils.resolve_rendertype(rendertype_lower)
    render_url = utils.build_render_url(rendertype_lower, username)
    logger.info(f"为 {username} 生成渲染 URL (nmsr {resolved_type}): {render_url}")

    # 4. 准备结果
    render_desc = f"'{resolved_type}' 渲染"
    if resolved_type != rendertype_lower:
        render_desc += f" (原类型: {rendertype_lower})"
    chain = [
        Comp.Plain(f"这是 {username} 的 {render_desc}：\n"),
        Comp.Image.fromURL(url=render_url)
    ]
    return chain


async def process_randomskin_command(session: aiohttp.ClientSession) -> list | str:
    """
    从 NameMC 随机皮肤页面获取一个随机皮肤，解析第一个玩家名称并返回默认皮肤渲染链。

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
        # 使用 safari17_0 指纹。
        # 注意：NameMC 的 Cloudflare 目前会拦截 curl_cffi 的 chrome120 等 Chrome 指纹
        # （返回 403 + "Just a moment..."），Safari 指纹可正常通过（curl_cffi >= 0.6.0）。
        resp = requests.get(url, headers=headers, impersonate="safari17_0", timeout=20)
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

    # 使用 nmsr 默认渲染类型 'fullbody' 生成结果
    return await process_skin_command(session, player, config.DEFAULT_RENDERTYPE)

async def upload_and_render_custom_skin(
    session: aiohttp.ClientSession,
    uuid: str,
    model_url: str,
    username: str,
    camera_position: dict | None = None,
    camera_focal_point: dict | None = None,
) -> list:
    """
    [已废弃] 自定义模型渲染功能。
    nmsr 不支持自定义模型上传，Starlight Skins 已宕机。
    """
    return [
        Comp.Plain(
            "自定义模型渲染功能暂不可用。\n"
            "原因：原渲染服务器 Starlight Skins 已宕机，新的渲染服务 nmsr 不支持自定义模型上传。\n"
            "如需此功能，可以自行部署 nmsr-rs (https://github.com/NickAcPT/nmsr-rs) 并修改配置。"
        )
    ]

async def process_wallpaper_command(session: aiohttp.ClientSession, wallpaper_id: str, usernames: list[str]) -> list | str:
    """
    [已废弃] 壁纸功能。
    nmsr 不支持壁纸渲染，Starlight Skins 已宕机。
    """
    return "壁纸功能暂不可用：原渲染服务器 Starlight Skins 已宕机，新的渲染服务 nmsr 不支持壁纸功能。"

