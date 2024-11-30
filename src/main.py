from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    pass


app: FastAPI = FastAPI(
    title=f"UNSTA: {settings.APP_NAME}",
    description="A system for logging actions performed on your system.",
    docs_url="/trailhub/docs",
    redoc_url="/trailhub/redoc",
    openapi_url="/trailhub/openapi.json",
)


@app.get("/", include_in_schema=False)
async def read_root():
    return RedirectResponse(url="/trailhub/docs")


@app.get("/trailhub/@ping", tags=["DEFAULT"], summary="Check if server is available")
async def ping():
    return {"message": "pong !"}
