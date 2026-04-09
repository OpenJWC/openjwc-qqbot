from typing import List

import httpx
from nonebot import logger

from plugins.news.model import SuccessResponse, FetchedNotice, LabelsResponse, FetchNewsResponseData, \
    SearchQueryResponseData, SearchQuery


class NewsFetcher:
    def __init__(self, host: str, port: int, auth: str, device_id: str, use_http: bool = False):
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
                    result = SuccessResponse[FetchNewsResponseData].model_validate(resp.json())
                    return result.data.notices
                else:
                    logger.error(f"API Failure: {resp.status_code}")
            except Exception as e:
                logger.error(f"Network Error: {e}")
            return []

    async def search_notices(self, query: str, top_k: int = 5) -> List[SearchQuery]:
        async with httpx.AsyncClient(timeout=20) as client:
            try:
                payload = {"query": query, "top_k": top_k}

                resp = await client.post(
                    f"{self.base_url}api/v1/client/notices/search",
                    headers=self.headers,
                    json=payload
                )

                if resp.status_code == 200:
                    result = SuccessResponse[SearchQueryResponseData].model_validate(resp.json())
                    return result.data.results
                else:
                    logger.error(f"搜索 API 失败: {resp.status_code}, 响应: {resp.text}")
            except Exception as e:
                logger.error(f"语义搜索网络错误: {e}")
            return []
