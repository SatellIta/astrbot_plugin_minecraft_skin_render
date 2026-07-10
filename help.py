from . import config

def get_help_text() -> str:
    """
    生成插件的帮助信息文本
    """
    # /skin 指令帮助
    help_text = (
        "--- Minecraft 皮肤渲染插件帮助 ---\n"
        "渲染服务: nmsr.nickac.dev (NickAc's Minecraft Skin Renderer)\n\n"
        "【指令1】/skin <param1> [param2]\n"
        "用法1: /skin <玩家名称>\n"
        "  » 示例: /skin Notch\n"
        f"  <玩家名称>: 必需。玩家的 Minecraft ID 或者 UUID。\n\n"
        "用法2 (推荐): /skin <渲染类型> <玩家名称>\n"
        "  » 示例: /skin head Notch\n"
        f"  <渲染类型>: 可选。默认为 '{config.DEFAULT_RENDERTYPE}'。\n\n"
        "--- 所有可用的 [rendertype] 列表 ---\n"
    )
    
    # 渲染类型列表（按字母顺序排序，带中文描述）
    types_lines = []
    for name in sorted(config.VALID_RENDERTYPES):
        desc = config.NMSR_RENDERTYPE_INFO.get(name, "")
        if desc:
            types_lines.append(f"  • {name} — {desc}")
        else:
            types_lines.append(f"  • {name}")
    types_str = "\n".join(types_lines)
    
    # /randomskin 指令帮助
    randomskin_help = (
        "\n\n【指令2】/randomskin\n"
        "  功能: 从 NameMC 随机获取一个皮肤并提取对应玩家名称，随后生成该玩家的全身渲染预览。\n"
    )

    # /wallpaper 指令帮助
    wallpaper_help = (
        "\n\n【指令3】/wallpaper [param1] [param2] ...\n"
        "  [已废弃] 壁纸功能暂不可用。\n"
        "  原因：原渲染服务器 Starlight Skins 已宕机，nmsr 不支持壁纸功能。\n"
    )
    
    # /customskin 指令帮助
    customskin_help = (
        "\n【指令4】/customskin <玩家名称> [相机预设] [焦点预设]\n"
        "  [已废弃] 自定义模型渲染功能暂不可用。\n"
        "  原因：原渲染服务器 Starlight Skins 已宕机，nmsr 不支持自定义模型上传。\n"
        "  如需此功能，可自行部署 nmsr-rs: https://github.com/NickAcPT/nmsr-rs\n"
    )
    
    # 返回合并后的帮助信息
    return help_text + types_str + randomskin_help + wallpaper_help + customskin_help

def get_customskin_help_text() -> str:
    """
    生成 /customskin 指令的详细帮助。
    [已废弃] 自定义渲染功能
    """
    return (
        "--- /customskin 详细帮助 ---\n\n"
        "自定义模型渲染功能暂不可用。\n"
        "原因：原渲染服务器 Starlight Skins 已宕机，新的渲染服务 nmsr 不支持自定义模型上传。\n\n"
        "如需此功能，可以自行部署 nmsr-rs: https://github.com/NickAcPT/nmsr-rs\n"
        "部署后修改 config.py 中的 NMSR_BASE_URL 为自己的服务地址即可。"
    )
