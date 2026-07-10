# API URLs
MOJANG_API_URL = "https://api.mojang.com/users/profiles/minecraft/{username}"
MOJANG_API_UUID_URL = "https://api.minecraftservices.com/minecraft/profile/lookup/{uuid}"

# nmsr (NickAc's Minecraft Skin Renderer) - 替代已宕机的 Starlight Skins
# 可通过 AstrBot 配置面板中的 render_server_url 修改此地址
NMSR_BASE_URL = "https://nmsr.nickac.dev"

# 旧的 Starlight 相关配置（已废弃，保留供参考）
# WALLPAPER_API_URL / CUSTOM_RENDER_API_ENDPOINT 不再可用

# NAMEMC
NAMEMC_RAMDOM = "https://namemc.com/minecraft-skins/random"
NAMEMC_SKIN = "https://namemc.com/skin/{skinid}"

# 有效的渲染类型（nmsr 支持的类型及其描述）
NMSR_RENDERTYPE_INFO = {
    "fullbody":     "全身 3D 等距视图",
    "fullbodyiso":  "全身真正等距投影",
    "bust":         "半身视图（头+躯干+手臂）",
    "frontfull":    "正面 2D 全身",
    "frontbust":    "正面等距半身",
    "head":         "头像",
    "headiso":      "等距 3D 头像",
    "face":         "正脸",
    "skin":         "原始皮肤贴图（无渲染）",
}
VALID_RENDERTYPES = set(NMSR_RENDERTYPE_INFO.keys())

# 旧 Starlight 渲染类型到 nmsr 的兼容映射
# 保留以兼容老用户的命令，映射到最接近的 nmsr 类型
LEGACY_RENDERTYPE_MAP = {
    "default": "fullbody",     "marching": "fullbody",
    "walking": "fullbody",     "crouching": "fullbody",
    "crossed": "fullbody",     "criss_cross": "fullbody",
    "ultimate": "fullbody",    "isometric": "fullbodyiso",
    "head": "headiso",         "custom": "fullbody",
    "cheering": "fullbody",    "relaxing": "fullbody",
    "trudging": "fullbody",    "cowering": "fullbody",
    "pointing": "fullbody",    "lunging": "fullbody",
    "dungeons": "fullbody",    "facepalm": "fullbody",
    "sleeping": "fullbody",    "dead": "fullbody",
    "archer": "fullbody",      "kicking": "fullbody",
    "mojavatar": "fullbody",   "reading": "fullbody",
    "high_ground": "fullbody", "clown": "fullbody",
    "bitzel": "fullbody",      "pixel": "fullbody",
    "ornament": "fullbody",    "skin": "skin",
    "profile": "fullbody",
}

# 壁纸配置（已废弃 - nmsr 不支持壁纸功能）
WALLPAPER_CONFIGS = {}

# 默认请求头配置

DEFAULT_HEADER = {
        'authority': 'namemc.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'referer': 'https://www.google.com/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# 默认渲染配置
DEFAULT_RENDERTYPE = "fullbody"

# 自定义渲染配置（已废弃 - nmsr 不支持自定义模型上传）
DEFAULT_CAMERA_POSITION = {}
DEFAULT_CAMERA_FOCAL_POINT = {}
ALLOWED_MODEL_EXTENSIONS = set()
FILE_WAIT_TIMEOUT = 15

# 预置相机/焦点（已废弃，保留空字典避免导入错误）
CAMERA_PRESETS = {}
FOCAL_PRESETS = {}
