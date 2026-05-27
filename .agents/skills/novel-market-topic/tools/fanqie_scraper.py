#!/usr/bin/env python3
"""番茄小说排行榜爬虫

爬取番茄小说 API，获取各分类排行榜数据，输出结构化 JSON。

使用方法：
    python fanqie_scraper.py                              # 默认爬取女频所有分类日榜，输出到 stdout
    python fanqie_scraper.py -o data.json                 # 输出到文件
    python fanqie_scraper.py --gender male                # 爬取男频分类
    python fanqie_scraper.py --gender female --categories 古代言情,现代言情  # 指定女频分类
    python fanqie_scraper.py --gender all                 # 爬取男频+女频所有分类
    python fanqie_scraper.py --rank-type weekly            # 指定榜单类型（daily/weekly/monthly）
    python fanqie_scraper.py --pages 2                     # 每个榜单爬取页数（默认2页）

依赖：requests（pip install requests）
"""

import argparse
import json
import sys
import time
import random
from datetime import datetime
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    print("错误：需要安装 requests 库。请运行：pip install requests", file=sys.stderr)
    sys.exit(1)

# ── 常量 ──────────────────────────────────────────────

BASE_URL = "https://fanqienovel.com/api/rank/category/list"
APP_ID = "1967"
DEFAULT_LIMIT = 30
DEFAULT_PAGES = 2
MAX_RETRIES = 3
BASE_DELAY = 1.0  # 请求间隔基础秒数

# 已知的女频分类 ID 映射（后备，优先通过 API 自动发现）
KNOWN_CATEGORIES_FEMALE = {
    "现代言情": "7",
    "古代言情": "8",
    "幻想言情": "9",
    "青春日常": "11",
}

# 已知的男频分类 ID 映射（后备，优先通过 API 自动发现）
KNOWN_CATEGORIES_MALE = {
    "玄幻奇幻": "1",
    "仙侠武侠": "2",
    "都市职场": "3",
    "历史军事": "4",
    "悬疑推理": "5",
    "科幻末世": "6",
    "游戏电竞": "12",
}

# 短篇分类（男女通用）
KNOWN_CATEGORIES_SHORT = {
    "短篇/辣文": "10",
}

RANK_TYPE_MAP = {
    "daily": "daily",
    "weekly": "weekly",
    "monthly": "monthly",
}

GENDER_CATEGORIES = {
    "female": KNOWN_CATEGORIES_FEMALE,
    "male": KNOWN_CATEGORIES_MALE,
    "short": KNOWN_CATEGORIES_SHORT,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://fanqienovel.com/rank",
}


# ── 工具函数 ──────────────────────────────────────────

