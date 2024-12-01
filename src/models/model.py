from datetime import datetime
from typing import Optional

from beanie import after_event, Document, Insert, PydanticObjectId
from pydantic import BaseModel, Field

from src.config import settings


class CreateLoggingModel(BaseModel):
    source: str = Field(..., description="Source of the log")
    message: str = Field(..., description="Message to log")
    address_ip: str = Field(..., description="Address IP")
    user_id: Optional[PydanticObjectId] = Field(default=None, description="User ID")
    device: Optional[str] = Field(default=None, description="Device used")
    os: Optional[str] = Field(default=None, description="Operating system")
    user_agent: Optional[str] = Field(default=None, description="User agent")
    browser: Optional[str] = Field(default=None, description="Browser used")
    is_tablet: Optional[bool] = Field(default=False, description="Is the device a tablet")
    is_mobile: Optional[bool] = Field(default=False, description="Is the device a mobile")
    is_pc: Optional[bool] = Field(default=False, description="Is the device a PC")
    is_bot: Optional[bool] = Field(default=False, description="Is the device a bot")
    is_touch_capable: Optional[bool] = Field(default=False, description="Is the device touch capable")


class TrailHubModel(CreateLoggingModel, Document):
    created: datetime = Field(default=datetime.now(), description="Date of creation")
    anonymous: Optional[bool] = Field(default=False, description="Is the user anonymous")

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
