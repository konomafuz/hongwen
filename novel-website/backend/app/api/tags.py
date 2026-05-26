from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.models.project import Project, ProjectTags
from app.schemas.project import TagCreate, TagUpdate, TagResponse
from app.core.deps import get_current_active_user

router = APIRouter(prefix="/api/projects/{project_id}/tags", tags=["Tags"])


@router.get("", response_model=TagResponse)
async def get_tags(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project(project_id, current_user.id, db)
    result = await db.execute(select(ProjectTags).where(ProjectTags.project_id == project_id))
    tags = result.scalar_one_or_none()
    if not tags:
        raise HTTPException(status_code=404, detail="Tags not found")
    return TagResponse.model_validate(tags)


@router.post("", response_model=TagResponse, status_code=201)
async def create_tags(
    project_id: int,
    data: TagCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project(project_id, current_user.id, db)
    result = await db.execute(select(ProjectTags).where(ProjectTags.project_id == project_id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Tags already exist, use PUT to update")

    tags = ProjectTags(
        project_id=project_id,
        tags=data.tags,
        synopsis_versions=data.synopsis_versions,
        recommendation=data.recommendation,
        status="draft",
    )
    db.add(tags)
    await db.flush()
    await db.refresh(tags)
    return TagResponse.model_validate(tags)


@router.put("", response_model=TagResponse)
async def update_tags(
    project_id: int,
    data: TagUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project(project_id, current_user.id, db)
    result = await db.execute(select(ProjectTags).where(ProjectTags.project_id == project_id))
    tags = result.scalar_one_or_none()
    if not tags:
        raise HTTPException(status_code=404, detail="Tags not found")

    if data.tags is not None:
        tags.tags = data.tags
    if data.synopsis_versions is not None:
        tags.synopsis_versions = data.synopsis_versions
    if data.recommendation is not None:
        tags.recommendation = data.recommendation

    db.add(tags)
    await db.flush()
    await db.refresh(tags)
    return TagResponse.model_validate(tags)


async def _get_project(project_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project or project.user_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project