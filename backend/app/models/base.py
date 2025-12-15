from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from datetime import datetime

# 使用 async SQLAlchemy 的 declarative base
Base = declarative_base()

class BaseModel(Base):
    """
    所有模型的基类，包含通用字段
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        """将模型实例转换为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}