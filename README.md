# AstrBot Minecraft 皮肤插件 (MCSkinRenderer)
用于获取 Minecraft 玩家皮肤的 3D 渲染图（支持动作）、2D 头像或皮肤文件。

# 🔧 安装
方法一：使用插件市场 (推荐)

搜索 MC皮肤渲染插件 并安装

方法二：Git Clone

进入 AstrBot 的 data/plugins/ 目录，然后执行：

```bash
git clone https://github.com/SatellIta/astrbot_plugin_minecraft_skin_render
```

安装依赖

无论使用哪种方法，插件的依赖都会在机器人下次重启时自动安装。

# 🚀 使用说明
核心命令
`/skin <username> [pose]`

参数
<username>: 必需。玩家名称（带空格请使用引号，如 "Steve Jobs"）。

[pose]：可选。默认动作为default

可用pose列表，请使用 `/skinhelp` 指令查看可用动作

💡 示例
/skin Notch (默认全身渲染)

/skin Notch walking (行走动作的全身渲染 - 快捷方式)
