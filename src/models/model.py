from datetime import datetime
from typing import Optional, Union

from beanie import after_event, Document, Insert, PydanticObjectId
from pydantic import BaseModel, Field

from src.config import settings


class LoggingBaseModel(BaseModel):
    user_id: Optional[Union[PydanticObjectId, str]] = Field(default=None, description="User ID")
    device: Optional[str] = Field(default=None, description="Device used")
    os: Optional[str] = Field(default=None, description="Operating system")
    is_tablet: Optional[bool] = Field(default=None, description="Is the device a tablet")
    is_mobile: Optional[bool] = Field(default=None, description="Is the device a mobile")
    is_pc: Optional[bool] = Field(default=None, description="Is the device a PC")
    is_bot: Optional[bool] = Field(default=None, description="Is the device a bot")


class LoggingFilter(LoggingBaseModel):
    source: Optional[str] = Field(default=None, description="Source of the log")
    created: Optional[datetime] = Field(default=None, description="Date of creation")
    anonymous: Optional[bool] = Field(default=None, description="Is the user anonymous")


class CreateLoggingModel(LoggingBaseModel):
    source: str = Field(..., description="Source of the log")
    message: str = Field(..., description="Message to log")
    address_ip: str = Field(..., description="Address IP")


class TrailHubModel(CreateLoggingModel, Document):
    created: datetime = Field(default=datetime.now(), description="Date of creation")
    anonymous: Optional[bool] = Field(default=None, description="Is the user anonymous")

    class Settings:
        name = settings.TRAILHUB_MODEL_NAME.split(".")[1]

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat(), PydanticObjectId: str}

    @after_event(Insert)
    def set_anonymous_status(self, *args, **kwargs):
        """
        Validates and sets the anonymous status based on user_id presence.
        If user_id is None, sets anonymous to True regardless of input value.
        """
        if self.user_id is None:
            self.anonymous = True
        else:
            self.anonymous = False
