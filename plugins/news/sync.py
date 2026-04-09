from datetime import datetime
from typing import List

from nonebot import get_bot, get_plugin_config, logger
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_apscheduler import scheduler

from .client import NewsFetcher
from .config import Config
from .model import FetchedNotice
from .search import *

config = get_plugin_config(Config)

@scheduler.scheduled_job(
    "interval",
    minutes=config.openjwc_check_interval,
    id="openjwc_news_sync",
    next_run_time=datetime.now()
)
async def sync_news():
    fetcher = NewsFetcher(
        host=config.openjwc_host,
        port=config.openjwc_port,
        auth=config.openjwc_auth_key,
        device_id=config.openjwc_device_id,
        use_http=config.openjwc_use_http
    )
    labels = await fetcher.fetch_labels()
    if not labels:
        logger.warning("未能获取到任何标签，跳过本次同步")
        return

    new_notices: List[FetchedNotice] = []

    async with get_session() as session:
        for label in labels:
            logger.debug(f"正在检查分类: {label}")
            notices = await fetcher.fetch_category(label, page=1, size=10)

            for notice in notices:
                stmt = select(PushedNotice).where(PushedNotice.id == notice.id)
                exists = (await session.execute(stmt)).scalar_one_or_none()

                if not exists:
                    new_notices.append(notice)
                    session.add(PushedNotice(
                        id=notice.id,
                        label=notice.label,
                        title=notice.title,
                        date=notice.date,
                        detail_url=notice.detail_url,
                        is_page=notice.is_page,
                        content_text=notice.content_text,
                        attachment_urls=notice.attachment_urls
                    ))

        await session.commit()

    if new_notices:
        limited_notices = new_notices[:10]
        has_more = len(new_notices) > 10

        logger.info(f"本次发现 {len(new_notices)} 条新资讯，推送前 10 条")
        await send_combined_notification(limited_notices, has_more)
    else:
        logger.debug("未检测到新资讯")


async def send_combined_notification(notices: List[FetchedNotice], has_more: bool):
    try:
        bot = get_bot()
    except ValueError:
        return

    msg = MessageSegment.at("all") + f"\n🔔 发现新资讯！(本次更新 {len(notices)} 条)\n"

    for i, notice in enumerate(notices, 1):
        msg += (
            f"\n{i}. 【{notice.label}】{notice.title}\n"
            f"   详情：{notice.detail_url}\n"
        )

    if has_more:
        msg += "\n...\n 更多资讯请前往 OpenJWC 查看。"

    # 4. 发送
    for group_id in config.openjwc_notice_groups:
        try:
            await bot.send_group_msg(group_id=group_id, message=msg)
        except Exception as e:
            logger.error(f"发送失败: {e}")

