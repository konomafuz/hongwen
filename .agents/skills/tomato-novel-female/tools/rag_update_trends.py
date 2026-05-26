#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update the local novel RAG KB from search APIs, assistant research, or inbox files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_QUERIES = [
    "2026 最新热梗 女频小说 对白 吐槽",
    "2026 小红书 评论区 热梗 口语表达",
    "2026 抖音 评论区 热梗 语录",
    "2026 B站 弹幕 热词 吐槽",
    "番茄小说 女频 现言 评论区 热词",
]

STOP_PHRASES = {
    "最新热梗",
    "热梗",
    "小红书",
    "抖音",
    "微博",
    "B站",
    "番茄小说",
    "评论区",
    "女频小说",
}


def load_env_file(kb_root: Path) -> None:
    env_path = kb_root / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def stable_id(prefix: str, text: str) -> str:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def append_jsonl(path: Path, rows: list[dict[str, Any]], dry_run: bool = False) -> int:
    if not rows:
        return 0
    existing_ids = {str(row.get("id")) for row in read_jsonl(path) if row.get("id")}
    seen_ids = set(existing_ids)
    new_rows: list[dict[str, Any]] = []
    for row in rows:
        row_id = str(row.get("id"))
        if row_id in seen_ids:
            continue
        seen_ids.add(row_id)
        new_rows.append(row)
    if dry_run or not new_rows:
        return len(new_rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        for row in new_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return len(new_rows)


def write_jsonl(path: Path, rows: list[dict[str, Any]], dry_run: bool = False) -> int:
    if dry_run:
        return len(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return len(rows)


def http_json(url: str, *, method: str = "GET", headers: dict[str, str] | None = None, body: dict[str, Any] | None = None) -> dict[str, Any]:
    encoded_body = None
    request_headers = headers or {}
    if body is not None:
        encoded_body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        request_headers = {"Content-Type": "application/json", **request_headers}
    request = urllib.request.Request(url, data=encoded_body, headers=request_headers, method=method)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def search_tavily(query: str, max_results: int) -> list[dict[str, str]]:
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("缺少 TAVILY_API_KEY 环境变量")
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
        "include_answer": False,
        "include_raw_content": False,
    }
    data = http_json("https://api.tavily.com/search", method="POST", body=payload)
    results = []
    for item in data.get("results", []) or []:
        results.append(
            {
                "title": str(item.get("title", "")),
                "url": str(item.get("url", "")),
                "snippet": str(item.get("content", "")),
            }
        )
    return results


def collect_inbox_texts(inbox_dir: Path) -> list[dict[str, str]]:
    notes: list[dict[str, str]] = []
    if not inbox_dir.exists():
        return notes
    for path in sorted(inbox_dir.iterdir()):
        if path.is_dir() or path.suffix.lower() not in {".txt", ".md", ".jsonl"}:
            continue
        if path.suffix.lower() == ".jsonl":
            for row in read_jsonl(path):
                text = " ".join(str(row.get(key, "")) for key in ("phrase", "text", "pattern", "meaning", "usage"))
                if text.strip():
                    notes.append({"title": path.name, "url": "", "snippet": text.strip()})
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for line in content.splitlines():
            line = line.strip(" \t-•#")
            if len(line) >= 4:
                notes.append({"title": path.name, "url": "", "snippet": line})
    return notes


def extract_candidate_phrases(text: str) -> list[str]:
    candidates: list[str] = []
    quoted = re.findall(r"[「『“\"]([^」』”\"]{2,18})[」』”\"]", text)
    candidates.extend(quoted)
    hashtag = re.findall(r"#([\u4e00-\u9fffA-Za-z0-9_]{2,18})", text)
    candidates.extend(hashtag)
    short_chunks = re.findall(r"[\u4e00-\u9fff]{2,10}", text)
    for chunk in short_chunks:
        if any(stop in chunk for stop in STOP_PHRASES):
            continue
        if re.search(r"(离谱|上头|社死|嘴硬|反击|吐槽|发疯|破防|抽象|松弛|癫|爽|尬|谢|尊重)", chunk):
            candidates.append(chunk)
    clean: list[str] = []
    for phrase in candidates:
        phrase = phrase.strip(" ：:，,。.!！？?（）()[]【】")
        if 2 <= len(phrase) <= 18 and phrase not in STOP_PHRASES and phrase not in clean:
            clean.append(phrase)
    return clean[:8]


def note_to_meme_entry(phrase: str, note: dict[str, str], query: str | None, source_type: str) -> dict[str, Any]:
    source = note.get("url") or note.get("title") or source_type
    base = f"{phrase}|{source}|{query or ''}"
    return {
        "id": stable_id("meme-web", base),
        "phrase": phrase,
        "meaning": "待人工确认：由搜索结果或 inbox 素材提取，使用前需要确认语义。",
        "usage": "候选热梗。建议先改写成角色自己的说法，再用于吐槽、反击、社死或内心OS。",
        "scenes": ["吐槽"],
        "genres": ["现言", "校园", "娱乐圈", "职场"],
        "avoid": ["未确认语义前不要直接写入正文", "古言/年代文需转译", "严肃虐点慎用"],
        "expiry_risk": "中",
        "date": today(),
        "source": source,
        "source_type": source_type,
        "query": query or "",
        "needs_review": True,
    }


def note_to_voice_entry(note: dict[str, str], query: str | None, source_type: str) -> dict[str, Any] | None:
    snippet = note.get("snippet", "").strip()
    if len(snippet) < 8:
        return None
    condensed = re.sub(r"\s+", " ", snippet)[:80]
    source = note.get("url") or note.get("title") or source_type
    return {
        "id": stable_id("voice-web", condensed + source),
        "pattern": "候选口语/评论区表达：" + condensed,
        "usage": "待人工确认：可提炼成对白、内心OS或吐槽节奏，正文中不要整句照搬。",
        "example": "",
        "scenes": ["吐槽", "社死", "反击"],
        "genres": ["现言", "校园", "娱乐圈", "职场"],
        "avoid": ["不要照搬搜索结果原句", "不确定来源时只学语气结构"],
        "expiry_risk": "中",
        "date": today(),
        "source": source,
        "source_type": source_type,
        "query": query or "",
        "needs_review": True,
    }


def build_entries(notes: list[dict[str, str]], query: str | None, source_type: str, target: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    meme_rows: list[dict[str, Any]] = []
    voice_rows: list[dict[str, Any]] = []
    for note in notes:
        note_query = query or note.get("query") or ""
        text = " ".join([note.get("title", ""), note.get("snippet", "")])
        phrases = extract_candidate_phrases(text)
        if target in {"auto", "memes"}:
            for phrase in phrases:
                meme_rows.append(note_to_meme_entry(phrase, note, note_query, source_type))
        if target in {"auto", "voice"}:
            voice = note_to_voice_entry(note, note_query, source_type)
            if voice:
                voice_rows.append(voice)
    return meme_rows, voice_rows


def write_report(
    kb_root: Path,
    title: str,
    notes: list[dict[str, str]],
    entries_count: dict[str, int],
    meme_rows: list[dict[str, Any]],
    voice_rows: list[dict[str, Any]],
    dry_run: bool,
) -> Path | None:
    if dry_run:
        return None
    report_dir = kb_root / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"rag-update-{timestamp()}.md"
    lines = [
        f"# {title}\n\n",
        f"- 日期：{today()}\n",
        f"- 候选热梗条目：{entries_count.get('memes', 0)}\n",
        f"- 候选语感条目：{entries_count.get('voice', 0)}\n\n",
        "## 候选热梗条目\n\n",
    ]
    if meme_rows:
        for index, row in enumerate(meme_rows, start=1):
            lines.append(f"{index}. **{row.get('phrase', '').strip() or row.get('id', '')}**\n")
            lines.append(f"   - Query：{row.get('query', '')}\n")
            lines.append(f"   - Source：{row.get('source', '')}\n")
            lines.append(f"   - 用法：{row.get('usage', '')}\n")
            lines.append(f"   - 状态：{'需人工确认' if row.get('needs_review') else '可用'}\n")
    else:
        lines.append("- 无\n")
    lines.extend([
        "\n",
        "## 候选语感条目\n\n",
    ])
    if voice_rows:
        for index, row in enumerate(voice_rows, start=1):
            lines.append(f"{index}. **{row.get('id', '')}**\n")
            lines.append(f"   - Query：{row.get('query', '')}\n")
            lines.append(f"   - Source：{row.get('source', '')}\n")
            lines.append(f"   - Pattern：{row.get('pattern', '')}\n")
            lines.append(f"   - 状态：{'需人工确认' if row.get('needs_review') else '可用'}\n")
    else:
        lines.append("- 无\n")
    lines.extend([
        "\n",
        "## 原始来源摘要\n\n",
    ])
    for index, note in enumerate(notes, start=1):
        lines.append(f"{index}. **{note.get('title', '').strip() or 'Untitled'}**\n")
        if note.get("url"):
            lines.append(f"   - URL：{note['url']}\n")
        if note.get("snippet"):
            lines.append(f"   - 摘要：{note['snippet'][:300]}\n")
    path.write_text("".join(lines), encoding="utf-8")
    return path


def default_candidate_path(kb_root: Path) -> Path:
    return kb_root / "candidates" / f"rag-candidates-{timestamp()}.jsonl"


def parse_queries(args: argparse.Namespace) -> list[str]:
    queries: list[str] = []
    queries.extend(args.query or [])
    if args.query_file:
        content = Path(args.query_file).read_text(encoding="utf-8")
        queries.extend(line.strip() for line in content.splitlines() if line.strip())
    if args.default_queries:
        queries.extend(DEFAULT_QUERIES)
    return list(dict.fromkeys(queries))


def main() -> int:
    parser = argparse.ArgumentParser(description="Update local novel RAG KB from search APIs, assistant research, or inbox files.")
    default_root = Path(os.environ.get("NOVEL_RAG_KB", Path.home() / "novel-rag-kb"))
    parser.add_argument("--kb-root", default=str(default_root), help="Knowledge base root. Defaults to ~/novel-rag-kb.")
    parser.add_argument("--provider", choices=["tavily"], default="tavily", help="Search API provider.")
    parser.add_argument("--query", action="append", help="Search query. Can be repeated.")
    parser.add_argument("--query-file", help="UTF-8 file with one search query per line.")
    parser.add_argument("--default-queries", action="store_true", help="Use built-in hot-meme search queries.")
    parser.add_argument("--from-inbox", action="store_true", help="Ingest text/md/jsonl files from kb_root/inbox.")
    parser.add_argument("--assistant-report-file", help="Markdown/text report produced by manual assistant web research.")
    parser.add_argument("--max-results", type=int, default=5, help="Search results per query.")
    parser.add_argument("--target", choices=["auto", "memes", "voice"], default="auto", help="Which KB files to update.")
    parser.add_argument("--candidate-output", help="Write raw candidate entries to this JSONL file.")
    parser.add_argument("--staging-only", action="store_true", help="Write candidates/report only; do not append to approved KB files.")
    parser.add_argument("--dry-run", action="store_true", help="Print summary without writing KB files.")
    args = parser.parse_args()

    kb_root = Path(args.kb_root)
    load_env_file(kb_root)
    kb_dir = kb_root / "kb"
    all_notes: list[dict[str, str]] = []

    queries = parse_queries(args)
    for query in queries:
        results = search_tavily(query, args.max_results)
        for result in results:
            result["query"] = query
        all_notes.extend(results)

    if args.from_inbox:
        all_notes.extend(collect_inbox_texts(kb_root / "inbox"))

    if args.assistant_report_file:
        path = Path(args.assistant_report_file)
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            line = line.strip(" \t-•#")
            if len(line) >= 4:
                all_notes.append({"title": path.name, "url": "", "snippet": line})

    if not all_notes:
        print("没有可处理的输入。请提供 --query、--default-queries、--from-inbox 或 --assistant-report-file。", file=sys.stderr)
        return 2

    meme_rows, voice_rows = build_entries(all_notes, None, "search/inbox", args.target)
    candidate_rows: list[dict[str, Any]] = []
    for row in meme_rows:
        candidate_rows.append({"target_file": "memes.jsonl", **row})
    for row in voice_rows:
        candidate_rows.append({"target_file": "voice_patterns.jsonl", **row})

    candidate_path = Path(args.candidate_output) if args.candidate_output else default_candidate_path(kb_root)
    candidates_written = write_jsonl(candidate_path, candidate_rows, dry_run=args.dry_run)

    if args.staging_only:
        memes_added = 0
        voice_added = 0
    else:
        memes_added = append_jsonl(kb_dir / "memes.jsonl", meme_rows, dry_run=args.dry_run)
        voice_added = append_jsonl(kb_dir / "voice_patterns.jsonl", voice_rows, dry_run=args.dry_run)
    report_path = write_report(
        kb_root,
        "Novel RAG Trend Update",
        all_notes,
        {"memes": memes_added, "voice": voice_added},
        meme_rows,
        voice_rows,
        args.dry_run,
    )

    print(json.dumps(
        {
            "notes_seen": len(all_notes),
            "candidate_memes": len(meme_rows),
            "candidate_voice_patterns": len(voice_rows),
            "memes_to_add" if args.dry_run else "memes_added": memes_added,
            "voice_patterns_to_add" if args.dry_run else "voice_patterns_added": voice_added,
            "dry_run": args.dry_run,
            "report": str(report_path) if report_path else "",
            "candidate_output": str(candidate_path),
            "candidates_written": candidates_written,
            "staging_only": args.staging_only,
            "kb_root": str(kb_root),
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
