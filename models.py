from pydantic import BaseModel, Field, ConfigDict, field_serializer
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    completed: bool = False

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None


class TaskInDB(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, dt: datetime) -> str:
        return dt.isoformat()
