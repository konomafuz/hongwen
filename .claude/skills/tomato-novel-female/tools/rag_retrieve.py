#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retrieve a lightweight writing-style RAG cheat sheet for novel chapters."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable


KB_FILES = {
    "热梗表达": "memes.jsonl",
    "语感模板": "voice_patterns.jsonl",
    "短摘录分析": "excerpts.jsonl",
}

GENRE_MARKERS = {
    # ── 女频 ──
    "古言": ["古言", "王爷", "侯府", "宫", "嫡女", "庶女", "将军", "权臣", "皇", "世子", "丞相"],
    "年代": ["年代", "七零", "八零", "九零", "知青", "供销社", "大队", "工分", "家属院", "重生年代", "技能致富", "赶山", "打猎", "赶海"],
    "现言": ["现言", "总裁", "豪门", "闪婚", "办公室", "公司", "手机", "微信", "咖啡", "电梯"],
    "校园": ["校园", "同桌", "高考", "宿舍", "班主任", "校草", "学生会"],
    "娱乐圈": ["娱乐圈", "综艺", "热搜", "粉丝", "经纪人", "直播", "镜头"],
    "职场": ["职场", "公司", "会议", "老板", "同事", "客户", "项目", "甩锅"],
    # ── 男频都市 ──
    "都市高武": [
        "都市高武", "序列", "觉醒", "斩神", "戏神", "邪神", "诸神", "神明降临",
        "灵气复苏", "时停", "诡异", "异能", "超能", "克系", "守护", "诡秘",
    ],
    "上交国家": [
        "上交国家", "上交", "国家队", "宗门", "组织", "修仙界", "时空门",
        "国家复仇", "融合", "体制", "官方",
    ],
    # ── 男频玄幻仙侠 ──
    "玄幻": [
        "玄幻", "异界", "斗气", "魔法", "位面", "神兽", "契约", "武魂", "血脉",
        "天渊", "神王", "逆天", "金手指", "神墟", "万古", "至尊", "大帝",
    ],
    "仙侠": [
        "仙侠", "修仙", "修真", "渡劫", "元婴", "金丹", "飞升", "法宝", "灵根",
        "长生", "苟道", "稳健", "宗门", "炼丹", "秘境", "洞府", "仙尊",
    ],
    # ── 男频悬疑怪谈 ──
    "规则怪谈": [
        "规则怪谈", "怪谈", "无限流", "诡舍", "十日终焉", "多子多福",
        "诡异", "解密", "怪谈空间", "规则", "禁忌", "生存", "逃生",
    ],
    # ── 男频历史 ──
    "历史": [
        "历史", "争霸", "王朝", "征战", "权谋", "朝堂", "江山",
        "科举", "琅琊", "知识碾压", "家国情怀", "古人", "穿越历史", "策论",
    ],
    # ── 男频科幻末世 ──
    "末世": [
        "末世", "末世生存", "公路求生", "囤货", "丧尸", "避难所",
        "末日", "废土", "生存焦虑", "物资",
    ],
    "科幻": [
        "科幻", "星际", "赛博", "机甲", "基因", "变异", "舰队",
        "深空", "AI", "未来", "高科技", "宇宙",
    ],
    # ── 男频游戏衍生 ──
    "游戏竞技": [
        "游戏", "电竞", "副本", "装备", "公会", "竞技", "对战",
        "游戏入侵", "抢机缘", "反套路", "全息", "网游",
    ],
    "衍生同人": [
        "同人", "衍生", "火影", "奥特曼", "四合院", "二郎神",
        "动漫IP", "影视同人", "人民的名义", "崩铁", "三角洲",
    ],
    # ── 男频通用 ──
    "系统流": [
        "系统", "签到", "神豪", "职业系统", "绑定", "商城",
        "抽奖", "兑换", "升级系统", "面板",
    ],
    "脑洞": [
        "脑洞", "搞笑", "玩梗", "整活", "反差", "沙雕", "抽象",
        "荒诞", "创意", "新奇",
    ],
}

