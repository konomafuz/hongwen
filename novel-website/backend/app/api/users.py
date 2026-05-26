from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.schemas.user import UserResponse, UserUpdate
from app.core.deps import get_current_active_user

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_active_user)):
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if data.nickname is not None:
        current_user.nickname = data.nickname
    db.add(current_user)
    await db.flush()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.get("/me/project-count")
async def get_project_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.user_id == current_user.id))
    projects = result.scalars().all()
    return {"count": len(projects), "total_word_count": sum(p.word_count for p in projects)}