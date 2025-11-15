# AstrBot Minecraft 皮肤插件 (MCSkinRenderer)
用于获取 Minecraft 玩家皮肤的 3D 渲染图（支持动作）、2D 头像或皮肤文件。

# 🔧 安装
方法一：使用插件市场 (推荐)

搜索

方法二：Git Clone

进入 AstrBot 的 data/plugins/ 目录，然后执行：

```bash
git clone https://github.com/SatellIta/astrbot_plugin_minecraft_skin_render
```

安装依赖

无论使用哪种方法，插件的依赖都会在机器人下次重启时自动安装。

# 🚀 使用说明
核心命令
/skin <username> [type|pose] [pose]

参数
<username>: 必需。玩家名称（带空格请使用引号，如 "Steve Jobs"）。

[type|pose]: 可选。渲染类型或动作快捷方式。

类型: body (默认), head, avatar, skin。

快捷方式: 如果直接输入动作名 (如 walking)，则默认为 body 类型。

[pose]: 可选。仅在 body 或 head 类型时生效。

可用动作 (Poses)
default, walking, marching, crouching, cheering, archer, lunging, sleeping, dead

💡 示例
/skin Notch (默认全身渲染)

/skin Notch walking (行走动作的全身渲染 - 快捷方式)

/skin Notch body archer (射箭动作的全身渲染 - 标准方式)

/skin Notch head crouching (潜行姿势的头部渲染)

/skin Notch avatar (2D头像)