SCENE_MARKERS = {
    # ── 女频场景 ──
    "反击": ["反击", "回怼", "怼", "打脸", "揭穿", "阴阳", "嘲讽", "刁难", "道德绑架"],
    "社死": ["社死", "尴尬", "误会", "撞见", "丢脸", "下不来台"],
    "暧昧拉扯": ["暧昧", "拉扯", "吃醋", "嘴硬", "告白", "心动", "靠近"],
    "家庭矛盾": ["亲戚", "家宴", "婆婆", "姑姑", "舅妈", "催婚", "彩礼", "继母"],
    "职场甩锅": ["甩锅", "会议", "同事", "老板", "客户", "背锅", "方案"],
    "马甲": ["马甲", "身份", "掉马", "隐藏", "揭穿", "认出"],
    "甜宠": ["甜宠", "照顾", "护着", "心疼", "偏爱", "撑腰"],
    # ── 男频场景：都市高武 ──
    "序列觉醒": [
        "觉醒", "序列", "激活", "超能", "能力觉醒", "SSS", "天赋",
        "资质", "血脉觉醒", "变异",
    ],
    "斩神/守护": [
        "斩神", "戏神", "邪神", "神明", "守护", "城市", "拯救",
        "对抗", "降临", "诡异",
    ],
    # ── 男频场景：规则博弈 ──
    "规则博弈": [
        "规则", "博弈", "解密", "破局", "推理", "陷阱", "怪谈",
        "智斗", "逻辑", "线索", "反转",
    ],
    # ── 男频场景：上交国家 ──
    "上交国家": [
        "上交", "国家", "组织", "汇报", "国家队", "宗门", "官方介入",
        "报告", "合作", "体制", "民族",
    ],
    # ── 男频场景：战斗升级 ──
    "战斗": [
        "战斗", "击杀", "秒杀", "暴击", "力量", "对战", "碾压",
        "斩杀", "团灭", "对决", "大战",
    ],
    "升级打怪": [
        "升级", "打怪", "突破", "修炼", "灵石", "筑基", "金丹", "元丹",
        "练功", "冲关", "渡劫", "历练",
    ],
    # ── 男频场景：苟道/扮猪吃虎 ──
    "苟道长生": [
        "苟道", "长生", "躺平", "低调", "稳健", "发育", "隐藏实力",
        "扮猪", "隐忍", "积蓄", "底牌", "保命",
    ],
    "扮猪吃虎": [
        "扮猪吃虎", "隐藏", "实力", "碾压", "打脸", "震惊",
        "深藏不露", "低调", "爆发", "反差",
    ],
    # ── 男频场景：秘境/探险 ──
    "秘境探险": [
        "秘境", "遗迹", "宝藏", "传承", "洞府", "探险", "禁地",
        "古墓", "寻宝", "冒险",
    ],
    # ── 男频场景：搞笑整活 ──
    "搞笑整活": [
        "搞笑", "玩梗", "整活", "沙雕", "反差", "互坑", "吐槽",
        "幽默", "笑点", "轻松",
    ],
    # ── 男频场景：情绪爆发 ──
    "情绪爆发": [
        "爆发", "复仇", "破碎", "不屈", "释放", "逆袭", "崛起",
        "打脸", "翻盘", "崛起",
    ],
    # ── 男频场景：游戏入侵 ──
    "游戏入侵": [
        "游戏入侵", "抢机缘", "反套路", "副本攻略", "抢怪", "首杀",
        "游戏降临", "全息", "竞技场",
    ],
}

# 女频现代题材
MODERN_GENRES = {"现言", "校园", "娱乐圈", "职场"}
# 女频古风/年代题材
PERIOD_GENRES = {"古言", "年代"}
# 男频题材全集
MALE_GENRES = {"都市高武", "上交国家", "玄幻", "仙侠", "规则怪谈", "历史", "末世", "科幻", "游戏竞技", "衍生同人", "系统流", "脑洞"}


