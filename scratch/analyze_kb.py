import re
import os
import json
import argparse
from collections import Counter, defaultdict
from datetime import datetime

# Define file paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

# 品类 → KB 文件 / stats 输出映射
BOOK_TYPE_MAP = {
    "female_novel": ("hot_books_kb.md", "statistics_output.txt"),
    "male_novel":   ("hot_books_male_kb.md", "statistics_output_male.txt"),
    "short_story":  ("hot_books_short_kb.md", "statistics_output_short.txt"),
    "short_drama":  ("hot_books_short_kb.md", "statistics_output_short.txt"),
}

# 女频分类映射
FEMALE_CATEGORY_MAP = {
    '都市言情': '豪门总裁/都市现代',
    '现代言情': '豪门总裁/都市现代',
    '古代言情': '古代言情',
    '年代': '年代文/种田日常',
    '种田': '年代文/种田日常',
    '随军': '年代文/种田日常',
    '系统': '穿书/系统/女配觉醒',
    '穿书': '穿书/系统/女配觉醒',
    '脑洞': '脑洞/无限流/发疯文学/大女主',
    '幻想言情': '脑洞/无限流/发疯文学/大女主',
    '悬疑': '脑洞/无限流/发疯文学/大女主',
}

# 男频分类映射
MALE_CATEGORY_MAP = {
    '玄幻奇幻': '玄幻奇幻',
    '玄幻': '玄幻奇幻',
    '仙侠武侠': '仙侠武侠',
    '仙侠': '仙侠武侠',
    '武侠': '仙侠武侠',
    '都市职场': '都市职场',
    '都市': '都市职场',
    '历史军事': '历史军事',
    '历史': '历史军事',
    '悬疑推理': '悬疑推理',
    '悬疑': '悬疑推理',
    '科幻末世': '科幻末世',
    '科幻': '科幻末世',
    '游戏电竞': '游戏电竞',
    '游戏': '游戏电竞',
}

NEW_BOOKS = [
    {
        "title": "桃源大地主",
        "author": "乡村野夫",
        "category": "现代言情",
        "tags": "搞笑,种田,日常,无脑残,无狗血",
        "word_count": "650000",
        "read_count": "3200000",
        "rank_type": "搞笑榜",
        "book_id": "10051",
        "insert_time": "2026-05-23",
        "abstract": "讲述在桃源村的轻松悠闲种田生活，没有无脑反派 and 狗血误会，全凭爆笑日常和种田致富吸引读者，是高分精品。"
    },
    {
        "title": "穿成炮灰？我在娘胎卷哭修仙界",
        "author": "卷王之王",
        "category": "幻想言情",
        "tags": "穿书,修仙,女强,搞笑,爽文",
        "word_count": "1200000",
        "read_count": "4800000",
        "rank_type": "脑洞榜",
        "book_id": "10052",
        "insert_time": "2026-05-23",
        "abstract": "女主穿越成还没出生的炮灰婴儿，绑定了卷王系统，在娘胎里就开始修炼。出生后凭借妖孽资质和反套路作风，把修仙界的各路天才卷得哭爹喊娘，一路爽快逆袭。"
    },
    {
        "title": "欺负烈士遗孤？七个司令爹杀疯了",
        "author": "爱吃火锅",
        "category": "现代言情",
        "tags": "团宠,爽文,军婚,打脸,女强",
        "word_count": "800000",
        "read_count": "4300000",
        "rank_type": "现代言情榜",
        "book_id": "10053",
        "insert_time": "2026-05-23",
        "abstract": "烈士遗孤女主在乡下备受恶毒亲戚欺凌，千钧一发之际，父亲当年带过的七个战友（如今皆为军区司令大佬）开着直升机和坦克霸气降临，全方位开启护犊子模式，疯狂打脸人渣，团宠上天。"
    },
    {
        "title": "刚重生，娇憨小哑妻开口说话了",
        "author": "悔悟之光",
        "category": "现代言情",
        "tags": "重生,年代,糙汉,甜宠,日常",
        "word_count": "750000",
        "read_count": "3800000",
        "rank_type": "年代文榜",
        "book_id": "10054",
        "insert_time": "2026-05-23",
        "abstract": "男主前世亏欠妻子，重生回到1986年妻子和女儿出事的前夕。他改过自新，疼爱娇妻、照顾女儿，在东北农村白手起家，开启家长里短的温馨致富生活，治愈救赎。"
    },
    {
        "title": "山山有药",
        "author": "橘香袭人",
        "category": "古代言情",
        "tags": "种田,中医,致富,打脸,大女主",
        "word_count": "900000",
        "read_count": "3500000",
        "rank_type": "古代言情榜",
        "book_id": "10055",
        "insert_time": "2026-05-23",
        "abstract": "中医女主穿越成古代山村的泼辣农女，不仅精通医术，还致力于改变村里重男轻女的陈旧观念，带领全村妇女搞药材种植、开办扫盲班脱贫，极具现实颗粒度。"
    },
    {
        "title": "硬骨头",
        "author": "北斗二娘",
        "category": "现代言情",
        "tags": "悬疑,刑侦,双强,商战,相爱相杀",
        "word_count": "850000",
        "read_count": "3100000",
        "rank_type": "悬疑推理榜",
        "book_id": "10056",
        "insert_time": "2026-05-23",
        "abstract": "主剧情的硬核刑侦文，男女主皆为刑警队中坚力量，脾气硬邦邦。两人面对离奇而又高能的连环案件，强强联手、破案追凶，并在生死边缘与日常互怼中产生自然克制的爱意。"
    }
]

