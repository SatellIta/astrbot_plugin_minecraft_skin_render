import aiohttp
from astrbot.api import logger
import json

async def upload_to_tmpfiles(session: aiohttp.ClientSession, file_path: str) -> str | None:
    """
    将文件上传到 tmpfiles.org 并返回公共 URL
    """
    try:
        logger.info(f"正在尝试上传文件到 tmpfiles.org: {file_path}...")
        
        data = aiohttp.FormData()
        data.add_field('file',
                       open(file_path, 'rb'),
                       filename = file_path.split('/')[-1] + '.obj'
                       )

        # tmpfiles.org API endpoint
        url = 'https://tmpfiles.org/api/v1/upload'
        
        # 设置请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # 增加30秒超时
        async with session.post(url, data=data, headers=headers, timeout=30) as response:
            if response.status == 200:
                result = await response.json()
                if result.get("status") == "success":
                    # API返回的是页面URL，格式为: https://tmpfiles.org/xxxx/filename.ext
                    page_url = result.get("data", {}).get("url")
                    if page_url:
                        # 将其转换为直接下载链接，格式为: https://tmpfiles.org/dl/xxxx/filename.ext
                        public_url = page_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                        logger.info(f"tmpfiles.org 上传成功，URL: {public_url}")
                        return public_url
                    else:
                        logger.error(f"tmpfiles.org API 响应中缺少 URL: {result}")
                        return None
                else:
                    logger.error(f"tmpfiles.org API 返回失败: {result}")
                    return None
            else:
                error_text = await response.text()
                logger.error(f"上传到 tmpfiles.org 失败，状态码: {response.status}, 错误: {error_text}")
                return None
    except Exception as e:
        logger.error(f"上传到 tmpfiles.org 过程中发生异常: {e}", exc_info=True)
        return None
