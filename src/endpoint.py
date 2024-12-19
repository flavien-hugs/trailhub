from typing import Optional
from urllib.parse import urljoin

from beanie import BeanieObjectId
from fastapi import APIRouter, Body, Depends, Query, Request, status
from fastapi_pagination.ext.beanie import paginate
from getmac import get_mac_address
from pymongo import ASCENDING, DESCENDING
from user_agents import parse

from src.common.depends.permission import CheckAccessAllow, VerifyAccessToken
from src.common.helpers.error_codes import AppErrorCode
from src.common.helpers.exception import CustomHTTPException
from src.common.helpers.pagination import customize_page
from src.common.helpers.utils import SortEnum
from src.config import settings
from src.models import CreateLoggingModel, LoggingFilter, TrailHubModel

trailhub_router = APIRouter(
    prefix="/logs",
    tags=["LOGS"],
    responses={404: {"description": "Not found"}},
)

VERIFY_ACCESS_TOKEN_URL = urljoin(settings.API_AUTH_URL_BASE, settings.API_AUTH_CHECK_VALIDATE_ACCESS_TOKEN)
CHECK_ACCESS_ALLOW_URL = urljoin(settings.API_AUTH_URL_BASE, settings.API_AUTH_CHECK_ACCESS_ENDPOINT)


@trailhub_router.post(
    "",
    dependencies=[Depends(VerifyAccessToken(url=VERIFY_ACCESS_TOKEN_URL))] if settings.ALLOW_ANONYM_PUSH else [],
    response_model=TrailHubModel,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new log",
)
async def create_log(request: Request, payload: CreateLoggingModel = Body(...)):

    # Retrieve client IP address
    address_ip = request.client.host

    # If behind a proxy, use the X-Forwarded-For header
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        address_ip = forwarded_for.split(",")[0]

    address_mac = (
        get_mac_address(ip=address_ip)
        or get_mac_address(interface="eth0")
        or get_mac_address(ip=address_ip, network_request=True)
    )

    # Retrieve User-Agent header
    user_agent_str = request.headers.get("User-Agent", "")
    user_agent = parse(user_agent_str)
    if not user_agent:
        user_agent = parse("")

    new_log = await TrailHubModel(
        **payload.model_dump(),
        device=user_agent.device.family,
        os=user_agent.os.family,
        browser=user_agent.browser.family,
        is_tablet=user_agent.is_tablet,
        is_mobile=user_agent.is_mobile,
        is_pc=user_agent.is_pc,
        is_bot=user_agent.is_bot,
        address_ip=address_ip,
        address_mac=address_mac,
    ).create()
    return new_log


@trailhub_router.get(
    "",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions={"trailhub:can-read-trail"}))],
    response_model=customize_page(TrailHubModel),
    summary="Get all logs",
    status_code=status.HTTP_200_OK,
)
async def get_logs(
    filter: LoggingFilter = Depends(LoggingFilter),
    sort: Optional[SortEnum] = Query(default=None, description="Sort by created date: 'asc' or 'desc'"),
):
    query = filter.model_dump(exclude_none=True, exclude_unset=True)
    if filter.source:
        query.update({"source": filter.source})
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
    return await paginate(query=logs)


@trailhub_router.get(
    "/{id}",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions={"trailhub:can-read-trail"}))],
    response_model=TrailHubModel,
    summary="Retrieve log by ID",
    status_code=status.HTTP_200_OK,
)
async def retrieve_log(id: BeanieObjectId):
    if (doc := await TrailHubModel.find_one({"_id": id})) is None:
        raise CustomHTTPException(
            code_error=AppErrorCode.DOCUMENT_NOT_FOUND,
            message_error=f"Document with '{id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return doc
