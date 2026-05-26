import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Enum, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ProjectStatus(str, enum.Enum):
    DRAFTING = "drafting"
    COMPLETED = "completed"


class ProjectMode(str, enum.Enum):
    GUIDE = "guide"
    EXPERT = "expert"


class ChapterStatus(str, enum.Enum):
    OUTLINE = "outline"
    DRAFTING = "drafting"
    REVIEWING = "reviewing"
    COMPLETED = "completed"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    mode: Mapped[ProjectMode] = mapped_column(Enum(ProjectMode), default=ProjectMode.GUIDE, nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.DRAFTING, nullable=False)
    word_count: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    owner = relationship("User", back_populates="projects")
    settings = relationship("ProjectSettings", back_populates="project", uselist=False, cascade="all, delete-orphan")
    tags = relationship("ProjectTags", back_populates="project", uselist=False, cascade="all, delete-orphan")
    volumes = relationship("Volume", back_populates="project", cascade="all, delete-orphan", order_by="Volume.volume_number")
    chapters = relationship("Chapter", back_populates="project", cascade="all, delete-orphan", order_by="Chapter.chapter_number")

    def __repr__(self):
        return f"<Project(id={self.id}, title={self.title})>"


class ProjectSettings(Base):
    __tablename__ = "project_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), unique=True, nullable=False)
    genre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    world_view: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    characters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    relationship_map: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    conflict_system: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    raw_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    project = relationship("Project", back_populates="settings")


class ProjectTags(Base):
    __tablename__ = "project_tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), unique=True, nullable=False)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    synopsis_versions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    project = relationship("Project", back_populates="tags")


class Volume(Base):
    __tablename__ = "project_volumes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    volume_number: Mapped[int] = mapped_column(Integer, nullable=False)
    volume_title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    plot_arc: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    chapters_estimated: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    project = relationship("Project", back_populates="volumes")


class Chapter(Base):
    __tablename__ = "project_chapters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    volume_id: Mapped[Optional[int]] = mapped_column(ForeignKey("project_volumes.id"), nullable=True, index=True)
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    outline: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    word_count: Mapped[int] = mapped_column(default=0, nullable=False)
    status: Mapped[ChapterStatus] = mapped_column(Enum(ChapterStatus), default=ChapterStatus.OUTLINE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    project = relationship("Project", back_populates="chapters")


class ProjectVersion(Base):
    __tablename__ = "project_versions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    step_name: Mapped[str] = mapped_column(String(100), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)