from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.models.project import Project, ProjectStatus, ProjectMode
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.core.deps import get_current_active_user

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(Project.updated_at.desc())
    )
    return [ProjectResponse.model_validate(p) for p in result.scalars().all()]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Check free user project limit
    if current_user.role.value == "free":
        result = await db.execute(select(Project).where(Project.user_id == current_user.id))
        existing = result.scalars().all()
        if len(existing) >= 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Free users can only create 1 project. Upgrade to VIP for unlimited projects.",
            )

    project = Project(
        user_id=current_user.id,
        title=data.title,
        mode=ProjectMode(data.mode),
        status=ProjectStatus.DRAFTING,
    )
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if data.title is not None:
        project.title = data.title
    if data.status is not None:
        project.status = ProjectStatus(data.status)

    db.add(project)
    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    await db.delete(project)


@router.post("/{project_id}/duplicate", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    original = result.scalar_one_or_none()
    if not original or original.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    new_project = Project(
        user_id=current_user.id,
        title=f"{original.title} (副本)",
        mode=original.mode,
        status=ProjectStatus.DRAFTING,
    )
    db.add(new_project)
    await db.flush()
    await db.refresh(new_project)
    return ProjectResponse.model_validate(new_project)