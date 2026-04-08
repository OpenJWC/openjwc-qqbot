from typing import List, Optional

from nonebot_plugin_orm import Model
from pydantic import BaseModel, Field
from sqlalchemy.orm import Mapped, mapped_column

class LabelsData(BaseModel):
    labels: List[str]

class LabelsResponse(BaseModel):
    msg: str
    data: LabelsData

class FetchedNotice(BaseModel):
    id: str
    label: str
    title: str
    date: str
    detail_url: str = Field(alias="detail_url")
    is_page: bool = Field(alias="is_page")
    content_text: Optional[str] = Field(None, alias="content_text")
    attachment_urls: Optional[List[str]] = Field(None, alias="attachments")

class FetchNewsResponseData(BaseModel):
    total_returned: int = Field(alias="total_returned")
    total_label: int = Field(alias="total_label")
    notices: List[FetchedNotice] = Field(alias="notices")

class SuccessResponse(BaseModel):
    msg: str
    data: FetchNewsResponseData

class PushedNotice(Model):
    __tablename__ = "fetch_news_pushed_notice"
    id: Mapped[str] = mapped_column(primary_key=True)