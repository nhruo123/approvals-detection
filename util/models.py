from typing import Annotated
from pydantic import AfterValidator, BaseModel, Field
from web3 import Web3

def _validate_address(addr:str):
    if not Web3.is_checksum_address(addr):
        raise ValueError(
            'All addresses must be a 20 hex string prefixed with 0x')
    return addr

Address = Annotated[str, AfterValidator(_validate_address)]

class ApprovalInput(BaseModel):
    addresses: list[Address]
    get_price: bool = False 


class ApprovalStatus(BaseModel):
    name: str
    symbol: str
    value: int
    address: str
    price: float | None = None
