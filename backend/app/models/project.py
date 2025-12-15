from sqlalchemy import Column, String, Text, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class ProjectStatus(str, enum.Enum):
    """项目状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Project(BaseModel):
    __tablename__ = "projects"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(
        Enum(ProjectStatus),
        default=ProjectStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # 关系定义
    episodes = relationship(
        "Episode",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin"  # 使用selectin加载策略，适合异步
    )
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status.value}')>"