def parse_markdown_kb(content):
    books = []
    parts = re.split(r'###\s+《', content)
    for part in parts[1:]:
        lines = part.strip().split('\n')
        title_match = re.match(r'([^》]+)》', lines[0])
        if not title_match:
            continue
        title = title_match.group(1)
        
        book = {"title": title, "abstract": ""}
        in_abstract = False
        
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('- **作者**：'):
                book['author'] = line.replace('- **作者**：', '').strip()
            elif line.startswith('- **分类**：'):
                book['category'] = line.replace('- **分类**：', '').strip()
            elif line.startswith('- **标签**：'):
                book['tags'] = line.replace('- **标签**：', '').strip()
            elif line.startswith('- **字数**：'):
                wc = line.replace('- **字数**：', '').replace('字', '').strip()
                book['word_count'] = wc
            elif line.startswith('- **阅读热度**：'):
                book['read_count'] = line.replace('- **阅读热度**：', '').strip()
            elif line.startswith('- **榜单分类**：'):
                book['rank_type'] = line.replace('- **榜单分类**：', '').strip()
            elif line.startswith('- **书籍ID**：'):
                book['book_id'] = line.replace('- **书籍ID**：', '').strip()
            elif line.startswith('- **入库时间**：'):
                book['insert_time'] = line.replace('- **入库时间**：', '').strip()
            elif line.startswith('- **简介**：'):
                in_abstract = True
            elif in_abstract:
                if line.startswith('>') or line.startswith('  >'):
                    abstract_line = re.sub(r'^\s*>\s*', '', line)
                    book['abstract'] += abstract_line + "\n"
                elif line.strip() == '' or line.startswith('---'):
                    in_abstract = False
                else:
                    book['abstract'] += line + "\n"
        book['abstract'] = book['abstract'].strip()
        books.append(book)
    return books

