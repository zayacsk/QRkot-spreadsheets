from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DonationBase(BaseModel):
    full_amount: int = Field(gt=0, examples=[1])
    comment: Optional[str] = None

    model_config = ConfigDict(extra='forbid')


class DonationCreate(DonationBase):
    pass


class DonationDB(DonationBase):
    id: int
    create_date: datetime


class DonationFullInfoDB(DonationDB):
    invested_amount: int
    fully_invested: bool
    user_id: int
    close_date: Optional[datetime] = None
