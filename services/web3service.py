from dataclasses import dataclass
from web3 import AsyncWeb3
from web3.exceptions import MismatchedABI
import asyncio
from aiohttp import client_exceptions
from util import exceptions
from async_lru import alru_cache
from util.erc20abi import erc20abi

_ADDER_LEN = 40
_APPROVED_HASH = AsyncWeb3.keccak(text="Approval(address,address,uint256)")


@dataclass
class ApprovalEvent():
    value: int
    name: str
    symbol: str
    address: str


class Web3service:
    def __init__(self, api_token: str):
        self._url = f'https://mainnet.infura.io/v3/{api_token}'
        self._w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(self._url))

    @alru_cache(maxsize=4816)
    async def _get_token_symbol(self, address) -> str | None:
        contract = self._w3.eth.contract(address, abi=erc20abi)
        try:
            return await contract.functions.symbol().call()
        except:
            return None

    @alru_cache(maxsize=4816)
    async def _get_token_name(self, address) -> str | None:
        contract = self._w3.eth.contract(address, abi=erc20abi)
        try:
            return await contract.functions.name().call()
        except:
            return None

    async def _build_approval_event(self, result) -> ApprovalEvent:
        value = AsyncWeb3.to_int(result.data)
        address = result.address
        return ApprovalEvent(value=value, name=await self._get_token_name(address), symbol=await self._get_token_symbol(address), address=address)

    @alru_cache(maxsize=4816, ttl=60*2)
    async def get_token_balance(self, token_address: str, holder_address: str) -> int | None:
        contract = self._w3.eth.contract(token_address, abi=erc20abi)
        try:
            return await contract.functions.balanceOf(holder_address).call()
        except MismatchedABI:
            return None

    async def check_connection(self) -> bool:
        return await self._w3.is_connected()

    async def get_all_approvals_events(self, approving_address: str) -> list[ApprovalEvent]:
        if not self._w3.is_checksum_address(approving_address):
            raise ValueError("invalid address")
        approving_address = \
            f"0x{approving_address[-_ADDER_LEN:].rjust(64, '0')}"
        try:
            results = await self._w3.eth.get_logs({'fromBlock': 'earliest', "toBlock": 'latest', 'topics': [
                _APPROVED_HASH, approving_address]})
        except ValueError as err:
            raise exceptions.ApiException(err)
        except client_exceptions.ClientResponseError as err:
            raise exceptions.ApiException(
                f"Failed getting data with error code: {err.status}")
        except client_exceptions.ClientError as err:
            raise exceptions.NodeConnectionException()
        return await asyncio.gather(*list(map(self._build_approval_event, results)))
