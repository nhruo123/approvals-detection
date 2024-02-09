from pydantic import BaseModel, model_validator
from web3 import Web3


class AddressesList(BaseModel):
    addresses: list[str]

    @model_validator(mode='after')
    def check_is_address(self):
        for address in self.addresses:
            if not Web3.is_checksum_address(address):
                raise ValueError(
                    'All addresses must be a 20 hex string prefixed with 0x')
        return self


class ApprovalStatus(BaseModel):
    name: str
    symbol: str
    value: int
    address: str
