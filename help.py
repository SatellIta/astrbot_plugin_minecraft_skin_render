import json
from . import config

def get_help_text() -> str:
    """
    生成插件的帮助信息文本
    """
    # 1. /skin 指令帮助
    help_text = (
        "--- Minecraft 皮肤渲染插件帮助 ---\n\n"
        "【指令1】/skin <param1> [param2]\n"
        "用法1 (推荐): /skin <渲染类型> <玩家名称>\n"
        "  » 示例: /skin walking Notch\n\n"
        f"  <渲染类型>: 可选。默认为 '{config.DEFAULT_RENDERTYPE}'。\n\n"
        "--- 所有可用的 [rendertype] 列表 ---\n"
        "用法2: /skin <玩家名称>\n"
        "  » 示例: /skin Notch\n"
        f"  <玩家名称>: 必需。玩家的 Minecraft ID。\n"
    )
    
    # 2. 渲染类型列表（按字母顺序排序）
    types_str = ", ".join(sorted(config.VALID_RENDERTYPES))
    
    # 3. /wallpaper 指令帮助
    wallpaper_help = (
        "\n\n【指令2】/wallpaper [param1] [param2] ...\n"
        "用法1 (推荐): /wallpaper <壁纸ID> <玩家1> [玩家2] ...\n"
        "  » 示例: /wallpaper quick_hide Notch\n\n"
        "用法2: /wallpaper <玩家1> [玩家2] ...\n"
        "  » 示例: /wallpaper Notch Steve\n"
        f"  <壁纸ID>: 可选。默认为 '{config.DEFAULT_WALLPAPER}'。\n"
        "  <玩家...>: 必需。至少1个玩家名称。\n\n"
        "--- 可用的壁纸ID及玩家上限 ---\n"
    )
    
    # 4. 壁纸列表（按字母顺序排序，带上限说明）
    wallpaper_list = []
    for wp_id, max_p in sorted(config.WALLPAPER_CONFIGS.items()):
        wallpaper_list.append(f"  • {wp_id} (最多 {max_p} 个玩家)")
    wallpapers_str = "\n".join(wallpaper_list)
    
    # 5. /customskin 指令帮助
    customskin_help = (
        "\n\n【指令3】/customskin <玩家名称> [相机预设] [焦点预设]\n"
        "  » 示例1: /customskin Notch front front\n"
        "  » 示例2: /customskin Notch {\"x\":\"11.92\",\"y\":\"15.81\",\"z\":\"-29.71\"} {\"x\":\"0.31\",\"y\":\"18.09\",\"z\":\"1.32\"}\n"
        "  功能: 使用你提供的 .obj 模型文件来渲染指定玩家的皮肤。\n"
        "  流程: 发送指令后，按提示在15秒内上传模型文件即可。\n"
        "  参数: [相机预设] 和 [焦点预设] 是可选的，可以使用预设名称或自定义JSON。\n"
        "  详情: 发送 /customskinhelp 查看所有可用预设。"
    )
    
    # 6. 返回合并后的帮助信息
    return help_text + types_str + wallpaper_help + wallpapers_str + customskin_help

def get_customskin_help_text() -> str:
    """
    生成 /customskin 指令的详细帮助，包含所有预设列表。
    """
    help_text = "--- /customskin 详细帮助 ---\n\n"
    help_text += "指令用法: /customskin <玩家名称> [相机预设] [焦点预设]\n"
    help_text += "参数可以是预设名称 (如下所列)，也可以是自定义的JSON字符串。\n\n"

    # 1. 相机预设
    help_text += "【可用的相机预设】\n"
    camera_list = []
    for name, data in sorted(config.CAMERA_PRESETS.items()):
        # 使用 json.dumps 保证格式一致且美观
        data_str = json.dumps(data)
        camera_list.append(f"  • {name}: {data_str}")
    help_text += "\n".join(camera_list)

    # 2. 焦点预设
    help_text += "\n\n【可用的焦点预设】\n"
    focal_list = []
    for name, data in sorted(config.FOCAL_PRESETS.items()):
        data_str = json.dumps(data)
        focal_list.append(f"  • {name}: {data_str}")
    help_text += "\n".join(focal_list)
    
    return help_text
