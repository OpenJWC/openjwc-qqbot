from typing import List, Optional, Generic, TypeVar

from nonebot_plugin_orm import Model
from pydantic import BaseModel, Field
from sqlalchemy import String, Boolean, JSON
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


class SearchQuery(BaseModel):
    id: str
    label: str
    title: str
    date: str
    detail_url: str
    is_page: bool
    similarity_score: float
    distance: float


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchQueryResponseData(BaseModel):
    total_found: int
    results: List[SearchQuery]


T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    msg: str
    data: T


class PushedNotice(Model):
    __tablename__ = "fetch_news_pushed_notice"

    id: Mapped[str] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    date: Mapped[str] = mapped_column(String, index=True)
    detail_url: Mapped[str] = mapped_column(String)
    is_page: Mapped[bool] = mapped_column(Boolean)
    content_text: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    attachment_urls: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
