from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
class TaskLog(BaseModel):
    __tablename__ = "task_logs"
    
    episode_id = Column(
        Integer,
        ForeignKey("episodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    task_type = Column(String(100), nullable=False, index=True)  # 任务类型
    status = Column(String(50), nullable=False, index=True)  # 任务状态
    message = Column(Text)
    details = Column(Text)  # 详细日志（JSON格式）
    execution_time = Column(Integer)  # 执行时间（毫秒）
    
    # 关系定义
    episode = relationship(
        "Episode",
        back_populates="task_logs",
        lazy="selectin"
    )
    
    def __repr__(self):
        return f"<TaskLog(id={self.id}, task_type='{self.task_type}', status='{self.status}')>"