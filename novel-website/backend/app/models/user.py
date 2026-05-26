import enum
from datetime import datetime
from sqlalchemy import String, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class UserRole(str, enum.Enum):
    FREE = "free"
    VIP = "vip"
    PREMIUM = "premium"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.FREE, nullable=False)
    daily_chapter_count: Mapped[int] = mapped_column(default=0, nullable=False)
    last_chapter_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"