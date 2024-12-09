from datetime import datetime
from typing import Optional

from beanie import after_event, Document, Insert, PydanticObjectId
from pydantic import Field

from src.config import settings
from .schema import CreateLoggingModel


class TrailHubModel(CreateLoggingModel, Document):
    created: datetime = Field(default=datetime.now(), description="Date of creation")
    device: Optional[str] = Field(default=None, description="Device used")
    address_ip: str = Field(..., description="Address IP")
    address_mac: Optional[str] = Field(default=None, description="Address MAC")
    os: Optional[str] = Field(default=None, description="Operating system")
    browser: Optional[str] = Field(default=None, description="Browser used")
    is_tablet: Optional[bool] = Field(default=None, description="Is the device a tablet")
    is_mobile: Optional[bool] = Field(default=None, description="Is the device a mobile")
    is_pc: Optional[bool] = Field(default=None, description="Is the device a PC")
    is_bot: Optional[bool] = Field(default=None, description="Is the device a bot")
    anonymous: Optional[bool] = Field(default=None, description="Is the user anonymous")

    class Settings:
        name = settings.TRAILHUB_MODEL_NAME.split(".")[1]

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat(), PydanticObjectId: str}

    @after_event(Insert)
    async def set_anonymous_status(self, *args, **kwargs):
        """
        Validates and sets the anonymous status based on user_id presence.
        If user_id is None, sets anonymous to True regardless of input value.
        """
        if self.user_id is None:
            anonymous = True
        else:
            anonymous = False
        await self.set({"anonymous": anonymous})
