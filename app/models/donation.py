from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import InvestmentBase


class Donation(InvestmentBase):
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.id', name='fk_donation_user_id_user')
    )

    def __repr__(self) -> str:
        return (
            f'{super().__repr__()}'
            f'{self.comment=}'
            f'{self.user_id=}'
        )
