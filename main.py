import aiohttp
import astrbot.api.message_components as Comp
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

# API URLs
MOJANG_API_URL = "https://api.mojang.com/users/profiles/minecraft/{username}"
STARLIGHT_RENDER_URL = "https://starlightskins.lunareclipse.studio/render/{rendertype}/{uuid}/{rendercrop}"

# 有效的渲染类型（使用 set 以提高查找效率）
VALID_RENDERTYPES = {
    "default", "marching", "walking", "crouching", "crossed", "criss_cross",
    "ultimate", "isometric", "head", "custom", "cheering", "relaxing",
    "trudging", "cowering", "pointing", "lunging", "dungeons", "facepalm",
    "sleeping", "dead", "archer", "kicking", "mojavatar", "reading",
    "high_ground", "clown", "bitzel", "pixel", "ornament", "skin", "profile"
}

# 默认渲染配置
DEFAULT_RENDERTYPE = "default"
DEFAULT_RENDERCROP = "full"
SKIN_RENDERCROP = "default"  # skin 类型使用的 rendercrop

# 注册插件
@register(
    "MCSkinRender",
    "SatellIta",
    "使用 Starlight API 异步获取 Minecraft 皮肤的多种渲染图和动作",
    "1.0.0",
    "https://github.com/SatellIta/astrbot_plugin_minecraft_skin_render"
)
class MCSkinPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 在插件初始化时创建一个可复用的 aiohttp.ClientSession
        self.session = aiohttp.ClientSession()

    async def _get_player_uuid(self, username: str) -> tuple[str | None, str | None]:
        """
        通过 Mojang API 获取玩家 UUID
        
        Args:
            username: 玩家用户名
            
        Returns:
            tuple[uuid, error_msg]: 成功返回 (uuid, None)，失败返回 (None, error_msg)
        """
        mojang_url = MOJANG_API_URL.format(username=username)
        logger.info(f"正在为 {username} 异步查询 UUID...")
        
        try:
            async with self.session.get(mojang_url) as response:
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

    def _build_render_url(self, rendertype: str, uuid: str) -> str:
        """
        构建 Starlight 渲染 API 的 URL
        
        Args:
            rendertype: 渲染类型
            uuid: 玩家 UUID
            
        Returns:
            完整的渲染 URL
        """
        rendercrop = SKIN_RENDERCROP if rendertype == "skin" else DEFAULT_RENDERCROP
        return STARLIGHT_RENDER_URL.format(
            rendertype=rendertype,
            uuid=uuid,
            rendercrop=rendercrop
        )

    def _validate_rendertype(self, rendertype: str) -> tuple[bool, str | None]:
        """
        验证渲染类型是否有效
        
        Args:
            rendertype: 要验证的渲染类型（小写）
            
        Returns:
            tuple[is_valid, error_msg]: 有效返回 (True, None)，无效返回 (False, error_msg)
        """
        if rendertype not in VALID_RENDERTYPES:
            valid_types_sample = ", ".join(sorted(VALID_RENDERTYPES)[:5]) + "..."
            error_msg = (f"未知的渲染类型 '{rendertype}'。\n"
                        f"有效类型例如: {valid_types_sample}\n"
                        f"输入 /skinhelp 查看完整列表。")
            return False, error_msg
        return True, None

    @filter.command("skin")
    async def get_skin(
        self, 
        event: AstrMessageEvent, 
        username: str, # 必填参数
        rendertype: str = DEFAULT_RENDERTYPE, # 可选的第一个参数
    ):
        """
        获取 Minecraft 玩家皮肤的渲染图
        
        Args:
            event: 消息事件
            username: 玩家用户名
            rendertype: 渲染类型，默认为 'default'
        """
        # 1. 验证渲染类型
        rendertype_lower = rendertype.lower()
        is_valid, error_msg = self._validate_rendertype(rendertype_lower)
        if not is_valid:
            yield event.plain_result(error_msg)
            return
        
        # 2. 获取玩家 UUID
        uuid, error_msg = await self._get_player_uuid(username)
        if error_msg:
            yield event.plain_result(error_msg)
            return
        
        # 3. 构建渲染 URL
        render_url = self._build_render_url(rendertype_lower, uuid)
        logger.info(f"为 {username} 生成渲染 URL: {render_url}")
        
        # 4. 发送结果
        render_desc = f"'{rendertype_lower}' 渲染"
        chain = [
            Comp.Plain(f"这是 {username} 的 {render_desc}：\n"),
            Comp.Image.fromURL(url=render_url)
        ]
        yield event.chain_result(chain)

    # /skinhelp 指令，合并了用法和类型列表
    @filter.command("skinhelp")
    async def skin_help(self, event: AstrMessageEvent):
        """
        /skinhelp
        显示 /skin 指令的详细帮助和所有可用的渲染类型
        """
        
        # 1. 帮助文本
        help_text = (
            "--- Minecraft 皮肤渲染插件帮助 ---\n"
            "指令用法：\n"
            "/skin <username> [rendertype]\n\n"
            "参数说明：\n"
            "  <username>: 必需。玩家名称（如果名称含空格，请使用引号，例如 \"Steve Jobs\"）。\n"
            f"  [rendertype]: 可选。渲染类型（默认为 '{DEFAULT_RENDERTYPE}'）。\n\n"
            "--- 所有可用的 [rendertype] 列表 ---\n"
        )
        
        # 2. 渲染类型列表（按字母顺序排序）
        types_str = ", ".join(sorted(VALID_RENDERTYPES))
        
        # 3. 发送合并后的帮助信息
        yield event.plain_result(help_text + types_str)

    async def terminate(self):
        """插件卸载/停止时，异步关闭 session"""
        await self.session.close()
        logger.info("MCSkinPlugin: aiohttp session 已成功关闭")