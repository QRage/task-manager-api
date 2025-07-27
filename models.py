from pydantic import BaseModel, Field, ConfigDict, field_serializer
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    """
    Base Pydantic model for common task attributes.

    :param title: The title of the task. Must be a string between 1 and 100 characters.
    :type title: str
    :param description: A detailed description of the task. Optional.
    :type description: Optional[str]
    :param completed: The completion status of the task (True for completed, False for pending). Defaults to False.
    :type completed: bool
    """
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    completed: bool = False

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(TaskBase):
    """
    Pydantic model for creating a new task.
    Inherits all fields from TaskBase.
    """
    pass


class TaskPut(BaseModel):
    """
    Pydantic model for completely updating an existing task (PUT request).
    All fields are required for a full resource replacement.

    :param title: The new title for the task. This field is required.
    :type title: str
    :param description: The new description for the task. Optional.
    :type description: Optional[str]
    :param completed: The new completion status for the task. This field is required with a default value.
    :type completed: bool
    """
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    completed: bool = False


class TaskPatch(BaseModel):
    """
    Pydantic model for partially updating an existing task (PATCH request).
    All fields are optional, as PATCH only modifies the specified attributes.

    :param title: The optional new title for the task.
    :type title: Optional[str]
    :param description: The optional new description for the task.
    :type description: Optional[str]
    :param completed: The optional new completion status for the task.
    :type completed: Optional[bool]
    """
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None)
    completed: Optional[bool] = None


class TaskInDB(TaskBase):
    """
    Pydantic model for a task as stored in the "database" (in-memory).
    Includes task ID and creation/update timestamps.

    :param id: The unique identifier of the task.
    :type id: int
    :param created_at: The timestamp when the task was created.
    :type created_at: datetime
    :param updated_at: The timestamp when the task was last updated.
    :type updated_at: datetime
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, dt: datetime) -> str:
        """
        Serializes datetime objects to ISO 8601 format for JSON responses.

        :param dt: The datetime object to serialize.
        :type dt: datetime
        :return: A string representation of the datetime in ISO 8601 format.
        :rtype: str
        """
        return dt.isoformat()
