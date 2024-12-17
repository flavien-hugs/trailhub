from datetime import datetime
from typing import Optional, Union

from beanie import after_event, Document, Insert, PydanticObjectId
from bson import ObjectId
from pydantic import Field, model_validator

from src.config import settings


class TrailHubModel(Document):
    user_id: Optional[Union[PydanticObjectId, str]] = Field(default=None, description="User ID")
    source: Optional[str] = Field(default=None, description="Source of the log")
    message: Optional[str] = Field(default=None, description="Message to log")
    created: Optional[datetime] = Field(default=datetime.now(), description="Date of creation")
    device: Optional[str] = Field(default=None, description="Device used")
    address_ip: Optional[str] = Field(default=None, description="Address IP")
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

    @classmethod
    def _convert_dict(cls, data: dict):
        if isinstance(data.get("_id"), ObjectId):
            data["_id"] = str(data["_id"])
        return data

    @model_validator(mode="before")
    def convert_objectid_to_string(cls, data: Union[dict, list[dict]]):  # noqa
        if isinstance(data, list):
            return [cls._convert_dict(item) for item in data]
        return cls._convert_dict(data)

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