@dataclass
class RagEntry:
    kind: str
    data: dict[str, Any]
    score: float = 0.0
    reasons: list[str] | None = None


def read_text_arg(value: str | None, file_value: str | None) -> str:
    parts: list[str] = []
    if value:
        parts.append(value)
    if file_value:
        parts.append(Path(file_value).read_text(encoding="utf-8"))
    return "\n".join(parts).strip()


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in re.split(r"[,，/、\s]+", value) if item.strip()]
    return [str(value).strip()]


def primary_text(data: dict[str, Any]) -> str:
    for key in ("phrase", "pattern", "text", "title", "excerpt", "analysis", "usage", "meaning"):
        value = data.get(key)
        if value:
            return str(value)
    return ""


def combined_text(data: dict[str, Any]) -> str:
    chunks: list[str] = []
    for value in data.values():
        if isinstance(value, list):
            chunks.extend(str(item) for item in value)
        elif isinstance(value, dict):
            chunks.extend(str(item) for item in value.values())
        elif value is not None:
            chunks.append(str(value))
    return " ".join(chunks)


def detect_labels(text: str, markers: dict[str, list[str]]) -> list[str]:
    found: list[str] = []
    for label, words in markers.items():
        if any(word in text for word in words):
            found.append(label)
    return found


def extract_terms(text: str) -> set[str]:
    terms: set[str] = set()
    for label, words in {**GENRE_MARKERS, **SCENE_MARKERS}.items():
        if label in text or any(word in text for word in words):
            terms.add(label)
            terms.update(word for word in words if word in text)
    for token in re.findall(r"[A-Za-z0-9_]{2,}|[\u4e00-\u9fff]{2,8}", text):
        terms.add(token.lower())
    return terms


def load_entries(kb_root: Path) -> tuple[list[RagEntry], list[str]]:
    entries: list[RagEntry] = []
    warnings: list[str] = []
    kb_dir = kb_root / "kb"
    for kind, filename in KB_FILES.items():
        path = kb_dir / filename
        if not path.exists():
            warnings.append(f"缺少知识库文件：{path}")
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                warnings.append(f"{filename}:{line_no} JSON 解析失败：{exc.msg}")
                continue
            if isinstance(data, dict):
                entries.append(RagEntry(kind=kind, data=data))
            else:
                warnings.append(f"{filename}:{line_no} 不是 JSON 对象，已跳过")
    return entries, warnings


def parse_day(value: Any) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def score_entry(entry: RagEntry, query_terms: set[str], query_genres: list[str], query_scenes: list[str]) -> RagEntry:
    data = entry.data
    text = combined_text(data).lower()
    entry_terms = extract_terms(text)
    entry_genres = as_list(data.get("genres"))
    entry_scenes = as_list(data.get("scenes"))
    reasons: list[str] = []
    score = 0.0

    overlap = query_terms & entry_terms
    if overlap:
        score += min(len(overlap), 8) * 1.5
        reasons.append("关键词匹配：" + "、".join(sorted(list(overlap))[:5]))

    scene_overlap = set(query_scenes) & set(entry_scenes)
    if scene_overlap:
        score += len(scene_overlap) * 4
        reasons.append("场景匹配：" + "、".join(scene_overlap))

    # 题材冲突判定（古言/年代文坚决不用现代网络表达，硬过滤）
    if (set(query_genres) & PERIOD_GENRES) and (set(entry_genres) & MODERN_GENRES):
        score -= 10
        reasons.append("题材冲突：古言/年代慎用现代网络表达")
    elif query_genres and entry_genres:
        genre_overlap = set(query_genres) & set(entry_genres)
        if genre_overlap:
            score += len(genre_overlap) * 3
            reasons.append("题材匹配：" + "、".join(genre_overlap))
        elif set(query_genres) & MODERN_GENRES and set(entry_genres) & {"古言"}:
            score -= 2
            reasons.append("题材弱匹配")

    expiry_risk = str(data.get("expiry_risk", "")).strip()
    if data.get("needs_review") is True:
        score -= 6
        reasons.append("候选条目尚未人工确认，降权")
    elif str(data.get("review_status", "")).strip() == "approved":
        score += 2
        reasons.append("人工确认条目")

    if str(data.get("review_status", "")).strip() == "rejected":
        score -= 20
        reasons.append("已剔除条目")

    if expiry_risk == "高":
        score -= 1.5
        reasons.append("过期风险高，慎用")
    elif expiry_risk == "低":
        score += 0.5

    expires_at = parse_day(data.get("expires_at"))
    if expires_at and expires_at < date.today():
        score -= 4
        reasons.append("已超过建议使用日期")

    added_at = parse_day(data.get("date"))
    if added_at:
        age_days = (date.today() - added_at).days
        if age_days <= 30:
            score += 1
        elif age_days > 180:
            score -= 1
            reasons.append("录入较久，注意新鲜度")

    entry.score = score
    entry.reasons = reasons
    return entry


