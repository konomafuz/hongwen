from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.ai import AIGenerateRequest, AIGenerateResponse
from app.core.deps import get_current_active_user
from app.services.ai_service import generate_with_deepseek

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/generate", response_model=AIGenerateResponse)
async def generate_content(
    data: AIGenerateRequest,
    current_user: User = Depends(get_current_active_user),
):
    try:
        content, usage = await generate_with_deepseek(
            prompt=data.prompt,
            context=data.context,
            temperature=data.temperature,
            max_tokens=data.max_tokens,
            style=data.style,
            mode=data.mode,
        )
        return AIGenerateResponse(content=content, usage=usage)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.post("/draft", response_model=AIGenerateResponse)
async def draft_chapter(
    data: AIGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a full chapter draft."""
    try:
        content, usage = await generate_with_deepseek(
            prompt=data.prompt,
            context=data.context,
            temperature=data.temperature or 0.8,
            max_tokens=data.max_tokens or 4096,
            style=data.style or "default",
            mode="draft",
        )
        return AIGenerateResponse(content=content, usage=usage)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Draft generation failed: {str(e)}")


@router.get("/rag")
async def search_rag(
    q: str,
    current_user: User = Depends(get_current_active_user),
):
    """RAG search for style references."""
    from app.services.rag_service import search_rag
    try:
        results = await search_rag(q)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG search failed: {str(e)}")