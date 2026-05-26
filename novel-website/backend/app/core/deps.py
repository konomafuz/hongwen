from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole
from app.models.project import Project
from datetime import date

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


async def check_project_owner(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")
    return project


async def check_daily_limit(current_user: User = Depends(get_current_active_user)) -> None:
    today = date.today()
    if current_user.last_chapter_date and current_user.last_chapter_date.date() == today:
        daily_count = current_user.daily_chapter_count
    else:
        daily_count = 0

    limits = {
        UserRole.FREE: 2,
        UserRole.VIP: 50,
        UserRole.PREMIUM: 200,
    }
    limit = limits.get(current_user.role, 2)

    if daily_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily chapter limit reached ({limit}/{limit})",
        )