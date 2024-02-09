from web3 import Web3
from functools import lru_cache

_addr_len = 40
_approve_hash = Web3.keccak(text="Approval(address,address,uint256)")
_abi = [{"inputs": [], "name": "name", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {
    "inputs": [], "name": "symbol", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}]


class InfraWrapper:
    def __init__(self, API_TOKEN: str) -> None:
        self._url = f'https://mainnet.infura.io/v3/{API_TOKEN}'
        self._w3 = Web3(Web3.HTTPProvider(self._url))

    @lru_cache(maxsize=512)
    def _get_contract_name(self, address):
        contract = self._w3.eth.contract(address, abi=_abi)
        name = address
        try:
            name = contract.functions.symbol().call()
        except:
            try:
                name = contract.functions.name().call()
            except:
                pass
        return name
        
    def _build_approval_event(self, result):
        value = Web3.to_int(result.data)

        return {
            'value': value,
            'name': self._get_contract_name(result.address),
        }


    def get_all_approvals_events(self, approving_address: str):
        if not self._w3.is_checksum_address(approving_address):
            raise Exception("invalid address")
        approving_address = f"0x{approving_address[-_addr_len:].rjust(64, '0')}"
        results = self._w3.eth.get_logs({'fromBlock': 'earliest', "toBlock": 'latest', 'topics': [
                                        _approve_hash, approving_address]})
        return list(map(self._build_approval_event, results))
        