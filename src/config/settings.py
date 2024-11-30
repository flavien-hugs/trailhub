from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class TrailHubSettings(BaseSettings):
    # APP CONFIG
    APP_NAME: Optional[str] = Field(default="TrailHub", alias="APP_NAME", description="Name of the application")
    APP_HOSTNAME: Optional[str] = Field(
        default="0.0.0.0", alias="APP_HOSTNAME", description="Hostname of the application"
    )
    APP_RELOAD: Optional[bool] = Field(default=True, alias="APP_RELOAD", description="Enable/Disable auto-reload")
    APP_ACCESS_LOG: Optional[bool] = Field(
        default=True, alias="APP_ACCESS_LOG", description="Enable/Disable access log"
    )
    APP_DEFAULT_PORT: Optional[int] = Field(
        default=1993, alias="APP_DEFAULT_PORT", description="Default port of the application"
    )
    ALLOW_ANONYM_PUSH: Optional[bool] = Field(
        default=False, alias="ALLOW_ANONYM_PUSH", description="Allow anonymous push to the config"
    )

    # APP MODEL NAME
    TRAILHUB_MODEL_NAME: str = Field(..., alias="TRAILHUB_MODEL_NAME", description="Name of the model")

    # DATABASE CONFIG
    MONGO_DB: str = Field(..., alias="MONGO_DB", description="Name of the config")
    MONGODB_URI: str = Field(..., alias="MONGODB_URI", description="URI of the MongoDB config")

    # VALIDATE TOKEN AND CHECK ACCESS ENDPOINT
    API_AUTH_URL_BASE: str = Field(..., alias="API_AUTH_URL_BASE", description="Base URL of the authentication service")
    API_AUTH_CHECK_ACCESS_ENDPOINT: str = Field(
        ..., alias="API_AUTH_CHECK_ACCESS_ENDPOINT", description="Endpoint to check access"
    )
    API_AUTH_VALIDATE_TOKEN_ENDPOINT: str = Field(
        ..., alias="API_AUTH_VALIDATE_TOKEN_ENDPOINT", description="Endpoint to validate token"
    )


@lru_cache
def get_settings() -> TrailHubSettings:
    return TrailHubSettings()
