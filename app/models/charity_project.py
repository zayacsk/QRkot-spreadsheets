from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import InvestmentBase


class CharityProject(InvestmentBase):
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return (
            f'{super().__repr__()}'
            f'{self.name=}'
            f'{self.description=}'
        )
