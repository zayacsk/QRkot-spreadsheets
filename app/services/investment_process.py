from app.models.base import InvestmentBase


def execute_investment_process(
    target: InvestmentBase,
    sources: list[InvestmentBase],
) -> list[InvestmentBase]:
    update_sources = []
    for source in sources:
        update_sources.append(source)
        amount_to_invest = min(
            source.full_amount - source.invested_amount,
            target.full_amount - target.invested_amount
        )
        for object in (target, source):
            object.invested_amount += amount_to_invest
            object.close_fully_invested()
        if target.fully_invested:
            break
    return update_sources
