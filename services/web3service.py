from dataclasses import dataclass
from web3 import AsyncWeb3
import asyncio
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
    def __init__(self, api_token: str) -> None:
        self._url = f'https://mainnet.infura.io/v3/{api_token}'
        self._w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(self._url))

    @alru_cache(maxsize=4816)
    async def _get_token_symbol(self, address):
        contract = self._w3.eth.contract(address, abi=erc20abi)
        try:
            return await contract.functions.symbol().call()
        except:
            return None

    @alru_cache(maxsize=4816)
    async def _get_token_name(self, address):
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
    async def get_token_balance(self, token_address: str, holder_address: str):
        # README: This function works under the assumption that the working contract is ERC-20
        # This assumption is true as long as only ERC-20 contracts can emit Approval events
        # in the case that it's false make sure to handle error cases
        contract = self._w3.eth.contract(token_address, abi=erc20abi)
        return await contract.functions.balanceOf(holder_address).call()

    async def check_connection(self):
        return await self._w3.is_connected()

    async def get_all_approvals_events(self, approving_address: str) -> list[ApprovalEvent]:
        if not self._w3.is_checksum_address(approving_address):
            raise Exception("invalid address")
        approving_address = \
            f"0x{approving_address[-_ADDER_LEN:].rjust(64, '0')}"

        results = await self._w3.eth.get_logs({'fromBlock': 'earliest', "toBlock": 'latest', 'topics': [
            _APPROVED_HASH, approving_address]})

        return await asyncio.gather(*list(map(self._build_approval_event, results)))
