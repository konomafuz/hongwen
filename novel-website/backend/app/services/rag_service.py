from typing import Any
import json
import os


KNOWLEDGE_BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "knowledge_base",
)


async def search_rag(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Search RAG knowledge base for style references."""
    results = []
    kb_dir = KNOWLEDGE_BASE_DIR

    if not os.path.exists(kb_dir):
        return [{"message": "知识库目录不存在，请在项目根目录创建 knowledge_base/ 目录并放入素材文件"}]

    for fname in os.listdir(kb_dir):
        if fname.endswith((".md", ".txt", ".json")):
            fpath = os.path.join(kb_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                # Simple keyword matching
                if query.lower() in content.lower():
                    results.append({
                        "filename": fname,
                        "content": content[:1000] + ("..." if len(content) > 1000 else ""),
                        "match_type": "keyword",
                    })
                if len(results) >= limit:
                    break
            except Exception:
                continue

    # If no keyword matches, return a sample of available files
    if not results:
        for fname in list(os.listdir(kb_dir))[:limit]:
            if fname.endswith((".md", ".txt", ".json")):
                fpath = os.path.join(kb_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    results.append({
                        "filename": fname,
                        "content": content[:500] + ("..." if len(content) > 500 else ""),
                        "match_type": "sample",
                    })
                except Exception:
                    continue

    return results