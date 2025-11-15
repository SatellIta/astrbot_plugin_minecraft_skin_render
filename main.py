import aiohttp
import astrbot.api.message_components as Comp
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

# .../render/:RENDERTYPE/:PLAYERNAME OR UUID/:RENDERCROP
VALID_RENDERTYPES = [
    "default", "marching", "walking", "crouching", "crossed", "criss_cross",
    "ultimate", "isometric", "head", "custom", "cheering", "relaxing",
    "trudging", "cowering", "pointing", "lunging", "dungeons", "facepalm",
    "sleeping", "dead", "archer", "kicking", "mojavatar", "reading",
    "high_ground", "clown", "bitzel", "pixel", "ornament", "skin", "profile"
]

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

    @filter.command("skin")
    async def get_skin(
        self, 
        event: AstrMessageEvent, 
        username: str, # 必填参数
        rendertype: str = 'default', # 可选的第一个参数
    ):
        """
        /skin <username> [rendertype]
        获取 Minecraft 皮肤渲染图
        
        参数:
          username: 必需, 玩家名称 (如果名称含空格，请使用引号)
          
          rendertype: 可选, Starlight API 的渲染类型 (默认: default)
            - 例如: default, walking, head, skin, mojavatar (头像), archer ...
            - (输入 /help skin_types 查看所有类型 - 见下个函数)
        """
        
        # 1. 解析参数
        rendertype_lower = rendertype.lower()

        # 2. 验证 rendertype
        if rendertype_lower not in VALID_RENDERTYPES:
            valid_types_str = ", ".join(VALID_RENDERTYPES[:5]) + "..."
            yield event.plain_result(f"未知的渲染类型 '{rendertype_lower}'。\n"
                                     f"有效类型例如: {valid_types_str}\n"
                                     f"输入 /skin_types 查看完整列表。")
            return
        
        try:
            # 3. 异步调用 Mojang API 获取 UUID (逻辑不变)
            mojang_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
            logger.info(f"正在为 {username} (Type: {rendertype_lower}) 异步查询 UUID...")
            
            async with self.session.get(mojang_url) as response:
                if response.status != 200:
                    logger.warning(f"Mojang API 玩家 {username} 未找到 (状态: {response.status})。")
                    yield event.plain_result(f"错误：找不到玩家 '{username}'。")
                    return
                player_data = await response.json()
                uuid = player_data.get("id")
                if not uuid:
                    logger.error(f"Mojang API 响应中未找到 {username} 的 UUID。")
                    yield event.plain_result("获取玩家数据时出错。")
                    return
                logger.info(f"成功获取 {username} 的 UUID: {uuid}")

            # .../render/:RENDERTYPE/:UUID/:RENDERCROP
            rendercrop = "full" # 默认为 full
            if rendertype_lower == "skin":
                rendercrop = "default" # 如果类型是 skin，则改为 default

            render_url = f"https://starlightskins.lunareclipse.studio/render/{rendertype_lower}/{uuid}/{rendercrop}"
            render_desc = f"'{rendertype_lower}' 渲染"

            logger.info(f"为 {username} 生成 URL: {render_url}")
            
            chain = [
                Comp.Plain(f"这是 {username} 的 {render_desc}：\n"),
                Comp.Image.fromURL(url=render_url) # 直接使用 URL
            ]
            yield event.chain_result(chain)

        except aiohttp.ClientError as e:
            logger.error(f"为 {username} 获取皮肤时发生 aiohttp ClientError: {e}")
            yield event.plain_result(f"查询时发生网络错误，请稍后再试。")
        except Exception as e:
            logger.error(f"处理 /skin {username} 时发生未知错误: {e}", exc_info=True)
            yield event.plain_result(f"发生了一个内部错误。")

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
            "  [rendertype]: 可选。渲染类型（默认为 'default'）。\n\n"
            "--- 所有可用的 [rendertype] 列表 ---\n"
        )
        
        # 2. 渲染类型列表
        types_str = ", ".join(VALID_RENDERTYPES)
        
        # 3. 发送合并后的帮助信息
        yield event.plain_result(help_text + types_str)

    async def terminate(self):
        """插件卸载/停止时，异步关闭 session"""
        await self.session.close()
        logger.info("MCSkinPlugin: aiohttp session 已成功关闭")