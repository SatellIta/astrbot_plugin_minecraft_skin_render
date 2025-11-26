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

## 指令1：获取皮肤渲染
`/skin [rendertype] <username>`

### 参数
- `[rendertype]`: 可选。渲染类型，默认为 `default`
- `<username>`: 必需。玩家名称（带空格请使用引号，如 "Steve Jobs"）

### 示例
- `/skin Notch` - 默认全身渲染
- `/skin walking Notch` - 行走动作的全身渲染

---

## 指令2：生成壁纸
`/wallpaper [wallpaper_id] <玩家名1> [玩家名2] [玩家名3]`

### 参数
- `[wallpaper_id]`: 可选。壁纸ID，默认为 `herobrine_hill`
- `<玩家名...>`: 必需。至少1个玩家名称，不同壁纸支持不同数量的玩家

### 可用壁纸及玩家上限
- `herobrine_hill` - 最多1个玩家
- `malevolent` - 最多1个玩家
- `off_to_the_stars` - 最多1个玩家
- `quick_hide` - 最多3个玩家
- `wheat` - 最多1个玩家

### 示例
- `/wallpaper herobrine_hill Notch` - 生成 Herobrine Hill 壁纸
- `/wallpaper quick_hide Notch jeb_ Dream` - 生成 Quick Hide 壁纸（3个玩家）
- `/wallpaper Notch` - 使用默认壁纸生成

---

## 指令3：自定义模型渲染
`/customskin <username> [camera_preset] [focal_preset]`

### 参数
- `<username>`: 必需。玩家名称。
- `[camera_preset]`: 可选。相机位置的预设名称或自定义JSON。
- `[focal_preset]`: 可选。焦点位置的预设名称或自定义JSON。

### 流程
1. 发送指令，例如 `/customskin Notch`。
2. 机器人会提示你发送一个 `.obj` 模型文件。
3. 在15秒内上传你的模型文件。
4. 机器人将使用你的模型和指定玩家的皮肤进行渲染。

### 示例
- `/customskin Notch` - 使用默认相机和焦点。
- `/customskin Notch front` - 使用名为 `front` 的相机预设。
- `/customskin Notch front top` - 同时使用相机和焦点的预设。
- `/customskin Notch '{"x":0,"y":20,"z":-50}'` - 使用自定义的JSON作为相机位置。

---

## 帮助命令
- `/skinhelp` - 查看所有可用的渲染类型和壁纸列表。
- `/customskinhelp` - 查看所有可用的相机和焦点预设及其详细数据。
