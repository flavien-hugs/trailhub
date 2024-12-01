from typing import Optional

from beanie import PydanticObjectId
from fastapi import APIRouter, Body, Depends, Query, status
from fastapi_pagination.ext.beanie import paginate
from pymongo import ASCENDING, DESCENDING

from src.common.helpers.utils import customize_page, SortEnum
from src.common.helpers.exception import CustomHTTPException, AppErrorCodes
from src.models import CreateLoggingModel, LoggingFilter, TrailHubModel

trailhub_router = APIRouter(
    prefix="/logs",
    tags=["LOGS"],
    responses={404: {"description": "Not found"}},
)


@trailhub_router.post("", response_model=TrailHubModel, status_code=status.HTTP_201_CREATED, summary="Create a new log")
async def create_log(payload: CreateLoggingModel = Body(...)):
    data = payload.model_copy(update={"source": payload.source.lower()})
    new_log = await TrailHubModel(**data.model_dump()).create()
    return new_log


@trailhub_router.get(
    "",
    response_model=customize_page(TrailHubModel),
    summary="Get all logs",
    status_code=status.HTTP_200_OK
)
async def get_logs(
        filter: LoggingFilter = Depends(LoggingFilter),
        sort: Optional[SortEnum] = Query(default=None, description="Sort by created date: 'asc' or 'desc'"),
):
    query = filter.model_dump(exclude_none=True, exclude_unset=True)
    if filter.source:
        query.update({"source": filter.source.lower()})
    elif filter.user_id:
        query.update({"user_id": filter.user_id})
    elif filter.device:
        query.update({"device": filter.device})
    elif filter.os:
        query.update({"os": filter.os})
    elif filter.is_tablet:
        query.update({"is_tablet": filter.is_tablet})
    elif filter.is_mobile:
        query.update({"is_mobile": filter.is_mobile})
    elif filter.is_pc:
        query.update({"is_pc": filter.is_pc})
    elif filter.is_bot:
        query.update({"is_bot": filter.is_bot})
    elif filter.anonymous:
        query.update({"anonymous": filter.anonymous})
    elif filter.created:
        query.update({"created": filter.created})

    _sort = DESCENDING if sort == SortEnum.DESC else ASCENDING
    logs = TrailHubModel.find(query, sort=[("created", _sort)])

    return await paginate(logs)


@trailhub_router.get(
    "/{id}",
    response_model=TrailHubModel,
    summary="Retrieve log by ID", status_code=status.HTTP_200_OK
)
async def retrieve_log(id: PydanticObjectId):
    if (document := await TrailHubModel.get(id)) is None:
        raise CustomHTTPException(
            error_code=AppErrorCodes.DOCUMENT_NOT_FOUND,
            error_message=f"Document with '{id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return document