def log(msg: str) -> None:
    """输出日志到 stderr，不干扰 stdout 的 JSON 输出。"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", file=sys.stderr)


def request_with_retry(url: str, params: dict, retries: int = MAX_RETRIES) -> dict | None:
    """带指数退避重试的 GET 请求。"""
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == 0 or "data" in data:
                return data
            log(f"  API 返回异常 code={data.get('code')}, msg={data.get('message', '无')}")
        except requests.RequestException as e:
            log(f"  请求失败（第{attempt + 1}次）：{e}")
        if attempt < retries - 1:
            delay = BASE_DELAY * (2 ** attempt) + random.uniform(0, 0.5)
            log(f"  等待 {delay:.1f}s 后重试...")
            time.sleep(delay)
    return None


def sleep_between_requests() -> None:
    """请求间随机延迟，防反爬。"""
    delay = BASE_DELAY + random.uniform(0.2, 0.8)
    time.sleep(delay)


# ── 分类发现 ──────────────────────────────────────────

def discover_categories(gender: str = "female") -> dict[str, str]:
    """尝试从页面或 API 自动发现分类列表。

    Args:
        gender: 目标性别分类 ("female", "male", "short")

    如果自动发现失败，回退到已知的硬编码分类。
    """
    # 尝试从排行榜页面 API 获取分类信息
    discovery_urls = [
        "https://fanqienovel.com/api/rank/category/list/page",
        "https://fanqienovel.com/api/author/library/category_list",
    ]

    for url in discovery_urls:
        params = {"app_id": APP_ID, "gender": gender}
        data = request_with_retry(url, params, retries=1)
        if data and "data" in data:
            categories = {}
            items = data["data"]
            if isinstance(items, list):
                for item in items:
                    name = item.get("category_name") or item.get("name", "")
                    cid = str(item.get("category_id") or item.get("id", ""))
                    if name and cid:
                        categories[name] = cid
            if categories:
                log(f"自动发现 {len(categories)} 个分类（{gender}）：{', '.join(categories.keys())}")
                return categories
        sleep_between_requests()

    # 回退到已知分类
    gender_label = {"female": "女频", "male": "男频", "short": "短篇"}.get(gender, gender)
    fallback = GENDER_CATEGORIES.get(gender, KNOWN_CATEGORIES_FEMALE)
    log(f"自动发现分类失败（{gender_label}），使用内置分类列表")
    return fallback.copy()


# ── 榜单爬取 ──────────────────────────────────────────

def fetch_rank_page(
    category_id: str,
    rank_mold: str = "daily",
    offset: int = 0,
    limit: int = DEFAULT_LIMIT,
    gender: str = "female",
) -> list[dict]:
    """爬取一页排行榜数据。"""
    params = {
        "app_id": APP_ID,
        "rank_list_type": "3",
        "category_id": category_id,
        "gender": gender,
        "rankMold": rank_mold,
        "offset": str(offset),
        "limit": str(limit),
    }

    data = request_with_retry(BASE_URL, params)
    if not data:
        return []

    books_raw = []
    # 尝试多种可能的响应结构
    if "data" in data:
        d = data["data"]
        if isinstance(d, list):
            books_raw = d
        elif isinstance(d, dict):
            books_raw = d.get("book_list") or d.get("rank_list") or d.get("list") or []
            if not books_raw and "data" in d:
                books_raw = d["data"] if isinstance(d["data"], list) else []

    return books_raw


def parse_book(raw: dict, category_name: str, rank_type: str) -> dict:
    """将 API 返回的原始书籍数据解析为标准格式。"""
    # 提取 tags
    tags = []
    tag_field = raw.get("tag") or raw.get("tags") or raw.get("tag_list") or ""
    if isinstance(tag_field, str) and tag_field:
        tags = [t.strip() for t in tag_field.split(",") if t.strip()]
    elif isinstance(tag_field, list):
        for t in tag_field:
            if isinstance(t, str):
                tags.append(t.strip())
            elif isinstance(t, dict):
                tags.append(t.get("tag_name") or t.get("name", ""))

    # 提取字数
    word_count = raw.get("word_count") or raw.get("word_number") or 0
    if isinstance(word_count, str):
        word_count = int(word_count) if word_count.isdigit() else 0

    # 提取阅读量
    read_count = raw.get("read_count") or raw.get("hot_value") or raw.get("total_read") or 0
    if isinstance(read_count, str):
        read_count = int(read_count) if read_count.isdigit() else 0

    return {
        "book_id": str(raw.get("book_id") or raw.get("item_id") or raw.get("id", "")),
        "title": raw.get("book_name") or raw.get("title") or raw.get("name", ""),
        "author": raw.get("author") or raw.get("author_name") or "",
        "abstract": raw.get("abstract") or raw.get("desc") or raw.get("description") or "",
        "word_count": word_count,
        "tags": [t for t in tags if t],
        "category": category_name,
        "rank_type": rank_type,
        "read_count": read_count,
        "thumb_url": raw.get("thumb_url") or raw.get("cover") or "",
        "creation_status": raw.get("creation_status") or raw.get("serial_status") or "",
    }


def scrape_category(
    category_name: str,
    category_id: str,
    rank_mold: str = "daily",
    pages: int = DEFAULT_PAGES,
    gender: str = "female",
) -> list[dict]:
    """爬取单个分类的多页排行榜数据。"""
    rank_type_label = {"daily": "日榜", "weekly": "周榜", "monthly": "月榜"}.get(rank_mold, rank_mold)
    log(f"爬取 [{category_name}] {rank_type_label}（共 {pages} 页）...")

    books = []
    for page in range(pages):
        offset = page * DEFAULT_LIMIT
        log(f"  第 {page + 1} 页（offset={offset}）...")
        raw_list = fetch_rank_page(category_id, rank_mold, offset, gender=gender)

        if not raw_list:
            log(f"  第 {page + 1} 页无数据，停止翻页")
            break

        for raw in raw_list:
            book = parse_book(raw, category_name, rank_type_label)
            if book["book_id"] and book["title"]:
                books.append(book)

        log(f"  获取 {len(raw_list)} 本书")
        if page < pages - 1:
            sleep_between_requests()

    return books


# ── 主流程 ──────────────────────────────────────────

def scrape_all(
    target_categories: list[str] | None = None,
    rank_type: str = "daily",
    pages: int = DEFAULT_PAGES,
    gender: str = "female",
) -> dict:
    """执行完整爬取流程。

    Args:
        target_categories: 目标分类名称列表。None 表示爬取所有分类。
        rank_type: 榜单类型 daily/weekly/monthly。
        pages: 每个榜单爬取页数。
        gender: 目标性别分类 ("female", "male", "short", "all")。
                 "all" 表示爬取女频+男频所有分类。
    """
    gender_label = {"female": "女频", "male": "男频", "short": "短篇", "all": "全部"}.get(gender, gender)
    log("=" * 50)
    log(f"番茄小说排行榜爬虫启动（{gender_label}）")
    log("=" * 50)

    if gender == "all":
        # 爬取全部：先女频后男频
        all_books = []
        all_categories_scraped = []
        for g in ("female", "male"):
            result = scrape_all(
                target_categories=target_categories,
                rank_type=rank_type,
                pages=pages,
                gender=g,
            )
            all_books.extend(result.get("books", []))
            all_categories_scraped.extend(result.get("categories_scraped", []))
            sleep_between_requests()
        # 去重
        seen_ids = set()
        unique_books = []
        for book in all_books:
            bid = book["book_id"]
            if bid not in seen_ids:
                seen_ids.add(bid)
                unique_books.append(book)
        log(f"\n全量爬取完成：共 {len(unique_books)} 本去重书籍")
        return {
            "scrape_time": datetime.now().isoformat(),
            "total_books": len(unique_books),
            "categories_scraped": all_categories_scraped,
            "rank_type": rank_type,
            "gender": "all",
            "books": unique_books,
        }

    # 1. 获取分类列表
    all_categories = discover_categories(gender=gender)
    sleep_between_requests()

    # 2. 筛选目标分类
    if target_categories:
        categories = {}
        for name in target_categories:
            name = name.strip()
            if name in all_categories:
                categories[name] = all_categories[name]
            else:
                log(f"警告：分类 '{name}' 未找到，跳过。可用分类：{', '.join(all_categories.keys())}")
        if not categories:
            log("错误：没有有效的分类可爬取")
            return {"scrape_time": datetime.now().isoformat(), "total_books": 0, "books": []}
    else:
        categories = all_categories

    # 3. 逐分类爬取
    all_books = []
    for i, (cat_name, cat_id) in enumerate(categories.items()):
        books = scrape_category(cat_name, cat_id, rank_type, pages, gender=gender)
        all_books.extend(books)
        if i < len(categories) - 1:
            sleep_between_requests()

    # 4. 去重（同一本书可能出现在多个榜单）
    seen_ids = set()
    unique_books = []
    duplicate_count = 0
    for book in all_books:
        bid = book["book_id"]
        if bid not in seen_ids:
            seen_ids.add(bid)
            unique_books.append(book)
        else:
            duplicate_count += 1

    log(f"\n爬取完成：共 {len(all_books)} 条记录，去重后 {len(unique_books)} 本书（{duplicate_count} 本重复）")

    return {
        "scrape_time": datetime.now().isoformat(),
        "total_books": len(unique_books),
        "categories_scraped": list(categories.keys()),
        "rank_type": rank_type,
        "gender": gender,
        "books": unique_books,
    }


def main():
    parser = argparse.ArgumentParser(
        description="番茄小说排行榜爬虫",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例：\n"
               "  python fanqie_scraper.py\n"
               "  python fanqie_scraper.py -o data.json\n"
               "  python fanqie_scraper.py --gender male --categories 玄幻奇幻,都市职场\n"
               "  python fanqie_scraper.py --gender all\n"
               "  python fanqie_scraper.py --rank-type weekly --pages 3\n",
    )
    parser.add_argument("-o", "--output", help="输出 JSON 文件路径（默认输出到 stdout）")
    parser.add_argument(
        "--gender",
        choices=["female", "male", "short", "all"],
        default="female",
        help="目标性别分类：female（女频，默认）、male（男频）、short（短篇）、all（全部）",
    )
    parser.add_argument(
        "--categories",
        help="指定分类，逗号分隔（如：古代言情,现代言情）。不指定则爬取对应性别的所有分类",
    )
    parser.add_argument(
        "--rank-type",
        choices=["daily", "weekly", "monthly"],
        default="daily",
        help="榜单类型（默认 daily）",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=DEFAULT_PAGES,
        help=f"每个榜单爬取页数（默认 {DEFAULT_PAGES}，每页 {DEFAULT_LIMIT} 本）",
    )

    args = parser.parse_args()

    # 解析分类参数
    target_categories = None
    if args.categories:
        target_categories = [c.strip() for c in args.categories.split(",") if c.strip()]

    # 执行爬取
    result = scrape_all(
        target_categories=target_categories,
        rank_type=args.rank_type,
        pages=args.pages,
        gender=args.gender,
    )

    # 输出 JSON
    json_str = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        log(f"数据已保存到 {args.output}")
    else:
        print(json_str)


if __name__ == "__main__":
    main()
