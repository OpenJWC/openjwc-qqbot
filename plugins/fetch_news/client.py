from typing import List

import httpx
from nonebot import logger

from plugins.fetch_news.model import SuccessResponse, FetchedNotice, LabelsResponse


class NewsFetcher:
    def __init__(self, host: str, port: int, auth: str, device_id: str, use_http: bool=False):
        protocol = "http" if use_http else "https"
        self.base_url = f"{protocol}://{host}:{port}/"
        self.headers = {
            "Authorization": f"Bearer {auth}",
            "X-Device-ID": device_id
        }

    async def fetch_labels(self) -> List[str]:
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                resp = await client.get(
                    f"{self.base_url}api/v1/client/notices/labels",
                    headers=self.headers
                )
                if resp.status_code == 200:
                    result = LabelsResponse.model_validate(resp.json())
                    return result.data.labels
                logger.error(f"获取标签失败: {resp.status_code}")
            except Exception as e:
                logger.error(f"获取标签网络错误: {e}")
            return []

    async def fetch_category(self, label: str, page: int = 1, size: int = 20) -> List[FetchedNotice]:
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(
                    f"{self.base_url}api/v1/client/notices",
                    headers=self.headers,
                    params={"label": label, "page": page, "size": size}
                )
                if resp.status_code == 200:
                    result = SuccessResponse.model_validate(resp.json())
                    return result.data.notices
                else:
                    logger.error(f"API Failure: {resp.status_code}")
            except Exception as e:
                logger.error(f"Network Error: {e}")
            return []