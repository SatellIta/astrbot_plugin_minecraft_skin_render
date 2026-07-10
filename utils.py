import aiohttp
import os
import asyncio
import uuid as uuid_lib
from astrbot.api import logger

from . import config

async def get_player_uuid(session: aiohttp.ClientSession, username: str) -> tuple[str | None, str | None]:
    """
    通过 Mojang API 获取玩家 UUID，如果传入的已经是UUID，则直接格式化并返回。
    
    Args:
        session: aiohttp.ClientSession
        username: 玩家用户名或UUID
        
    Returns:
        tuple[uuid, error_msg]: 成功返回 (uuid, None)，失败返回 (None, error_msg)
    """
    # 检查传入的 username 是否已经是 UUID
    try:
        # 尝试将输入解析为UUID对象
        parsed_uuid = uuid_lib.UUID(username)
        # 如果成功，格式化为32位无连字符的字符串
        uuid_hex = parsed_uuid.hex
    
        # 验证UUID是否存在
        validation_url = config.MOJANG_API_UUID_URL.format(uuid=uuid_hex)
        async with session.get(validation_url) as response:
            if response.status == 200:
                logger.info(f"UUID '{parsed_uuid}' 验证成功，直接使用: {uuid_hex}")
                return uuid_hex, None
            elif response.status == 404:
                logger.warning(f"UUID '{parsed_uuid}' 格式正确但不存在。")
                return None, f"错误：UUID '{username}' 对应的玩家不存在。"
            else:
                logger.error(f"验证UUID时发生API错误，状态码: {response.status}")
                return None, "验证UUID时发生网络错误。"
    
    except ValueError:
        # 如果不是有效的UUID，则继续执行API查询
        logger.info(f"输入 '{username}' 不是UUID，将作为玩家名进行查询。")

    mojang_url = config.MOJANG_API_URL.format(username=username)
    logger.info(f"正在为 {username} 异步查询 UUID...")
    
    try:
        async with session.get(mojang_url) as response:
            if response.status != 200:
                logger.warning(f"Mojang API 玩家 {username} 未找到 (状态: {response.status})。")
                return None, f"错误：找不到玩家 '{username}'。"
            
            player_data = await response.json()
            uuid = player_data.get("id")
            
            if not uuid:
                logger.error(f"Mojang API 响应中未找到 {username} 的 UUID。")
                return None, "获取玩家数据时出错。"
            
            logger.info(f"成功获取 {username} 的 UUID: {uuid}")
            return uuid, None
            
    except aiohttp.ClientError as e:
        logger.error(f"为 {username} 获取 UUID 时发生 aiohttp ClientError: {e}")
        return None, "查询玩家信息时发生网络错误，请稍后再试。"
    except Exception as e:
        logger.error(f"获取 {username} 的 UUID 时发生未知错误: {e}", exc_info=True)
        return None, "查询玩家信息时发生内部错误。"

def resolve_rendertype(rendertype: str) -> str:
    """
    解析渲染类型，支持 nmsr 原生类型和旧 Starlight 类型兼容映射。
    
    Args:
        rendertype: 渲染类型（小写）
        
    Returns:
        解析后的 nmsr 渲染类型
    """
    # 先检查是否是 nmsr 原生类型
    if rendertype in config.VALID_RENDERTYPES:
        return rendertype
    # 再检查旧 Starlight 兼容映射
    if rendertype in config.LEGACY_RENDERTYPE_MAP:
        return config.LEGACY_RENDERTYPE_MAP[rendertype]
    return rendertype  # 未知类型，由 validate 处理

def build_render_url(rendertype: str, identifier: str) -> str:
    """
    构建 nmsr 渲染 API 的 URL。
    nmsr 支持用户名或 UUID 作为 identifier。

    Args:
        rendertype: nmsr 渲染类型 (fullbody, bust, head, headiso, face, skin, etc.)
        identifier: 玩家用户名或 UUID

    Returns:
        完整的渲染 URL
    """
    resolved_type = resolve_rendertype(rendertype)
    base = config.NMSR_BASE_URL.rstrip('/')
    return f"{base}/{resolved_type}/{identifier}"

def validate_rendertype(rendertype: str) -> tuple[bool, str | None]:
    """
    验证渲染类型是否有效（支持 nmsr 原生类型和旧 Starlight 兼容类型）
    
    Args:
        rendertype: 要验证的渲染类型（小写）
        
    Returns:
        tuple[is_valid, error_msg]: 有效返回 (True, None)，无效返回 (False, error_msg)
    """
    # 检查 nmsr 原生类型
    if rendertype in config.VALID_RENDERTYPES:
        return True, None
    # 检查旧 Starlight 兼容类型
    if rendertype in config.LEGACY_RENDERTYPE_MAP:
        mapped = config.LEGACY_RENDERTYPE_MAP[rendertype]
        logger.info(f"旧渲染类型 '{rendertype}' 已映射为 nmsr 类型 '{mapped}'")
        return True, None
    
    valid_types = ", ".join(sorted(config.VALID_RENDERTYPES))
    error_msg = (f"未知的渲染类型 '{rendertype}'。\n"
                f"有效类型: {valid_types}\n"
                f"输入 /skinhelp 查看完整列表。")
    return False, error_msg

def validate_wallpaper(wallpaper_id: str) -> tuple[bool, str | None, int]:
    """
    壁纸功能已废弃（nmsr 不支持）
    
    Args:
        wallpaper_id: 壁纸ID
        
    Returns:
        tuple[is_valid, error_msg, max_players]
    """
    return False, "壁纸功能暂不可用：原渲染服务器 Starlight Skins 已宕机，新的渲染服务 nmsr 不支持壁纸功能。", 0


