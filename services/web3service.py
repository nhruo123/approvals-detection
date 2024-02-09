from web3 import AsyncWeb3
import asyncio
from async_lru import alru_cache
from util.models import ApprovalStatus

_addr_len = 40
_approve_hash = AsyncWeb3.keccak(text="Approval(address,address,uint256)")
_abi = [{"inputs": [], "name": "name", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {
    "inputs": [], "name": "symbol", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}]


class web3service:
    def __init__(self, api_token: str) -> None:
        self._url = f'https://mainnet.infura.io/v3/{api_token}'
        self._w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(self._url))

    @alru_cache(maxsize=512)
    async def _get_token_symbol(self, address):
        contract = self._w3.eth.contract(address, abi=_abi)
        try:
            return await contract.functions.symbol().call()
        except:
            return None

    @alru_cache(maxsize=512)
    async def _get_token_name(self, address):
        contract = self._w3.eth.contract(address, abi=_abi)
        try:
            return await contract.functions.name().call()
        except:
            return None

    async def _build_approval_event(self, result) -> ApprovalStatus:
        value = AsyncWeb3.to_int(result.data)
        address = result.address
        return ApprovalStatus(value=value, name=await self._get_token_name(address), symbol=await self._get_token_symbol(address), address=address)

    async def check_connection(self):
        return await self._w3.is_connected()

    async def get_all_approvals_events(self, approving_address: str) -> list[ApprovalStatus]:
        if not self._w3.is_checksum_address(approving_address):
            raise Exception("invalid address")
        approving_address = f"0x{approving_address[-_addr_len:].rjust(64, '0')}"
        results = await self._w3.eth.get_logs({'fromBlock': 'earliest', "toBlock": 'latest', 'topics': [
            _approve_hash, approving_address]})

        return await asyncio.gather(*list(map(self._build_approval_event, results)))
