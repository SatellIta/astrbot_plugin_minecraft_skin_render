import aiohttp
import astrbot.api.message_components as Comp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig

from . import actions, utils, help
from . import config as plugin_config

# 注册插件
@register(
    "MCSkinRender",
    "SatellIta",
    "使用 nmsr API 异步获取 Minecraft 玩家皮肤的多种渲染图",
    "1.2.0",
    "https://github.com/SatellIta/astrbot_plugin_minecraft_skin_render"
)
class MCSkinPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.session = aiohttp.ClientSession()

        # 从插件配置注入渲染服务器地址
        server_url = self.config.get("render_server_url", "").strip()
        if server_url:
            plugin_config.NMSR_BASE_URL = server_url
            logger.info(f"MCSkinPlugin: 渲染服务器地址已设置为 {server_url}")

    @filter.command("skin")
    async def get_skin(
        self,
        event: AstrMessageEvent,
        param1: str = None,
        param2: str = None
    ):
        """
        获取 Minecraft 玩家皮肤的渲染图。
        支持两种用法:
        1. /skin <username>
        2. /skin <rendertype> <username>
        """
        # 如果没有提供任何参数，显示错误
        if not param1:
            yield event.plain_result(
                "错误：请提供玩家名称。\n"
                "用法1: /skin <玩家名称>\n"
                "用法2: /skin <渲染类型> <玩家名称>"
            )
            return

        username: str
        rendertype: str

        # 检查提供了多少参数
        if param2:
            # 提供了两个参数: /skin <param1> <param2>
            # 检查 param1 是否为有效的渲染类型
            is_valid_type, _ = utils.validate_rendertype(param1.lower())
            if is_valid_type:
                # 用法: /skin <rendertype> <username>
                rendertype = param1
                username = param2
            else:
                # 用法: /skin <username> [ignored_param]
                # 将 param1 视为用户名，忽略 param2
                username = param1
                rendertype = plugin_config.DEFAULT_RENDERTYPE
                logger.warning(f"参数 '{param1}' 不是有效的渲染类型，已忽略第二个参数 '{param2}'，并使用默认渲染类型。")
        else:
            # 只提供了一个参数: /skin <param1>
            # 将 param1 视为用户名，使用默认渲染类型
            username = param1
            rendertype = plugin_config.DEFAULT_RENDERTYPE

        # 调用核心逻辑
        result = await actions.process_skin_command(self.session, username, rendertype)

        # 根据结果类型发送消息
        if isinstance(result, str):
            yield event.plain_result(result)
        else:
            yield event.chain_result(result)

    @filter.command("wallpaper")
    async def get_wallpaper(
        self,
        event: AstrMessageEvent,
        param1: str = None,
        param2: str = None,
        param3: str = None,
        param4: str = None
    ):
        """
        获取 Minecraft 壁纸。
        支持智能参数解析。
        """
        # 如果没有提供任何参数，显示错误
        if not param1:
            yield event.plain_result(
                "错误：请提供玩家名称或壁纸ID。\n"
                f"用法1: /wallpaper <玩家名称1> [玩家名称2] ...\n"
                f"用法2: /wallpaper <壁纸ID> <玩家名称1> [玩家名称2] ..."
            )
            return

        wallpaper_id: str
        usernames: list[str]

        # 检查 param1 是否为有效的壁纸ID
        is_valid_wallpaper, _, _ = utils.validate_wallpaper(param1.lower())

        if is_valid_wallpaper:
            # 第一个参数是壁纸ID
            wallpaper_id = param1
            usernames = [p for p in [param2, param3, param4] if p]
        else:
            # 第一个参数不是壁纸ID，视为玩家名
            wallpaper_id = ""
            usernames = [p for p in [param1, param2, param3, param4] if p]

        # 调用核心逻辑
        result = await actions.process_wallpaper_command(self.session, wallpaper_id, usernames)

        # 根据结果类型发送消息
        if isinstance(result, str):
            yield event.plain_result(result)
        else:
            yield event.chain_result(result)

    @filter.command("skinhelp")
    async def skin_help(self, event: AstrMessageEvent):
        """
        /skinhelp
        显示 /skin 指令的详细帮助和所有可用的渲染类型
        """
        full_help = help.get_help_text()
        yield event.plain_result(full_help)

    @filter.command("customskinhelp")
    async def custom_skin_help(self, event: AstrMessageEvent):
        """
        /customskinhelp
        显示 /customskin 指令的详细帮助和所有可用的预设
        """
        full_help = help.get_customskin_help_text()
        yield event.plain_result(full_help)

    @filter.command("customskin")
    async def custom_skin(self, event: AstrMessageEvent, username: str = None, camera_preset: str = None, focal_preset: str = None):
        """
        /customskin <玩家名称> [相机预设] [焦点预设]
        [已废弃] 原 Starlight Skins 渲染服务器已宕机，nmsr 不支持自定义模型上传。
        """
        yield event.plain_result(
            "自定义模型渲染功能暂不可用。\n"
            "原因：原渲染服务器 Starlight Skins 已宕机，新的渲染服务 nmsr 不支持自定义模型上传。\n"
            "如需此功能，可以自行部署 nmsr-rs (https://github.com/NickAcPT/nmsr-rs) 并修改配置。"
        )

    async def terminate(self):
        """插件卸载/停止时，异步关闭 session"""
        await self.session.close()
        logger.info("MCSkinPlugin: aiohttp session 已成功关闭")

    @filter.command("randomskin")
    async def random_skin(self, event: AstrMessageEvent):
        """
        /randomskin
        从 NameMC 获取一个随机皮肤，提取玩家名称并渲染默认皮肤预览。
        """
        result = await actions.process_randomskin_command(self.session)

        if isinstance(result, str):
            yield event.plain_result(result)
        else:
            yield event.chain_result(result)