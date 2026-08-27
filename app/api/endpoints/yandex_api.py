from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.core.yandex_client import YandexDiskClient, get_yandex_client
from app.crud.charity_project import charity_project_crud
from app.services.yandex_api import create_simple_report

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
YaDiskClientDep = Annotated[YandexDiskClient, Depends(get_yandex_client)]

ERROR_NOT_FOUND = 'Нет данных для формирования отчёта'
ERROR_CREATE_REPORT = 'Ошибка при создании отчёта: {error}'


@router.post(
    '/',
    response_model=str,
    dependencies=[Depends(current_superuser)],
)
async def post_report(session: SessionDep, yandex_client: YaDiskClientDep):
    charity_projects = (
        await charity_project_crud.get_fully_invested_projects(session)
    )
    try:
        public_url = await create_simple_report(
            charity_projects, yandex_client
        )
        return public_url
    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_CREATE_REPORT.format(error)
        )
