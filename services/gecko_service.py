from async_lru import alru_cache
import httpx
from datetime import datetime, timedelta
from util import exceptions

_HEADERS = {'accept': 'application/json'}


class GeckoService:
    def __init__(self) -> None:
        self._url = 'https://api.coingecko.com/api/v3'

    @alru_cache(ttl=60*10)
    async def _get_coin_dict(self) -> dict[tuple[str, str], str]:
        result_dict = dict()
        try:
            async with httpx.AsyncClient() as client:
                result = await client.get(f'{self._url}/coins/list', headers=_HEADERS)
                if result.is_error:
                    raise exceptions.ApiException("Failed to fetch coins data")
                self._next_coin_update = datetime.now() + timedelta(minutes=5)
                result_array = result.json()
                for entry in result_array:
                    result_dict[(entry["name"], entry["symbol"].lower())
                                ] = entry["id"]

                return result_dict
        except httpx.NetworkError as err:
            raise exceptions.NodeConnectionException(err)

    @alru_cache(maxsize=4816, ttl=60)
    async def get_coin_price(self, name: str, symbol: str) -> float | None:
        symbol = symbol.lower()
        COUNTER_CURRENCY = 'usd'
        key = (name, symbol)
        coin_dict = await self._get_coin_dict()
        if not name or not symbol or key not in coin_dict:
            return None

        coin_id = coin_dict[key]
        try:
            async with httpx.AsyncClient() as client:
                result = await client.get(f'{self._url}/simple/price', headers=_HEADERS, params={'ids': coin_id, 'vs_currencies': COUNTER_CURRENCY})
                if result.is_error:
                    # it's very easy to reach the request limit due to only having 30 requests per minute so we will pretend the token price is unknown
                    # TODO: ask if thats fine
                    return None
                result_body = result.json()
                if coin_id not in result_body:
                    return None

                return result_body[coin_id][COUNTER_CURRENCY]
        except httpx.NetworkError as err:
            raise exceptions.NodeConnectionException(err)
