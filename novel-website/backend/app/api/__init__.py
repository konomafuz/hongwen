from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.projects import router as projects_router
from app.api.settings import router as settings_router
from app.api.tags import router as tags_router
from app.api.volumes import router as volumes_router
from app.api.chapters import router as chapters_router
from app.api.ai import router as ai_router
from app.api.export import router as export_router

__all__ = [
    "auth_router", "users_router", "projects_router",
    "settings_router", "tags_router", "volumes_router",
    "chapters_router", "ai_router", "export_router",
]