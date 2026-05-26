from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.models.project import Project, Chapter
from app.schemas.export import ExportRequest
from app.core.deps import get_current_active_user
from app.services.export_service import export_to_word
import os

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.post("/word")
async def export_word(
    data: ExportRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Export project to Word document."""
    # Verify project ownership
    result = await db.execute(select(Project).where(Project.id == data.project_id))
    project = result.scalar_one_or_none()
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    # Fetch all chapters
    ch_result = await db.execute(
        select(Chapter)
        .where(Chapter.project_id == data.project_id)
        .order_by(Chapter.chapter_number)
    )
    chapters = ch_result.scalars().all()

    filepath = await export_to_word(project, chapters, include_outline=data.include_outline)
    filename = os.path.basename(filepath)

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )