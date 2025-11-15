import aiohttp
import shlex  # 用于安全地解析命令行参数
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Image, Plain
from astrbot.api import logger

# Starlight API (https://starlightskins.lunareclipse.studio)
# 支持的动作列表
VALID_POSES = [
    "default",  "walking",  "marching", "crouching",
    "cheering", "archer",   "lunging",  "sleeping", "dead"
]

# 定义所有有效的渲染类型
VALID_TYPES = ["body", "head", "avatar", "skin"]

# 注册插件
@register(
    name="MCSkinRendererUnified",
    author="SatellIta",
    description="使用 Starlight API 异步获取 Minecraft 皮肤的多种渲染图和动作",
    version="1.0.0",
    repo_url="https://github.com/SatellIta/astrbot_plugin_minecraft_skin_render"
)
class MCSkinPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 在插件初始化时创建一个可复用的 aiohttp.ClientSession
        self.session = aiohttp.ClientSession()

    @filter.command("skin")
    async def get_skin(self, event: AstrMessageEvent):
        """
        /skin <username> [type|pose] [pose]
        获取 Minecraft 皮肤渲染图
        
        参数:
          username: 必需, 玩家名称 (如果名称含空格，请使用引号)
          
          type: 可选, 渲染类型 (默认: body)
            - body:   全身3D渲染 (支持[pose]参数)
            - head:   头部3D渲染 (支持[pose]参数)
            - avatar: 2D头像 (不支持[pose])
            - skin:   原始皮肤文件 (不支持[pose])
            
          pose: 可选, 仅在 type 为 body 或 head 时生效 (默认: default)
            - 可选动作: default, walking, marching, crouching,
                         cheering, archer, lunging, sleeping, dead
                         
        快捷方式: /skin <username> <pose> 将自动渲染全身动作
        """
        
        # 1. 使用 shlex 解析参数
        command_args = event.message_str.replace('/skin', '').strip()
        try:
            args = shlex.split(command_args)
        except ValueError:
            yield event.plain_result("参数解析失败，请检查引号是否正确闭合。")
            return

        if not args:
            yield event.plain_result("请提供一个玩家名称。\n使用 /help skin 查看帮助。")
            return

        # 2. 解析参数
        username = args[0]
        type_arg = args[1].lower() if len(args) > 1 else "body"
        pose_arg = args[2].lower() if len(args) > 2 else "default"

        # 3. 处理快捷方式 /skin <username> <pose>
        if type_arg in VALID_POSES and pose_arg == "default":
            logger.info(f"检测到快捷方式：将 {type_arg} 视为动作，类型设为 body")
            pose_arg = type_arg  # 将动作名赋给 pose_arg
            type_arg = "body"   # 将类型强制设为 body

        # 4. 验证渲染类型
        if type_arg not in VALID_TYPES:
            valid_types_str = ", ".join(VALID_TYPES)
            yield event.plain_result(f"未知的渲染类型 '{type_arg}'。\n"
                                     f"有效类型为: {valid_types_str}")
            return

        try:
            # 5. 异步调用 Mojang API 获取 UUID (逻辑不变)
            mojang_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
            logger.info(f"正在为 {username} 异步查询 UUID...")
            
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

            # 统一使用 Starlight API
            render_url = ""
            render_desc = ""

            if type_arg in ["body", "head"]:
                # 这两种类型支持动作，验证 pose_arg
                if pose_arg not in VALID_POSES:
                    valid_poses_str = ", ".join(VALID_POSES)
                    yield event.plain_result(f"未知的动作 '{pose_arg}'。\n"
                                             f"有效动作为: {valid_poses_str}")
                    return
                
                # 'body' 对应 'full', 'head' 对应 'head'
                render_part = "full" if type_arg == "body" else "head"
                render_url = f"https://starlightskins.lunareclipse.studio/render/{pose_arg}/{uuid}/{render_part}"
                
                if type_arg == "body":
                    render_desc = f"{pose_arg} 姿势的全身渲染"
                else:
                    render_desc = f"{pose_arg} 姿势的头部渲染"
            
            elif type_arg == "avatar":
                render_url = f"https://starlightskins.lunareclipse.studio/avatar/{uuid}"
                render_desc = "2D头像"
                # 如果用户在 avatar/skin 类型下指定了动作，给予提示
                if len(args) > 2:
                    yield event.plain_result("提示：[pose] 参数仅在 type 为 'body' 或 'head' 时生效。")

            elif type_arg == "skin":
                render_url = f"https://starlightskins.lunareclipse.studio/skin/{uuid}"
                render_desc = "原始皮肤文件"
                if len(args) > 2:
                    yield event.plain_result("提示：[pose] 参数仅在 type 为 'body' 或 'head' 时生效。")
            
            # 6. 回复图片
            logger.info(f"为 {username} 生成 URL: {render_url}")
            yield MessageEventResult(components=[
                Plain(f"这是 {username} 的 {render_desc}：\n"),
                Image.fromURL(url=render_url)
            ])

        except aiohttp.ClientError as e:
            logger.error(f"为 {username} 获取皮肤时发生 aiohttp 错误: {e}")
            yield event.plain_result(f"查询时发生网络错误，请稍后再试。")
        except Exception as e:
            logger.error(f"处理 /skin {username} 时发生未知错误: {e}", exc_info=True)
            yield event.plain_result(f"发生了一个内部错误。")

    async def terminate(self):
        """插件卸载/停止时，异步关闭 session"""
        await self.session.close()
        logger.info("MCSkinPlugin: aiohttp session 已成功关闭")