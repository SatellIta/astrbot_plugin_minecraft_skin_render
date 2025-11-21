import aiohttp
import astrbot.api.message_components as Comp
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

# API URLs
MOJANG_API_URL = "https://api.mojang.com/users/profiles/minecraft/{username}"
STARLIGHT_RENDER_URL = "https://starlightskins.lunareclipse.studio/render/{rendertype}/{uuid}/{rendercrop}"
WALLPAPER_API_URL = "https://starlightskins.lunareclipse.studio/render/wallpaper/{wallpaper_id}/{playernames}"

# 有效的渲染类型（使用 set 以提高查找效率）
VALID_RENDERTYPES = {
    "default", "marching", "walking", "crouching", "crossed", "criss_cross",
    "ultimate", "isometric", "head", "custom", "cheering", "relaxing",
    "trudging", "cowering", "pointing", "lunging", "dungeons", "facepalm",
    "sleeping", "dead", "archer", "kicking", "mojavatar", "reading",
    "high_ground", "clown", "bitzel", "pixel", "ornament", "skin", "profile"
}

# 壁纸配置（壁纸ID -> 支持的最大玩家数）
WALLPAPER_CONFIGS = {
    "herobrine_hill": 1,
    "quick_hide": 3,
    "malevolent": 1,
    "off_to_the_stars": 1,
    "wheat": 1
}

# 默认渲染配置
DEFAULT_RENDERTYPE = "default"
DEFAULT_RENDERCROP = "full"
SKIN_RENDERCROP = "default"  # skin 类型使用的 rendercrop
DEFAULT_WALLPAPER = "herobrine_hill"  # 默认壁纸

