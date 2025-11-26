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

# 自定义渲染配置
CUSTOM_RENDER_API_ENDPOINT = "https://starlightskins.lunareclipse.studio/render/custom/{uuid}/full"
DEFAULT_CAMERA_POSITION = {"x":"-4.94","y":"32.09","z":"-21.6"}
DEFAULT_CAMERA_FOCAL_POINT = {"x":"3.67","y":"16.31","z":"3.35"}
ALLOWED_MODEL_EXTENSIONS = {".obj"}
# 等待用户发送文件的超时时间（秒）
FILE_WAIT_TIMEOUT = 15

# 预置的相机位置与焦点位置，用户可以在 /customskin 命令中按名称引用
CAMERA_PRESETS = {
    "default": {"x":"11.92","y":"15.81","z":"-29.71"},
    "marching": {"x":"21.96","y":"11.12","z":"-28.25"},
    "walking": {"x":"23.86","y":"22.67","z":"-26.65"},
    "crouching": {"x":"16.29","y":"21.82","z":"-34.03"},
    "crossed": {"x":"17.65","y":"21.37","z":"-24.47"},
    "criss_cross": {"x":"11.92","y":"15.81","z":"-29.71"},
    "ultimate": {"x":"15","y":"22","z":"-35"},
    "isometric": {"x":"-64","y":"60.26","z":"-64"},
    "head": {"x":"9.97","y":"19.64","z":"-20.98"},
    "cheering": {"x":"14.88","y":"28.91","z":"-30.19"},
    "relaxing": {"x":"-16.04","y":"16.57","z":"-27.5"},
    "trudging": {"x":"16.04","y":"16.57","z":"-27.5"},
    "cowering": {"x":"-14.62","y":"15.93","z":"-23.63"},
    "pointing": {"x":"-3.41","y":"18.3","z":"-30.8"},
    "lunging": {"x":"-0.41","y":"24.7","z":"-34.73"},
    "dungeons": {"x":"15.26","y":"19.62","z":"-27.58"},
    "facepalm": {"x":"3.11","y":"17.56","z":"-31.13"},
    "mojavatar": {"x":"23.05","y":"26.98","z":"-34.47"},
    "front": {"x":"0", "y":"18", "z":"-40"},
    "back": {"x":"0", "y":"18", "z":"40"},
    "left": {"x":"40", "y":"18", "z":"0"},
    "right": {"x":"-40", "y":"18", "z":"0"},
    "top": {"x":"0", "y":"60", "z":"0"},
    "top_30_deg": {"x":"0", "y":"40", "z":"-50"},
}

FOCAL_PRESETS = {
    "default": {"x":"0.31","y":"18.09","z":"1.32"},
    "marching": {"x":"0.03","y":"16.12","z":"-0.33"},
    "walking": {"x":"-1.49","y":"17.46","z":"2.16"},
    "crouching": {"x":"-1.83","y":"16.04","z":"-0.29"},
    "crossed": {"x":"-0.35","y":"16.83","z":"0.44"},
    "criss_cross": {"x":"0.31","y":"18.09","z":"1.32"},
    "ultimate": {"x":"0","y":"16","z":"0"},
    "isometric": {"x":"4","y":"12","z":"4"},
    "head": {"x":"-0.01","y":"27.96","z":"-0.32"},
    "cheering": {"x":"-0.19","y":"17.08","z":"3.46"},
    "relaxing": {"x":"-1.05","y":"6.89","z":"0.5"},
    "trudging": {"x":"0.03","y":"16.12","z":"-0.33"},
    "cowering": {"x":"1.38","y":"12.29","z":"-0.37"},
    "pointing": {"x":"-0.08","y":"19.08","z":"2.23"},
    "lunging": {"x":"0.45","y":"20.78","z":"3.79"},
    "dungeons": {"x":"-1.06","y":"17.6","z":"1.26"},
    "facepalm": {"x":"0.55","y":"20.96","z":"1.8"},
    "mojavatar": {"x":"1.27","y":"16.9","z":"-0.21"},
    "front": {"x":"0", "y":"18", "z":"0"},
    "back": {"x":"0", "y":"18", "z":"0"},
    "left": {"x":"0", "y":"18", "z":"0"},
    "right": {"x":"0", "y":"18", "z":"0"},
    "top": {"x":"0", "y":"16", "z":"0"},
    "top_30_deg": {"x":"0", "y":"18", "z":"0"},
}
