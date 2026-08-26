from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_full_amount, check_fully_invested_amount,
                                check_invested_amount, check_project_exists,
                                check_unique_name)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.investment_process import execute_investment_process

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get('/', response_model=list[CharityProjectDB])
async def get_all_charity_project(
    session: SessionDep
):
    projects = await charity_project_crud.get_all(session)
    return projects


@router.post(
    '/',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def create_charity_project(
    charity_project: CharityProjectCreate,
    session: SessionDep
):
    await check_unique_name(charity_project.name, session)
    new_project = await charity_project_crud.create(
        charity_project, session
    )
    session.add_all(execute_investment_process(
        new_project, await donation_crud.get_uninvested_objects(session)
    ))
    await session.commit()
    await session.refresh(new_project)
    return new_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def update_charity_project(
    project_id: int,
    project_data: CharityProjectUpdate,
    session: SessionDep
):
    project = await check_project_exists(project_id, session)
    check_fully_invested_amount(project.fully_invested)
    if project_data.name is not None:
        await check_unique_name(project_data.name, session)
    if project_data.full_amount is not None:
        await check_full_amount(project_id, project_data.full_amount, session)
    project = await charity_project_crud.update(
        project, project_data, session
    )
    project.close_fully_invested()
    session.add_all(execute_investment_process(
        project, await donation_crud.get_uninvested_objects(session)
    ))
    await session.commit()
    await session.refresh(project)
    return project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def delete_charity_project(
    project_id: int,
    session: SessionDep
):
    charity_project = await check_project_exists(project_id, session)
    check_invested_amount(charity_project.invested_amount)
    charity_project = await charity_project_crud.remove(
        charity_project, session
    )
    return charity_project
