from typing import Optional, List
from .base import TimestampSchema,BaseSchema
from .episode import EpisodeRead
import datetime
# 项目基础Schema
class ProjectBase(TimestampSchema):
    name: str
    description: Optional[str] = None

# 创建项目
class ProjectCreate(BaseSchema):
    name: str
    description: Optional[str] = None

# 更新项目
class ProjectUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

# 项目返回（完整信息）
class ProjectRead(ProjectBase):
    id: int
    status: str
    episodes: List[EpisodeRead] = []
    
    class Config:
        from_attributes = True

# 项目返回（简单信息，用于列表）
class ProjectSimple(BaseSchema):
    id: int
    name: str
    description: Optional[str] = None
    status: str
    created_at: datetime

# 项目统计
class ProjectStats(BaseSchema):
    total_episodes: int
    completed_episodes: int
    processing_episodes: int
    failed_episodes: int
    total_video_duration: Optional[int] = None  # 总视频时长（秒）