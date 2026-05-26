from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# --- Project ---
class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    mode: str = Field(default="guide", pattern="^(guide|expert)$")


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = Field(None, pattern="^(drafting|completed)$")


class ProjectResponse(BaseModel):
    id: int
    user_id: int
    title: str
    mode: str
    status: str
    word_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Settings ---
class SettingCreate(BaseModel):
    genre: Optional[str] = None
    world_view: Optional[str] = None
    characters: Optional[dict] = None
    relationship_map: Optional[dict] = None
    conflict_system: Optional[dict] = None
    raw_content: Optional[str] = None


class SettingUpdate(BaseModel):
    genre: Optional[str] = None
    world_view: Optional[str] = None
    characters: Optional[dict] = None
    relationship_map: Optional[dict] = None
    conflict_system: Optional[dict] = None
    raw_content: Optional[str] = None


class SettingResponse(BaseModel):
    id: int
    project_id: int
    genre: Optional[str] = None
    world_view: Optional[str] = None
    characters: Optional[dict] = None
    relationship_map: Optional[dict] = None
    conflict_system: Optional[dict] = None
    raw_content: Optional[str] = None
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Tags ---
class TagCreate(BaseModel):
    tags: Optional[list] = None
    synopsis_versions: Optional[list] = None
    recommendation: Optional[str] = None


class TagUpdate(BaseModel):
    tags: Optional[list] = None
    synopsis_versions: Optional[list] = None
    recommendation: Optional[str] = None


class TagResponse(BaseModel):
    id: int
    project_id: int
    tags: Optional[list] = None
    synopsis_versions: Optional[list] = None
    recommendation: Optional[str] = None
    status: Optional[str] = None
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Volume ---
class VolumeCreate(BaseModel):
    volume_number: int = Field(..., ge=1)
    volume_title: str = Field(..., min_length=1, max_length=200)
    summary: Optional[str] = None
    plot_arc: Optional[dict] = None
    chapters_estimated: int = Field(default=0, ge=0)


class VolumeUpdate(BaseModel):
    volume_title: Optional[str] = Field(None, min_length=1, max_length=200)
    summary: Optional[str] = None
    plot_arc: Optional[dict] = None
    chapters_estimated: Optional[int] = Field(None, ge=0)


class VolumeResponse(BaseModel):
    id: int
    project_id: int
    volume_number: int
    volume_title: str
    summary: Optional[str] = None
    plot_arc: Optional[dict] = None
    chapters_estimated: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Chapter ---
class ChapterCreate(BaseModel):
    volume_id: Optional[int] = None
    chapter_number: int = Field(..., ge=1)
    title: str = Field(..., min_length=1, max_length=200)
    outline: Optional[str] = None


class ChapterUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    outline: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(outline|drafting|reviewing|completed)$")


class ChapterResponse(BaseModel):
    id: int
    project_id: int
    volume_id: Optional[int] = None
    chapter_number: int
    title: str
    outline: Optional[str] = None
    content: Optional[str] = None
    word_count: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}