def main():
    parser = argparse.ArgumentParser(description="Analyze hot books KB and generate statistics.")
    parser.add_argument("--book-type", choices=["female_novel", "male_novel", "short_story", "short_drama"],
                        default="female_novel", help="Book type to analyze (default: female_novel)")
    args = parser.parse_args()

    book_type = args.book_type
    kb_info = BOOK_TYPE_MAP.get(book_type, BOOK_TYPE_MAP["female_novel"])
    kb_path = os.path.join(REPO_ROOT, "knowledge_base", kb_info[0])
    output_path = os.path.join(REPO_ROOT, "scratch", kb_info[1])

    # Select the correct category mapping
    if book_type in ("male_novel",):
        cat_map = MALE_CATEGORY_MAP
        kb_title = "男频爆款知识库"
        kb_desc = "本库收集番茄小说男频高分、高流量的爆款书籍，包含书名、简介、人设、核心卖点等元数据，为后续书名及简介仿写提供底层参考。"
    elif book_type in ("short_story", "short_drama"):
        cat_map = {}
        kb_title = "短篇爆款知识库"
        kb_desc = "本库收集番茄小说/知乎盐选短篇高分、高流量的爆款作品，包含书名、简介、核心卖点等元数据，为短篇创作提供底层参考。"
    else:
        cat_map = FEMALE_CATEGORY_MAP
        kb_title = "爆款书籍知识库"
        kb_desc = "本库收集番茄小说女频高分、高流量的爆款书籍，包含书名、简介、人设、核心卖点等元数据，为后续书名及简介仿写提供底层参考。"

    if os.path.exists(kb_path):
        with open(kb_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = f"# {kb_title}\n\n"

    existing_books = parse_markdown_kb(content)
    existing_ids = {b['book_id'] for b in existing_books if 'book_id' in b}

    updated_books = list(existing_books)
    newly_added = []
    for nb in NEW_BOOKS:
        if nb['book_id'] not in existing_ids:
            updated_books.append(nb)
            newly_added.append(nb)

    if newly_added:
        # Group books and rewrite KB cleanly
        categories_dict = defaultdict(list)
        for b in updated_books:
            cat = b.get('category', '其他')
            main_cat = cat_map.get(cat, '其他') if cat_map else cat

            categories_dict[main_cat].append(b)

        with open(kb_path, 'w', encoding='utf-8') as f:
            f.write(f"# {kb_title}\n\n")
            f.write(f"{kb_desc}\n\n")

            for cat_name, books_list in categories_dict.items():
                f.write(f"## {cat_name}\n\n")
                for b in books_list:
                    f.write(f"### 《{b['title']}》\n")
                    f.write(f"- **作者**：{b.get('author', '')}\n")
                    f.write(f"- **分类**：{b.get('category', '')}\n")
                    f.write(f"- **标签**：{b.get('tags', '')}\n")
                    f.write(f"- **字数**：{b.get('word_count', '')}字\n")
                    f.write(f"- **阅读热度**：{b.get('read_count', '')}\n")
                    f.write(f"- **榜单分类**：{b.get('rank_type', '')}\n")
                    f.write(f"- **书籍ID**：{b.get('book_id', '')}\n")
                    f.write(f"- **入库时间**：{b.get('insert_time', '')}\n")
                    f.write(f"- **简介**：\n")
                    abstract_lines = b.get('abstract', '').split('\n')
                    for al in abstract_lines:
                        f.write(f"  > {al}\n")
                    f.write("\n---\n\n")

    # Run statistics on all books and write to output_path
    all_books = updated_books
    total_count = len(all_books)

    out = []
    out.append(f"Total books analyzed: {total_count}")

    # 2.1 Category/Genre Distribution
    categories = [b.get('category', '其他') for b in all_books]
    cat_counts = Counter(categories)
    out.append("\n--- CATEGORY DISTRIBUTION ---")
    for cat, cnt in cat_counts.most_common():
        percentage = (cnt / total_count) * 100
        cat_books = [b for b in all_books if b.get('category') == cat]
        cat_books.sort(key=lambda x: int(x.get('read_count', 0)) if str(x.get('read_count', 0)).isdigit() else 0, reverse=True)
        rep_works = [f"《{b['title']}》" for b in cat_books[:3]]
        out.append(f"| {cat} | {cnt} | {percentage:.1f}% | {', '.join(rep_works)} |")

    # 2.2 Tags frequency
    all_tags = []
    tag_combinations = Counter()
    tag_occurrences = defaultdict(list)
    for b in all_books:
        tags_str = b.get('tags', '')
        tags = [t.strip() for t in tags_str.split(',') if t.strip()]
        all_tags.extend(tags)
        
        sorted_tags = sorted(list(set(tags)))
        for i in range(len(sorted_tags)):
            for j in range(i + 1, len(sorted_tags)):
                tag_combinations[(sorted_tags[i], sorted_tags[j])] += 1
                
        for t in tags:
            tag_occurrences[t].append(b)

    tag_counts = Counter(all_tags)
    out.append("\n--- TAG FREQUENCY TOP 20 ---")
    for i, (tag, freq) in enumerate(tag_counts.most_common(20), 1):
        pct = (freq / total_count) * 100
        co_occurring = Counter()
        for b in tag_occurrences[tag]:
            tags = [t.strip() for t in b.get('tags', '').split(',') if t.strip()]
            for t in tags:
                if t != tag:
                    co_occurring[t] += 1
        top_co = [f"{t}({c})" for t, c in co_occurring.most_common(3)]
        out.append(f"| {i} | {tag} | {freq} | {pct:.1f}% | {', '.join(top_co)} |")

    # 2.3 Tag combinations TOP 10
    out.append("\n--- TAG COMBINATIONS TOP 10 ---")
    for i, (combo, freq) in enumerate(tag_combinations.most_common(10), 1):
        rep_works = []
        for b in all_books:
            tags = [t.strip() for t in b.get('tags', '').split(',') if t.strip()]
            if combo[0] in tags and combo[1] in tags:
                rep_works.append(f"《{b['title']}》")
        out.append(f"| {i} | {'+'.join(combo)} | {freq} | {', '.join(rep_works[:2])} |")

    # 2.4 Keyword extraction from titles and abstracts
    words = []
    stop_words = {'的', '了', '在', '是', '我', '有', '和', '人', '个', '他', '她', '它', '这', '那', '与', '被', '把', '自己', '一个', '从', '到', '去', '说', '后', '前', '上', '下', '里', '外', '中', '要', '就', '会', '能', '来', '出', '写', '做', '而', '及', '其', '等', '之', '也', '都', '又', '只', '已', '此', '本'}
    
    for b in all_books:
        text = b.get('title', '') + " " + b.get('abstract', '')
        chunks = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        for chunk in chunks:
            for length in [2, 3, 4]:
                for start in range(len(chunk) - length + 1):
                    word = chunk[start:start+length]
                    if not any(sc in word for sc in stop_words):
                        words.append(word)
                        
    word_counts = Counter(words)
    out.append("\n--- KEYWORDS TOP 30 ---")
    meaningful_keywords = []
    printed = 0
    for w, c in word_counts.most_common(200):
        if printed >= 30:
            break
        if len(w) >= 2:
            meaningful_keywords.append((w, c))
            printed += 1
            
    for i, (w, c) in enumerate(meaningful_keywords[:30], 1):
        out.append(f"| {i} | {w} | {c} |")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print(f"Stats written to {output_path}")

if __name__ == '__main__':
    main()
