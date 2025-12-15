from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class EpisodeStatus(str, enum.Enum):
    """剧集状态枚举"""
    PENDING = "pending"
    GENERATING_SCRIPT = "generating_script"
    GENERATING_IMAGES = "generating_images"
    GENERATING_AUDIO = "generating_audio"
    ADDING_SUBTITLES = "adding_subtitles"
    COMPOSING_VIDEO = "composing_video"
    COMPLETED = "completed"
    FAILED = "failed"

class Episode(BaseModel):
    __tablename__ = "episodes"
    
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    episode_number = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    script = Column(Text)
    status = Column(
        Enum(EpisodeStatus),
        default=EpisodeStatus.PENDING,
        nullable=False,
        index=True
    )
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    video_path = Column(String(500))
    video_duration = Column(Integer)  # 视频时长（秒）
    thumbnail_path = Column(String(500))  # 缩略图路径
    
    # 关系定义
    project = relationship(
        "Project",
        back_populates="episodes",
        lazy="selectin"
    )
    task_logs = relationship(
        "TaskLog",
        back_populates="episode",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="TaskLog.created_at.desc()"
    )
    
    def __repr__(self):
        return f"<Episode(id={self.id}, title='{self.title}', status='{self.status.value}', progress={self.progress}%)>"
    
    @property
    def is_completed(self) -> bool:
        """检查是否完成"""
        return self.status == EpisodeStatus.COMPLETED
    
    @property
    def is_processing(self) -> bool:
        """检查是否正在处理"""
        processing_statuses = [
            EpisodeStatus.GENERATING_SCRIPT,
            EpisodeStatus.GENERATING_IMAGES,
            EpisodeStatus.GENERATING_AUDIO,
            EpisodeStatus.ADDING_SUBTITLES,
            EpisodeStatus.COMPOSING_VIDEO
        ]
        return self.status in processing_statuses