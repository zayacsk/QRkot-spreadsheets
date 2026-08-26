from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base, CommonMixin


class InvestmentBase(CommonMixin, Base):
    __abstract__ = True

    full_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    invested_amount: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    fully_invested: Mapped[bool] = mapped_column(Boolean, default=False)
    create_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    close_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint('full_amount > 0'),
        CheckConstraint('0 <= invested_amount <= full_amount')
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.invested_amount = 0

    def __repr__(self) -> str:
        return (
            f'{super().__repr__()}'
            f'{self.full_amount=}'
            f'{self.invested_amount=}'
            f'{self.fully_invested=}'
            f'{self.create_date=}'
            f'{self.close_date=}'
        )

    def close_fully_invested(self):
        if self.invested_amount == self.full_amount:
            self.fully_invested = True
            self.close_date = datetime.now()
