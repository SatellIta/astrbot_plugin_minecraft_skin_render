# AstrBot Minecraft 皮肤插件 (MCSkinRenderer)
用于获取 Minecraft 玩家皮肤的 3D 渲染图、2D 头像或原始皮肤贴图。

> [!IMPORTANT]
> **渲染服务已迁移**：原 Starlight Skins 渲染服务已宕机，其 API 已废弃。本插件现已迁移至
> [nmsr (NickAc's Minecraft Skin Renderer)](https://nmsr.nickac.dev)。
>
> 迁移带来的功能变化：
> - ✅ `/skin`、`/randomskin` 正常可用
> - ❌ 壁纸功能 `/wallpaper` 不可用（nmsr 不支持壁纸渲染）
> - ❌ 自定义模型渲染 `/customskin` 不可用（nmsr 不支持上传自定义 `.obj` 模型）
>
> 对应的旧指令仍然保留，但会直接返回“功能暂不可用”的提示。

# 🔧 安装
方法一：使用插件市场 (推荐)

搜索 MC皮肤渲染插件 并安装

方法二：Git Clone

进入 AstrBot 的 data/plugins/ 目录，然后执行：

```bash
git clone https://github.com/SatellIta/astrbot_plugin_minecraft_skin_render
```

安装依赖

进入 plugins/astrbot_plugin_minecraft_skin_render/ 目录，然后执行

```bash
pip install -r requirements.txt
```

如果不想手动安装依赖，插件的依赖会在机器人下次重启时自动安装。

# ⚙️ 配置

在 AstrBot 插件配置面板中可以设置：

- `render_server_url`：渲染服务器基础 URL，默认为 `https://nmsr.nickac.dev`。
  如果你自行部署了 nmsr-rs，可改为 `http://localhost:8080` 或你的服务器地址（不要带末尾斜杠）。
- `use_file_transfer`：已废弃。原用于 `customskin` 的模型文件中转，现仅为兼容旧配置保留。

# 🚀 使用说明

## 指令1：获取皮肤渲染
`/skin [rendertype] <username>`

### 参数
- `[rendertype]`: 可选。渲染类型，默认为 `fullbody`
- `<username>`: 必需。玩家名称或者 UUID（带连字符或不带均可）

### 可用渲染类型

| 渲染类型 | 说明 |
| --- | --- |
| `fullbody` | 全身 3D 等距视图（默认） |
| `fullbodyiso` | 全身真正等距投影 |
| `bust` | 半身视图（头 + 躯干 + 手臂） |
| `frontfull` | 正面 2D 全身 |
| `frontbust` | 正面等距半身 |
| `head` | 头像 |
| `headiso` | 等距 3D 头像 |
| `face` | 正脸 |
| `skin` | 原始皮肤贴图（无渲染） |

### 旧版渲染类型兼容
旧版 Starlight 的渲染类型仍然接受，并会自动映射到最接近的 nmsr 类型，例如：

- `default`、`walking`、`sleeping` 等动作类 → `fullbody`
- `isometric` → `fullbodyiso`
- `skin` → `skin`（nmsr 原生类型）

> 注意：nmsr 不支持姿势/动作，动作类类型会输出静态全身图。`head`、`bust` 等名称与 nmsr 原生类型重名，会直接使用 nmsr 的原生渲染。

### 示例
- `/skin Notch` - 默认全身渲染
- `/skin head Notch` - 头像
- `/skin walking Notch` - 行走动作（实际输出 `fullbody` 静态全身图）
- `/skin 069a79f4-44e9-4726-a5be-fca90e38aaf5` - 使用 UUID 查询

---

## 指令2：随机皮肤预览
`/randomskin`

功能：从 NameMC 的随机皮肤页面抓取一个随机皮肤，解析出该皮肤关联的第一个玩家名称，然后使用该名称获取玩家 UUID 并生成默认的皮肤渲染预览。

> 该功能依赖 NameMC 网站。NameMC 使用 Cloudflare 防护，如果返回 `HTTP 403`，
> 通常是请求被 Cloudflare 拦截。插件已使用 `safari17_0` 浏览器指纹访问，
> 请确保 `curl_cffi >= 0.6.0`；若仍被拦截，可能是当前服务器的 IP 被 NameMC 限制。

---

## 指令3：生成壁纸（已弃用）
`/wallpaper [wallpaper_id] <玩家名1> [玩家名2] [玩家名3]`

**该功能已不可用。** 原壁纸渲染由 Starlight Skins 提供，该服务已宕机；新的渲染服务 nmsr 不支持壁纸功能。执行该指令会返回功能不可用的提示。

---

## 指令4：自定义模型渲染（已弃用）
`/customskin <username> [camera_preset] [focal_preset]`

**该功能已不可用。** 原功能允许上传 `.obj` 模型并使用指定玩家的皮肤渲染，但新的渲染服务 nmsr 不支持自定义模型上传。执行该指令会返回功能不可用的提示。

---

## 帮助命令
- `/skinhelp` - 查看所有可用的渲染类型和指令说明。
- `/customskinhelp` - 查看 `/customskin` 的说明（当前返回功能已弃用的提示）。

# 🖥️ 自行部署渲染服务

如果需要更稳定的渲染服务，可以自行部署 [nmsr-rs](https://github.com/NickAcPT/nmsr-rs)：

```bash
git clone https://github.com/NickAcPT/nmsr-rs
cd nmsr-rs
cp example.config.toml config.toml
docker build -t nmsr .
docker run -p 8080:8080 nmsr
```

然后在插件配置中将 `render_server_url` 设为 `http://localhost:8080`（或你的服务器地址）。

> 注意：即使自行部署 nmsr-rs，也仍然不支持自定义 `.obj` 模型上传和壁纸渲染。

# ❓ 常见问题

- **`/skin` 提示找不到玩家**：插件会先通过 Mojang API 查询玩家 UUID，请确认服务器可以访问 `api.mojang.com`，且玩家名称拼写正确。
- **`/randomskin` 提示 HTTP 403**：NameMC 的 Cloudflare 拦截了请求，请升级 `curl_cffi`（`pip install -U "curl_cffi>=0.6.0"`）；若服务器 IP 被限制，可尝试更换出口 IP。
- **渲染图无法显示**：请确认服务器可以访问 `render_server_url`（默认 `https://nmsr.nickac.dev`），或改用自建渲染服务。