def choose_entries(entries: Iterable[RagEntry], limit: int, minimum: int) -> list[RagEntry]:
    # 针对古言/年代文的硬性过滤，杜绝现代梗混入
    safe_entries = []
    for item in entries:
        reasons = item.reasons or []
        # 如果打上了题材冲突标签，直接在此丢弃
        if any("题材冲突" in r for r in reasons):
            continue
        safe_entries.append(item)
        
    ranked = sorted(safe_entries, key=lambda item: item.score, reverse=True)
    positives = [item for item in ranked if item.score > 0]
    if positives:
        return positives[:limit]
    return ranked[: min(limit, max(minimum, len(ranked)))]


def bullet(label: str, value: Any) -> str:
    if isinstance(value, list):
        value = "、".join(str(item) for item in value if str(item).strip())
    if not value:
        return ""
    return f"  - {label}：{value}\n"


def render_entry(entry: RagEntry, index: int) -> str:
    data = entry.data
    if entry.kind == "短摘录分析":
        title = data.get("title") or data.get("id") or f"excerpt-analysis-{index}"
    else:
        title = primary_text(data) or data.get("id", f"entry-{index}")
    lines = [f"{index}. **{entry.kind}：{title}**\n"]
    if entry.kind == "短摘录分析":
        lines.append(bullet("分析", data.get("analysis") or data.get("usage")))
        lines.append("  - 注意：短摘录只用于学习节奏和动作顺序，正文不得复写原句。\n")
    else:
        lines.append(bullet("含义", data.get("meaning")))
        lines.append(bullet("用法", data.get("usage") or data.get("example")))
    lines.append(bullet("适用场景", data.get("scenes")))
    lines.append(bullet("适用题材", data.get("genres")))
    lines.append(bullet("慎用/禁用", data.get("avoid")))
    lines.append(bullet("匹配理由", entry.reasons))
    risk = data.get("expiry_risk")
    if risk:
        lines.append(bullet("过期风险", risk))
    return "".join(line for line in lines if line)


