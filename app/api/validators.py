from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud

PROJECT_EXISTS = 'Проект с таким именем:{} уже существует!'
PROJECT_NOT_FOUND = 'Проекта с id:{} не найден'
FULL_AMOUNT_TOO_LOW = (
    'Нельзя установить значение full_amount меньше '
    'уже вложенной суммы.'
)
PROJECT_CLOSED = 'Закрытый проект нельзя редактировать!'
PROJECT_HAS_INVESTMENTS = (
    'Запрещено удаление проектов, в которые уже внесены средства!'
)


async def check_unique_name(
        project_name: str,
        session: AsyncSession
) -> None:
    project = await charity_project_crud.get_project_id_by_name(
        project_name, session
    )
    if project is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=PROJECT_EXISTS
        )


async def check_project_exists(
        project_id: int,
        session: AsyncSession
):
    charity_project = await charity_project_crud.get(project_id, session)
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PROJECT_NOT_FOUND
        )
    return charity_project


async def check_full_amount(
    charity_id: int,
    update_amount: int,
    session: AsyncSession
):
    charity_project = await charity_project_crud.get(charity_id, session)
    if update_amount < charity_project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=FULL_AMOUNT_TOO_LOW
        )


def check_fully_invested_amount(
    fully_invested: bool
):
    if fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=PROJECT_CLOSED
        )


def check_invested_amount(
    invested_amount: int
):
    if invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=PROJECT_HAS_INVESTMENTS
        )
