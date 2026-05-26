from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.models.project import Project, ProjectSettings
from app.schemas.project import SettingCreate, SettingUpdate, SettingResponse
from app.core.deps import get_current_active_user

router = APIRouter(prefix="/api/projects/{project_id}/settings", tags=["Settings"])


async def _get_project(project_id: int, user_id: int, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project or project.user_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("", response_model=SettingResponse)
async def get_settings(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project(project_id, current_user.id, db)
    result = await db.execute(select(ProjectSettings).where(ProjectSettings.project_id == project_id))
    settings = result.scalar_one_or_none()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return SettingResponse.model_validate(settings)


@router.post("", response_model=SettingResponse, status_code=201)
async def create_settings(
    project_id: int,
    data: SettingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project(project_id, current_user.id, db)

    # Check if settings already exist
    result = await db.execute(select(ProjectSettings).where(ProjectSettings.project_id == project_id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Settings already exist, use PUT to update")

    settings = ProjectSettings(
        project_id=project_id,
        genre=data.genre,
        world_view=data.world_view,
        characters=data.characters,
        relationship_map=data.relationship_map,
        conflict_system=data.conflict_system,
        raw_content=data.raw_content,
    )
    db.add(settings)
    await db.flush()
    await db.refresh(settings)
    return SettingResponse.model_validate(settings)


@router.put("", response_model=SettingResponse)
async def update_settings(
    project_id: int,
    data: SettingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project(project_id, current_user.id, db)
    result = await db.execute(select(ProjectSettings).where(ProjectSettings.project_id == project_id))
    settings = result.scalar_one_or_none()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    if data.genre is not None:
        settings.genre = data.genre
    if data.world_view is not None:
        settings.world_view = data.world_view
    if data.characters is not None:
        settings.characters = data.characters
    if data.relationship_map is not None:
        settings.relationship_map = data.relationship_map
    if data.conflict_system is not None:
        settings.conflict_system = data.conflict_system
    if data.raw_content is not None:
        settings.raw_content = data.raw_content

    db.add(settings)
    await db.flush()
    await db.refresh(settings)
    return SettingResponse.model_validate(settings)