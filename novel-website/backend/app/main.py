from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api import (
    auth_router, users_router, projects_router,
    settings_router, tags_router, volumes_router,
    chapters_router, ai_router, export_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(settings_router)
app.include_router(tags_router)
app.include_router(volumes_router)
app.include_router(chapters_router)
app.include_router(ai_router)
app.include_router(export_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": settings.VERSION}