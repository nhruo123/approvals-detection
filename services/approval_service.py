import asyncio
from services.gecko_service import GeckoService
from services.web3service import ApprovalEvent, Web3service
from util import models


def build_approval_model(approval_event: ApprovalEvent, price: float | None, balance: int, get_price: bool) -> models.ApprovalStatus:
    exposure = None
    if price is not None:
        exposure = min(approval_event.value, balance) * price

    result = models.ApprovalStatus(address=approval_event.address,
                                   name=approval_event.name,
                                   symbol=approval_event.symbol,
                                   value=approval_event.value,
                                   exposure=exposure)

    if get_price:
        result = result.model_copy(update={'price': price})

    return result


async def get_approvals_for_address(address: str, web3service: Web3service, gecko_service: GeckoService, get_price: bool) -> list[models.ApprovalStatus]:
    approvals = await web3service.get_all_approvals_events(address)
    prices_futures = asyncio.gather(
        *[gecko_service.get_coin_price(x.name, x.symbol) for x in approvals])
    balances_futures = asyncio.gather(
        *[web3service.get_token_balance(x.address, address) for x in approvals])

    (prices, balances) = await asyncio.gather(prices_futures, balances_futures)

    return [build_approval_model(approval_event, price, balance, get_price) for (approval_event, price, balance) in zip(approvals, prices, balances)]
