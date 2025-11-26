import aiohttp
import json
import asyncio, os
import astrbot.api.message_components as Comp
from astrbot.api.message_components import File
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
from astrbot.core.utils.session_waiter import session_waiter, SessionController

from . import actions, config, utils, help, transfer

# 注册插件
@register(
    "MCSkinRender",
    "SatellIta",
    "使用 Starlight API 异步获取 Minecraft 皮肤的多种渲染图和动作",
    "1.1.1",
    "https://github.com/SatellIta/astrbot_plugin_minecraft_skin_render"
)
class MCSkinPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        # 在插件初始化时创建一个可复用的 aiohttp.ClientSession
        self.config = config
        self.session = aiohttp.ClientSession()

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
                rendertype = config.DEFAULT_RENDERTYPE
                logger.warning(f"参数 '{param1}' 不是有效的渲染类型，已忽略第二个参数 '{param2}'，并使用默认渲染类型。")
        else:
            # 只提供了一个参数: /skin <param1>
            # 将 param1 视为用户名，使用默认渲染类型
            username = param1
            rendertype = config.DEFAULT_RENDERTYPE

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
            # 第一个参数不是壁纸ID，视为玩家名，使用默认壁纸
            wallpaper_id = config.DEFAULT_WALLPAPER
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
        使用自定义模型渲染皮肤
        """
        if not username:
            yield event.plain_result("错误：请提供玩家名称。\n用法: /customskin <玩家名称> [相机预设] [焦点预设]")
            return

        # 1. 获取玩家 UUID
        uuid, error_msg = await utils.get_player_uuid(self.session, username)
        if error_msg:
            yield event.plain_result(error_msg)
            return

        # 2. 发送提示
        prompt_msg = (
            f"请在 {config.FILE_WAIT_TIMEOUT} 秒内发送一个 .obj 模型文件 "
            f"来为玩家 {username} 进行渲染。"
        )
        await event.send(event.plain_result(prompt_msg))

        # 2.1 解析用户可选参数
        camera_param_raw = camera_preset
        focal_param_raw = focal_preset

        # 将原始字符串解析为 dict 或从预置中取值（延后到会话处理，以便用户仍可发送文件）

        # 3. 定义并启动会话控制器
        @session_waiter(timeout=config.FILE_WAIT_TIMEOUT, record_history_chains=False)
        async def custom_skin_waiter(controller: SessionController, event: AstrMessageEvent):
            file_component = None
            # 遍历消息组件，查找 File 类型的组件
            for component in event.get_messages():
                if isinstance(component, File):
                    file_component = component
                    break
            
            if not file_component:
            #    await event.send(event.plain_result("请发送文件，而不是文本消息。"))
                return

            local_path = await file_component.get_file()

            try:
                # 根据配置决定使用本地文件服务还是公共中转服务
                if self.config.get("use_file_transfer"):
                    # 使用公共中转服务 (tmpfiles.org)
                    logger.info("use_file_transfer 已开启，使用 tmpfiles.org 上传...")
                    stable_url = await transfer.upload_to_tmpfiles(self.session, local_path)
                else:
                    # 使用内置文件服务
                    logger.info("use_file_transfer 已关闭，使用内置文件服务注册...")
                    stable_url = await file_component.register_to_file_service()

                if not stable_url:
                    await event.send(event.plain_result("错误：文件上传或注册失败，无法获取有效的 URL。"))
                    controller.stop()
                    return

                logger.info(f"文件服务返回的稳定 URL: {stable_url}")

                # 2. 解析并决定最终使用的相机与焦点参数（优先使用用户输入，支持预置名或 JSON）
                def resolve_position_param(raw_value, presets, default):
                    if not raw_value:
                        return default
                    raw_lower = raw_value.lower()
                    # 如果用户提供了一个预置名
                    if raw_lower in presets:
                        return presets[raw_lower]
                    # 否则尝试解析 JSON
                    try:
                        parsed = json.loads(raw_value)
                        if isinstance(parsed, dict):
                            return parsed
                    except Exception:
                        pass
                    # 无法解析则返回默认并告知用户（但不抛错）
                    return default

                camera_position = resolve_position_param(camera_param_raw, config.CAMERA_PRESETS, config.DEFAULT_CAMERA_POSITION)
                camera_focal = resolve_position_param(focal_param_raw, config.FOCAL_PRESETS, config.DEFAULT_CAMERA_FOCAL_POINT)

                # 3. 将 URL 和额外参数传递给 action 构建最终的渲染URL
                result_chain = await actions.upload_and_render_custom_skin(
                    self.session,
                    uuid,
                    stable_url,
                    username,
                    camera_position=camera_position,
                    camera_focal_point=camera_focal,
                )

                # 3. 发送结果
                await event.send(event.chain_result(result_chain))
                
                controller.stop() # 成功处理，结束会话

            except Exception as e:
                logger.error(f"文件服务注册或处理时失败: {e}", exc_info=True)
                await event.send(event.plain_result("错误：文件处理失败。请检查机器人配置文件中的 `callback_api_base` 是否正确设置。"))
                controller.stop()

            finally:
                if local_path and os.path.exists(local_path):
                    # 定义一个后台清理函数
                    async def delayed_cleanup(path, delay=20):
                        await asyncio.sleep(delay) # 等待 20 秒，足够api获取图片并下载了
                        try:
                            if os.path.exists(path):
                                os.remove(path)
                                logger.info(f"延迟清理完成: {path}")
                            else:
                                logger.warning(f"文件已不存在，跳过清理：{path}")
                        except Exception as e:
                            logger.error(f"延迟清理文件{path}时失败：{e}")

                    logger.info(f"为{local_path}创建了延迟清理任务")
                    asyncio.create_task(delayed_cleanup(local_path))

        try:
            await custom_skin_waiter(event)
        except TimeoutError:
            yield event.plain_result("操作超时，已取消渲染。")
        except Exception as e:
            logger.error(f"customskin 会话期间发生未知错误: {e}", exc_info=True)
            yield event.plain_result(f"处理过程中发生内部错误: {e}")
        finally:
            event.stop_event()

    async def terminate(self):
        """插件卸载/停止时，异步关闭 session"""
        await self.session.close()
        logger.info("MCSkinPlugin: aiohttp session 已成功关闭")