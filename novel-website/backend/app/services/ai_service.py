import httpx
from typing import Optional
from app.config import settings

SYSTEM_PROMPTS = {
    "setting": "你是一位资深女频网文编辑，帮助作者构建完整的故事核心设定。请根据用户的需求，生成详细的世界观、人物设定、感情线和冲突体系。",
    "tag": "你是一位网文市场分析师，擅长为小说打标签和撰写吸睛简介。生成热门标签、多版本简介和推荐语。",
    "volume": "你是一位网文结构师，擅长规划小说的分卷结构和剧情走向。生成3-5卷的分卷大纲。",
    "chapter": "你是一位网文细纲专家，擅长为每一章撰写详细的章节大纲。",
    "draft": "你是一位女频网文作家，擅长创作1800-2200字的网文章节。注重人物对话、心理描写和情感冲突。",
    "polish": "你是一位网文资深编辑，擅长对已有正文进行润色和优化，保持文风一致。",
    "continue": "你是一位女频网文作家，擅长根据前文续写章节，保持故事连贯性和文风一致。",
}


def _get_provider_config():
    """根据 AI_PROVIDER 配置获取对应的 API 参数"""
    provider = settings.AI_PROVIDER

    if provider == "deepseek":
        return {
            "api_key": settings.DEEPSEEK_API_KEY,
            "api_base": settings.DEEPSEEK_API_BASE,
            "model": settings.DEEPSEEK_MODEL,
        }

    if provider == "volcengine":
        return {
            "api_key": settings.VOLCENGINE_API_KEY,
            "api_base": settings.VOLCENGINE_API_BASE,
            "model": settings.VOLCENGINE_MODEL,
        }

    if provider == "openai":
        return {
            "api_key": settings.OPENAI_API_KEY,
            "api_base": settings.OPENAI_API_BASE or "https://api.openai.com",
            "model": settings.OPENAI_MODEL,
        }

    # custom — 使用 OpenAI 兼容字段自定义
    return {
        "api_key": settings.OPENAI_API_KEY,
        "api_base": settings.OPENAI_API_BASE,
        "model": settings.OPENAI_MODEL,
    }


async def generate_with_deepseek(
    prompt: str,
    context: Optional[str] = None,
    temperature: float = 0.8,
    max_tokens: int = 4096,
    style: Optional[str] = None,
    mode: str = "draft",
):
    """AI 生成入口。根据 AI_PROVIDER 配置自动选择模型。"""
    cfg = _get_provider_config()
    messages = build_messages(prompt, context, mode)

    api_key = cfg["api_key"]
    if not api_key:
        raise ValueError(
            f"AI_PROVIDER 设置为 '{settings.AI_PROVIDER}'，"
            "但未配置对应的 API Key。请在 .env 中设置。"
        )

    api_base = cfg["api_base"]
    model = cfg["model"]

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{api_base}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage")
    return content, usage


def build_messages(prompt: str, context: Optional[str], mode: str = "draft") -> list:
    system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["draft"])
    messages = [{"role": "system", "content": system_prompt}]

    if context:
        messages.append({"role": "user", "content": f"参考上下文：\n{context}\n\n---\n\n{prompt}"})
    else:
        messages.append({"role": "user", "content": prompt})

    return messages