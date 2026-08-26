from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CharityProjectBase(BaseModel):
    name: str = Field(min_length=5, max_length=100)
    description: str = Field(min_length=10)
    full_amount: int = Field(gt=0, examples=[1])

    model_config = ConfigDict(extra='forbid')


class CharityProjectCreate(CharityProjectBase):
    pass


class CharityProjectDB(CharityProjectBase):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime] = None


class CharityProjectUpdate(CharityProjectBase):
    name: Optional[str] = Field(min_length=5, max_length=100, default=None)
    description: Optional[str] = Field(min_length=10, default=None)
    full_amount: Optional[int] = Field(gt=0, default=1)