def render_markdown(
    selected: list[RagEntry],
    query_genres: list[str],
    query_scenes: list[str],
    query_terms: set[str],
    warnings: list[str],
    total_entries: int,
) -> str:
    lines = [
        "【RAG小抄】\n",
        "\n",
        "## 本章匹配方向\n",
        f"- 题材：{'、'.join(query_genres) if query_genres else '未明确，按通用语感处理'}\n",
        f"- 场景：{'、'.join(query_scenes) if query_scenes else '未明确，优先选择通用表达'}\n",
        f"- 关键词：{'、'.join(sorted(query_terms)[:18]) if query_terms else '无'}\n",
        f"- 知识库命中：{len(selected)} / {total_entries}\n",
        "\n",
    ]

    if not selected:
        lines.extend(
            [
                "## 可用表达\n",
                "- 当前知识库没有可用条目。请先把热梗、评论区句子或风格样例放入 `C:\\Users\\xiong\\novel-rag-kb\\inbox`，再整理进 `kb/*.jsonl`。\n",
                "\n",
            ]
        )
    else:
        groups = ["热梗表达", "语感模板", "短摘录分析"]
        for group in groups:
            group_items = [item for item in selected if item.kind == group]
            if not group_items:
                continue
            lines.append(f"## {group}\n")
            for idx, item in enumerate(group_items, start=1):
                lines.append(render_entry(item, idx))
            lines.append("\n")

    lines.extend(
        [
            "## 使用提醒\n",
            "- 每章只自然使用 1-3 处，优先放在吐槽、社死、反击、嘴硬、暧昧拉扯处。\n",
            "- 如果小抄与人物设定、时代背景或章节大纲冲突，优先服从人物和剧情。\n",
            "- 古言、年代文要转译成时代内表达，不直接塞现代互联网词。\n",
            "- 禁止照抄短摘录原句；只学习节奏、动作顺序和情绪推进方式。\n",
        ]
    )
    if warnings:
        lines.append("\n## 知识库提醒\n")
        for warning in warnings:
            lines.append(f"- {warning}\n")
    return "".join(lines)


def render_json(selected: list[RagEntry], warnings: list[str]) -> str:
    payload = {
        "selected": [
            {"kind": item.kind, "score": item.score, "reasons": item.reasons or [], "data": item.data}
            for item in selected
        ],
        "warnings": warnings,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Retrieve a RAG cheat sheet for tomato novel chapter writing.")
    default_root = Path(os.environ.get("NOVEL_RAG_KB", Path.home() / "novel-rag-kb"))
    parser.add_argument("--kb-root", default=str(default_root), help="Knowledge base root. Defaults to ~/novel-rag-kb.")
    parser.add_argument("--core-setting", default="", help="Novel core setting text.")
    parser.add_argument("--core-setting-file", default="", help="UTF-8 file containing core setting.")
    parser.add_argument("--previous", default="", help="Previous chapter summary text.")
    parser.add_argument("--previous-file", default="", help="UTF-8 file containing previous chapter summary.")
    parser.add_argument("--outline", default="", help="Current chapter outline text.")
    parser.add_argument("--outline-file", default="", help="UTF-8 file containing current chapter outline.")
    parser.add_argument("--genre", default="", help="Optional genre tags, e.g. 现言, 古言, 年代.")
    parser.add_argument("--top-k", type=int, default=12, help="Maximum entries to output.")
    parser.add_argument("--min-k", type=int, default=5, help="Minimum fallback entries when matches are sparse.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    core = read_text_arg(args.core_setting, args.core_setting_file)
    previous = read_text_arg(args.previous, args.previous_file)
    outline = read_text_arg(args.outline, args.outline_file)
    if not outline:
        raise SystemExit("需要提供 --outline 或 --outline-file")

    query_text = "\n".join(part for part in [core, previous, outline, args.genre] if part)
    explicit_genres = as_list(args.genre)
    detected_genres = detect_labels(query_text, GENRE_MARKERS)
    query_genres = list(dict.fromkeys(explicit_genres + detected_genres))
    query_scenes = detect_labels(query_text, SCENE_MARKERS)
    query_terms = extract_terms(query_text)

    entries, warnings = load_entries(Path(args.kb_root))
    scored = [score_entry(entry, query_terms, query_genres, query_scenes) for entry in entries]
    selected = choose_entries(scored, max(args.top_k, 1), max(args.min_k, 0))

    if args.format == "json":
        print(render_json(selected, warnings))
    else:
        print(render_markdown(selected, query_genres, query_scenes, query_terms, warnings, len(entries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