# 注册插件
@register(
    "MCSkinRender",
    "SatellIta",
    "使用 Starlight API 异步获取 Minecraft 皮肤的多种渲染图和动作",
    "1.0.2",
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

    def _validate_wallpaper(self, wallpaper_id: str) -> tuple[bool, str | None, int]:
        """
        验证壁纸ID是否有效
        
        Args:
            wallpaper_id: 要验证的壁纸ID（小写）
            
        Returns:
            tuple[is_valid, error_msg, max_players]: 有效返回 (True, None, max_players)，无效返回 (False, error_msg, 0)
        """
        if wallpaper_id not in WALLPAPER_CONFIGS:
            available_wallpapers = ", ".join(sorted(WALLPAPER_CONFIGS.keys()))
            error_msg = (f"未知的壁纸类型 '{wallpaper_id}'。\n"
                        f"可用壁纸: {available_wallpapers}\n"
                        f"输入 /skinhelp 查看详细信息。")
            return False, error_msg, 0
        return True, None, WALLPAPER_CONFIGS[wallpaper_id]

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
            is_valid_type, _ = self._validate_rendertype(param1.lower())
            if is_valid_type:
                # 用法: /skin <rendertype> <username>
                rendertype = param1
                username = param2
            else:
                # 用法: /skin <username> [ignored_param]
                # 将 param1 视为用户名，忽略 param2
                username = param1
                rendertype = DEFAULT_RENDERTYPE
                logger.warning(f"参数 '{param1}' 不是有效的渲染类型，已忽略第二个参数 '{param2}'，并使用默认渲染类型。")
        else:
            # 只提供了一个参数: /skin <param1>
            # 将 param1 视为用户名，使用默认渲染类型
            username = param1
            rendertype = DEFAULT_RENDERTYPE

        # --- 后续逻辑与之前相同 ---

        # 1. 验证最终确定的渲染类型
        rendertype_lower = rendertype.lower()
        is_valid, error_msg = self._validate_rendertype(rendertype_lower)
        if not is_valid:
            # 理论上，只有当默认类型被错误配置时才会触发
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
        is_valid_wallpaper, _, _ = self._validate_wallpaper(param1.lower())

        if is_valid_wallpaper:
            # 第一个参数是壁纸ID
            wallpaper_id = param1
            usernames = [p for p in [param2, param3, param4] if p]
        else:
            # 第一个参数不是壁纸ID，视为玩家名，使用默认壁纸
            wallpaper_id = DEFAULT_WALLPAPER
            usernames = [p for p in [param1, param2, param3, param4] if p]

        # --- 后续逻辑 ---

        # 1. 验证最终确定的壁纸ID
        wallpaper_lower = wallpaper_id.lower()
        is_valid, error_msg, max_players = self._validate_wallpaper(wallpaper_lower)
        if not is_valid:
            # 理论上只有默认壁纸配置错误时才会触发
            yield event.plain_result(error_msg)
            return

        # 2. 检查玩家参数
        if not usernames:
            yield event.plain_result(
                f"错误：壁纸 '{wallpaper_lower}' 至少需要1个玩家名称。\n"
                f"用法：/wallpaper {wallpaper_lower} <玩家名1> [玩家名2] ...\n"
                f"该壁纸最多支持 {max_players} 个玩家。"
            )
            return

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
            uuid, error_msg_uuid = await self._get_player_uuid(username)
            if error_msg_uuid:
                failed_players.append(username)
                logger.warning(f"无法获取玩家 {username} 的 UUID，跳过该玩家")
            else:
                player_uuids.append(uuid)

        # 5. 检查是否有成功获取的UUID
        if not player_uuids:
            error_list = "\n".join([f"• {player}" for player in failed_players])
            yield event.plain_result(
                f"错误：无法获取任何玩家的 UUID。\n"
                f"失败的玩家：\n{error_list}"
            )
            return

        # 6. 如果有部分玩家失败，添加警告信息
        if failed_players:
            failed_list = ", ".join(failed_players)
            warning_msg += f"⚠️ 以下玩家未找到，已跳过：{failed_list}\n\n"

        # 7. 构建壁纸URL
        player_uuids_path = ",".join(player_uuids)
        wallpaper_url = WALLPAPER_API_URL.format(
            wallpaper_id=wallpaper_lower,
            playernames=player_uuids_path
        )

        logger.info(f"为壁纸 '{wallpaper_lower}' 生成 URL（{len(player_uuids)} 个玩家）: {wallpaper_url}")

        # 8. 发送结果
        success_players = [name for name in actual_usernames if name not in failed_players]
        players_desc = ", ".join(success_players)
        chain = [
            Comp.Plain(f"{warning_msg}这是壁纸 '{wallpaper_lower}' (玩家: {players_desc})：\n"),
            Comp.Image.fromURL(url=wallpaper_url)
        ]
        yield event.chain_result(chain)

    # /skinhelp 指令，合并了用法和类型列表
    @filter.command("skinhelp")
    async def skin_help(self, event: AstrMessageEvent):
        """
        /skinhelp
        显示 /skin 指令的详细帮助和所有可用的渲染类型
        """
        
        # 1. /skin 指令帮助
        help_text = (
            "--- Minecraft 皮肤渲染插件帮助 ---\n\n"
            "【指令1】/skin <param1> [param2]\n"
            "用法1 (推荐): /skin <渲染类型> <玩家名称>\n"
            "  » 示例: /skin walking Notch\n\n"
            f"  <渲染类型>: 可选。默认为 '{DEFAULT_RENDERTYPE}'。\n\n"
            "--- 所有可用的 [rendertype] 列表 ---\n"
            "用法2: /skin <玩家名称>\n"
            "  » 示例: /skin Notch\n"
            f"  <玩家名称>: 必需。玩家的 Minecraft ID。\n"
        )
        
        # 2. 渲染类型列表（按字母顺序排序）
        types_str = ", ".join(sorted(VALID_RENDERTYPES))
        
        # 3. /wallpaper 指令帮助
        wallpaper_help = (
            "\n\n【指令2】/wallpaper [param1] [param2] ...\n"
            "用法1 (推荐): /wallpaper <壁纸ID> <玩家1> [玩家2] ...\n"
            "  » 示例: /wallpaper quick_hide Notch\n\n"
            "用法2: /wallpaper <玩家1> [玩家2] ...\n"
            "  » 示例: /wallpaper Notch Steve\n"
            f"  <壁纸ID>: 可选。默认为 '{DEFAULT_WALLPAPER}'。\n"
            "  <玩家...>: 必需。至少1个玩家名称。\n\n"
            "--- 可用的壁纸ID及玩家上限 ---\n"
        )
        
        # 4. 壁纸列表（按字母顺序排序，带上限说明）
        wallpaper_list = []
        for wp_id, max_p in sorted(WALLPAPER_CONFIGS.items()):
            wallpaper_list.append(f"  • {wp_id} (最多 {max_p} 个玩家)")
        wallpapers_str = "\n".join(wallpaper_list)
        
        # 5. 发送合并后的帮助信息
        full_help = help_text + types_str + wallpaper_help + wallpapers_str
        yield event.plain_result(full_help)

    async def terminate(self):
        """插件卸载/停止时，异步关闭 session"""
        await self.session.close()
        logger.info("MCSkinPlugin: aiohttp session 已成功关闭")