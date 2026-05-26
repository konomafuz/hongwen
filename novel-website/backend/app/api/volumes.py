from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.models.project import Project, Volume
from app.schemas.project import VolumeCreate, VolumeUpdate, VolumeResponse
from app.core.deps import get_current_active_user

router = APIRouter(prefix="/api/projects/{project_id}/volumes", tags=["Volumes"])


async def _get_project(project_id: int, user_id: int, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project or project.user_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("", response_model=list[VolumeResponse])
async def list_volumes(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project(project_id, current_user.id, db)
    result = await db.execute(
        select(Volume)
        .where(Volume.project_id == project_id)
        .order_by(Volume.volume_number)
    )
    return [VolumeResponse.model_validate(v) for v in result.scalars().all()]


@router.post("", response_model=VolumeResponse, status_code=status.HTTP_201_CREATED)
async def create_volume(
    project_id: int,
    data: VolumeCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project(project_id, current_user.id, db)
    volume = Volume(
        project_id=project_id,
        volume_number=data.volume_number,
        volume_title=data.volume_title,
        summary=data.summary,
        plot_arc=data.plot_arc,
        chapters_estimated=data.chapters_estimated,
    )
    db.add(volume)
    await db.flush()
    await db.refresh(volume)
    return VolumeResponse.model_validate(volume)


@router.put("/{volume_id}", response_model=VolumeResponse)
async def update_volume(
    project_id: int,
    volume_id: int,
    data: VolumeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project(project_id, current_user.id, db)
    result = await db.execute(
        select(Volume).where(Volume.id == volume_id, Volume.project_id == project_id)
    )
    volume = result.scalar_one_or_none()
    if not volume:
        raise HTTPException(status_code=404, detail="Volume not found")

    if data.volume_title is not None:
        volume.volume_title = data.volume_title
    if data.summary is not None:
        volume.summary = data.summary
    if data.plot_arc is not None:
        volume.plot_arc = data.plot_arc
    if data.chapters_estimated is not None:
        volume.chapters_estimated = data.chapters_estimated

    db.add(volume)
    await db.flush()
    await db.refresh(volume)
    return VolumeResponse.model_validate(volume)


@router.delete("/{volume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_volume(
    project_id: int,
    volume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project(project_id, current_user.id, db)
    result = await db.execute(
        select(Volume).where(Volume.id == volume_id, Volume.project_id == project_id)
    )
    volume = result.scalar_one_or_none()
    if not volume:
        raise HTTPException(status_code=404, detail="Volume not found")
    await db.delete(volume)