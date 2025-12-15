from typing import Optional, List
from .base import TimestampSchema,BaseSchema
from .task_log import TaskLogRead
import datetime

# 剧集基础Schema
class EpisodeBase(TimestampSchema):
    episode_number: int
    title: str
    script: Optional[str] = None

# 创建剧集
class EpisodeCreate(BaseSchema):
    project_id: int
    episode_number: int
    title: str
    script: Optional[str] = None

# 更新剧集
class EpisodeUpdate(BaseSchema):
    title: Optional[str] = None
    script: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    video_path: Optional[str] = None
    video_duration: Optional[int] = None
    thumbnail_path: Optional[str] = None

# 剧集返回（完整信息）
class EpisodeRead(EpisodeBase):
    id: int
    project_id: int
    status: str
    progress: int
    video_path: Optional[str] = None
    video_duration: Optional[int] = None
    thumbnail_path: Optional[str] = None
    task_logs: List[TaskLogRead] = []
    
    class Config:
        from_attributes = True

# 剧集返回（简单信息）
class EpisodeSimple(BaseSchema):
    id: int
    episode_number: int
    title: str
    status: str
    progress: int
    created_at: datetime

# 剧集状态更新
class EpisodeStatusUpdate(BaseSchema):
    status: str
    progress: Optional[int] = None
    message: Optional[str] = None

# 剧集生成请求
class EpisodeGenerateRequest(BaseSchema):
    regenerate: bool = False  # 是否重新生成