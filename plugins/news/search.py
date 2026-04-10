from nonebot import on_command, get_plugin_config, logger
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
from nonebot_plugin_orm import get_session
from sqlalchemy import select
from thefuzz import fuzz, process

from .client import NewsFetcher
from .config import Config
from .model import PushedNotice

config = get_plugin_config(Config)

"""
def normalize_text(text: str) -> str:
    if not text: return ""
    return re.sub(r'[^\w\u4e00-\u9fa5]', '', text).lower()


def get_n_gram_parts(query: str) -> List[str]:
    clean_q = normalize_text(query)
    if not clean_q: return [query]

    if len(clean_q) <= 3:
        return list(clean_q)

    mid = len(clean_q) // 2
    parts = {clean_q, clean_q[:mid], clean_q[mid:], clean_q[1:mid + 1]}
    return [p for p in parts if len(p) >= 2]


def score_notice_flexible(query, notice, now_time: datetime):
    raw_title = notice.title or ""
    q_clean = normalize_text(query)
    t_clean = normalize_text(raw_title)

    if not q_clean or not t_clean: return 0, ""

    jw_score = distance.JaroWinkler.similarity(q_clean, t_clean) * 100
    w_score = fuzz.WRatio(q_clean, t_clean)

    coherence_bonus = 0
    if q_clean in t_clean:
        coherence_bonus = 40
    elif any(part in t_clean for part in [q_clean[i:i + 2] for i in range(len(q_clean) - 1)]):
        coherence_bonus = 15

    try:
        notice_date = datetime.strptime(notice.date, "%Y-%m-%d")
        days = (now_time - notice_date).days
        time_penalty = math.log10(days + 1) * 8
    except:
        time_penalty = 0

    final_score = (jw_score * 0.4 + w_score * 0.4 + coherence_bonus) - time_penalty

    reasons = []
    if coherence_bonus >= 40:
        reasons.append("完全匹配")
    elif w_score > 85:
        reasons.append("语义接近")
    if time_penalty < 5: reasons.append("新鲜度高")

    return max(0.0, final_score), " / ".join(reasons)
"""

check_cmd = on_command("check", aliases={"查看分类"})


@check_cmd.handle()
async def handle_check(arg: Message = CommandArg()):
    label = arg.extract_plain_text().strip()
    if not label:
        await check_cmd.finish("请输入要查看的标签名，例如：/check 教务资讯")

    if len(label) > config.openjwc_max_query_length:
        await search_cmd.finish(f"⚠️ 搜索词太长了（最多 {config.openjwc_max_query_length} 字），请精简你的关键词。")

    async with get_session() as session:
        stmt = (
            select(PushedNotice)
            .where(PushedNotice.label == label)
            .order_by(PushedNotice.date.desc())
            .limit(10)
        )
        results = (await session.execute(stmt)).scalars().all()

        if results:
            msg = f"📂 分类【{label}】下的最新通知：\n"
            for i, n in enumerate(results, 1):
                msg += f"\n{i}. {n.title}\n   🔗 {n.detail_url}"
            await check_cmd.finish(msg)

        label_stmt = select(PushedNotice.label).distinct()
        all_labels = (await session.execute(label_stmt)).scalars().all()

        if not all_labels:
            await check_cmd.finish("数据库中目前没有任何资讯记录。")

        matches = process.extract(label, all_labels, scorer=fuzz.WRatio, limit=3)
        suggestions = [m[0] for m in matches if m[1] > 50]
        if suggestions:
            suggest_text = "、".join(suggestions)
            await check_cmd.finish(f"未找到标签【{label}】。\n💡 你是不是想找：{suggest_text}？")
        else:
            all_text = "、".join(all_labels[:10])
            await check_cmd.finish(f"未找到标签【{label}】。\n当前已有标签：{all_text}...")


search_cmd = on_command("search", aliases={"搜索通知"})

"""
@search_cmd.handle()
async def handle_search(arg: Message = CommandArg()):
    raw_query = arg.extract_plain_text().strip()
    if len(raw_query) < 2:
        await search_cmd.finish("搜索词太短了，再多给两个字？")

    now_time = datetime.now()
    search_parts = get_n_gram_parts(raw_query)

    async with get_session() as session:
        conditions = []
        for p in search_parts:
            conditions.append(PushedNotice.title.ilike(f"%{p}%"))
            if len(p) > 2:
                conditions.append(PushedNotice.content_text.ilike(f"%{p}%"))

        stmt = select(PushedNotice).where(or_(*conditions))
        candidates = (await session.execute(stmt.limit(150))).scalars().all()

    if not candidates:
        await search_cmd.finish(f"翻遍了数据库也没找到关于“{raw_query}”的线索...")

    def rank_task():
        scored = []
        for n in candidates:
            score, reason = score_notice_flexible(raw_query, n, now_time)
            if score > 20:
                scored.append((n, score, reason))
        return scored

    scored = await anyio.to_thread.run_sync(rank_task)

    if not scored:
        await search_cmd.finish("匹配度较低，请尝试更换关键词。")

    # 排序
    scored.sort(key=lambda x: x[1], reverse=True)

    # 去重并构建 Top 5
    final_results = []
    seen_titles = set()
    for n, s, r in scored:
        if n.title not in seen_titles:
            seen_titles.add(n.title)
            final_results.append((n, s, r))
        if len(final_results) >= 5: break

    msg = f"🔍 “{raw_query}”的智能搜索结果：\n"
    for i, (n, score, reason) in enumerate(final_results, 1):
        msg += (
            f"\n{i}. {n.title}"
            f"\n   📅 {n.date} | ⭐ {score:.1f} ({reason or '综合推荐'})"
            f"\n   🔗 {n.detail_url}\n"
        )

    await search_cmd.finish(msg)
"""


@search_cmd.handle()
async def handle_search(arg: Message = CommandArg()):
    query = arg.extract_plain_text().strip()
    if not query:
        await search_cmd.finish("请输入搜索关键词，例如：/search 奖学金")

    if len(query) < 2:
        await search_cmd.finish("搜索词太短了，请至少输入两个字符。")

    if len(query) > config.openjwc_max_query_length:
        await search_cmd.finish(f"⚠️ 搜索词太长了（最多 {config.openjwc_max_query_length} 字），请精简你的关键词。")

    fetcher = NewsFetcher(
        host=config.openjwc_host, port=config.openjwc_port,
        auth=config.openjwc_auth_key, device_id=config.openjwc_device_id,
        use_http=config.openjwc_use_http
    )

    logger.info(f"正在进行语义搜索: {query}")
    results = await fetcher.search_notices(query=query, top_k=10)

    if not results:
        await search_cmd.finish(f"🔍 未能找到与“{query}”相关的资讯。")

    msg = f"🔍 关于“{query}”的智能搜索结果：\n"
    for i, res in enumerate(results, 1):
        msg += (
            f"\n{i}. 【{res.label}】{res.title}\n"
            f"   📅 {res.date} | 🎯 匹配度: {res.similarity_score:.2f}\n"
            f"   🔗 {res.detail_url}\n"
        )
    msg += "\n💡 提示：结果按语义相关性排序"

    await search_cmd.finish(msg)
