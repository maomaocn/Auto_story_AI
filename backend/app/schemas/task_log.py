from typing import List, Optional
from .base import TimestampSchema,BaseSchema

# 任务日志基础Schema
class TaskLogBase(TimestampSchema):
    task_type: str
    status: str
    message: Optional[str] = None

# 创建任务日志
class TaskLogCreate(BaseSchema):
    episode_id: int
    task_type: str
    status: str
    message: Optional[str] = None
    details: Optional[dict] = None
    execution_time: Optional[int] = None

# 任务日志返回
class TaskLogRead(TaskLogBase):
    id: int
    episode_id: int
    details: Optional[dict] = None
    execution_time: Optional[int] = None

# 批量创建任务日志
class TaskLogBatchCreate(BaseSchema):
    episode_id: int
    logs: List[TaskLogCreate]