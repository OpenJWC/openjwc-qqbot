from typing import Optional, List

from pydantic import BaseModel, Field


class Config(BaseModel):
    openjwc_host: str = "api.openjwc.org"
    openjwc_port: int = 443
    openjwc_use_http: bool = False

    openjwc_auth_key: str
    openjwc_device_id: str = "nonebot_default_device"

    openjwc_notice_groups: List[int] = Field(default_factory=list)
    openjwc_check_interval: int = 5

    class Config:
        extra = "ignore"