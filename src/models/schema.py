from datetime import datetime
from typing import Optional, Union

from beanie import PydanticObjectId
from pydantic import BaseModel, Field, field_validator


class LoggingBaseModel(BaseModel):
    user_id: Optional[Union[PydanticObjectId, str]] = Field(default=None, description="User ID")


class LoggingFilter(LoggingBaseModel):
    source: Optional[str] = Field(default=None, description="Source of the log")
    created: Optional[datetime] = Field(default=None, description="Date of creation")
    anonymous: Optional[bool] = Field(default=None, description="Is the user anonymous")
    device: Optional[str] = Field(default=None, description="Device used")
    os: Optional[str] = Field(default=None, description="Operating system")
    is_tablet: Optional[bool] = Field(default=None, description="Is the device a tablet")
    is_mobile: Optional[bool] = Field(default=None, description="Is the device a mobile")
    is_pc: Optional[bool] = Field(default=None, description="Is the device a PC")
    is_bot: Optional[bool] = Field(default=None, description="Is the device a bot")


class CreateLoggingModel(LoggingBaseModel):
    source: str = Field(..., description="Source of the log")
    message: str = Field(..., description="Message to log")


    @field_validator("source", mode="before")
    def source_to_lower(cls, value):
        return value.lower().replace(" ", "")
