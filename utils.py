import aiohttp
import os
import asyncio
from astrbot.api import logger

from . import config

async def get_player_uuid(session: aiohttp.ClientSession, username: str) -> tuple[str | None, str | None]:
    """
    通过 Mojang API 获取玩家 UUID
    
    Args:
        session: aiohttp.ClientSession
        username: 玩家用户名
        
    Returns:
        tuple[uuid, error_msg]: 成功返回 (uuid, None)，失败返回 (None, error_msg)
    """
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

def build_render_url(rendertype: str, uuid: str) -> str:
    """
    构建 Starlight 渲染 API 的 URL
    
    Args:
        rendertype: 渲染类型
        uuid: 玩家 UUID
        
    Returns:
        完整的渲染 URL
    """
    rendercrop = config.SKIN_RENDERCROP if rendertype == "skin" else config.DEFAULT_RENDERCROP
    return config.STARLIGHT_RENDER_URL.format(
        rendertype=rendertype,
        uuid=uuid,
        rendercrop=rendercrop
    )

def validate_rendertype(rendertype: str) -> tuple[bool, str | None]:
    """
    验证渲染类型是否有效
    
    Args:
        rendertype: 要验证的渲染类型（小写）
        
    Returns:
        tuple[is_valid, error_msg]: 有效返回 (True, None)，无效返回 (False, error_msg)
    """
    if rendertype not in config.VALID_RENDERTYPES:
        valid_types_sample = ", ".join(sorted(config.VALID_RENDERTYPES)[:5]) + "..."
        error_msg = (f"未知的渲染类型 '{rendertype}'。\n"
                    f"有效类型例如: {valid_types_sample}\n"
                    f"输入 /skinhelp 查看完整列表。")
        return False, error_msg
    return True, None

def validate_wallpaper(wallpaper_id: str) -> tuple[bool, str | None, int]:
    """
    验证壁纸ID是否有效
    
    Args:
        wallpaper_id: 要验证的壁纸ID（小写）
        
    Returns:
        tuple[is_valid, error_msg, max_players]: 有效返回 (True, None, max_players)，无效返回 (False, error_msg, 0)
    """
    if wallpaper_id not in config.WALLPAPER_CONFIGS:
        available_wallpapers = ", ".join(sorted(config.WALLPAPER_CONFIGS.keys()))
        error_msg = (f"未知的壁纸类型 '{wallpaper_id}'。\n"
                    f"可用壁纸: {available_wallpapers}\n"
                    f"输入 /skinhelp 查看详细信息。")
        return False, error_msg, 0
    return True, None, config.WALLPAPER_CONFIGS[wallpaper_id]


