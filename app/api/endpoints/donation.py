from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationCreate, DonationDB, DonationFullInfoDB
from app.services.investment_process import execute_investment_process

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get(
    '/',
    response_model=list[DonationFullInfoDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(session: SessionDep):
    donations = await donation_crud.get_all(session)
    return donations


@router.get(
    '/my',
    response_model=list[DonationDB],
    response_model_exclude_none=True
)
async def get_user_donations(
    session: SessionDep,
    user: Annotated[User, Depends(current_user)],
):
    return await donation_crud.get_user_donation(session, user)


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True
)
async def create_donation(
    donation: DonationCreate,
    session: SessionDep,
    user: Annotated[User, Depends(current_user)]
):
    donation = await donation_crud.create(
        obj_in=donation, session=session, user=user
    )
    session.add_all(execute_investment_process(
        donation, await charity_project_crud.get_uninvested_objects(session)
    ))
    await session.commit()
    await session.refresh(donation)
    return donation
