from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi_pagination import add_pagination

from src.common.config import shutdown_db_client, startup_db_client
from src.config import settings
from src.models import TrailHubModel
from .router import trailhub_router
from src.common.helpers.exception import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_db_client(
        app=app,
        mongodb_uri=settings.MONGODB_URI,
        database_name=settings.MONGO_DB,
        document_models=[TrailHubModel],
    )

    yield

    await shutdown_db_client(app=app)


app: FastAPI = FastAPI(
    lifespan=lifespan,
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


app.include_router(router=trailhub_router)
add_pagination(parent=app)
setup_exception_handlers(app=app)
