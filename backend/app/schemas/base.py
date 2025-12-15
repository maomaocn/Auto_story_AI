from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class BaseSchema(BaseModel):
    """所有Schema的基类"""
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

class TimestampSchema(BaseSchema):
    """包含时间戳的Schema基类"""
    created_at: datetime
    updated_at: datetime