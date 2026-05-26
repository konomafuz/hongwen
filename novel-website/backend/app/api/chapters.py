from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.models.project import Project, Chapter, ChapterStatus
from app.schemas.project import ChapterCreate, ChapterUpdate, ChapterResponse
from app.core.deps import get_current_active_user

router = APIRouter(prefix="/api/projects/{project_id}/chapters", tags=["Chapters"])


async def _get_project(project_id: int, user_id: int, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project or project.user_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("", response_model=list[ChapterResponse])
async def list_chapters(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project(project_id, current_user.id, db)
    result = await db.execute(
        select(Chapter)
        .where(Chapter.project_id == project_id)
        .order_by(Chapter.chapter_number)
    )
    return [ChapterResponse.model_validate(c) for c in result.scalars().all()]


@router.post("", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
async def create_chapter(
    project_id: int,
    data: ChapterCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project(project_id, current_user.id, db)

    # Validate volume belongs to project if specified
    if data.volume_id:
        v_result = await db.execute(
            select(Volume).where(Volume.id == data.volume_id, Volume.project_id == project_id)
        )
        if not v_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Volume does not belong to this project")

    chapter = Chapter(
        project_id=project_id,
        volume_id=data.volume_id,
        chapter_number=data.chapter_number,
        title=data.title,
        outline=data.outline,
        status=ChapterStatus.OUTLINE,
    )
    db.add(chapter)
    await db.flush()
    await db.refresh(chapter)
    return ChapterResponse.model_validate(chapter)


@router.get("/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    project_id: int,
    chapter_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project(project_id, current_user.id, db)
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.project_id == project_id)
    )
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return ChapterResponse.model_validate(chapter)


@router.put("/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    project_id: int,
    chapter_id: int,
    data: ChapterUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project(project_id, current_user.id, db)
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.project_id == project_id)
    )
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    if data.title is not None:
        chapter.title = data.title
    if data.outline is not None:
        chapter.outline = data.outline
    if data.content is not None:
        chapter.content = data.content
        chapter.word_count = len(data.content.replace(" ", "").replace("\n", ""))
    if data.status is not None:
        chapter.status = ChapterStatus(data.status)

    db.add(chapter)
    await db.flush()
    await db.refresh(chapter)
    return ChapterResponse.model_validate(chapter)


@router.delete("/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(
    project_id: int,
    chapter_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project(project_id, current_user.id, db)
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.project_id == project_id)
    )
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    await db.delete(chapter)


# Import for type hint
from app.models.project import Volume