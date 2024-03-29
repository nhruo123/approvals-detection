How to run
====
First install requirements `pip install -r .\requirements.txt`

To run cli tool: `python .\cli.py approvals` 

To run web server `uvicorn web:app`

Test addresses
----
https://etherscan.io/address/0x005e20fcf757b55d6e27dea9ba4f90c0b03ef852
https://etherscan.io/address/0xb4b28f9487cc25c26c655f04a37f974068920541

Question Mission
=====

`Approval` is an event that `ERC20` defines as part of it's [standard](https://github.com/ethereum/ercs/blob/master/ERCS/erc-20.md#approval), this is an `event` that MUST be triggered on any successful call to the `approve` function. An event is a primitive in solidity that can be listened to by Ethereum clients such as a wep application.

The [`approve`](https://github.com/ethereum/ercs/blob/master/ERCS/erc-20.md#approve) function allows ( or approve ) a spender to withdraw from your account multiple times, up to a set amount, `approve` should be used with the `transferFrom` function, which allows the approved address to transfer from you address to a target address.

The main differences between `transfer` and `transferFrom` is:
- `transfer` is used by an address to transfer an given amount of tokens from itself to another address ONCE. But on the other hand, `transferFrom` lets the caller to transfers an amount of tokens from an address (not only itself, but any address) to another address, but only up to the a total amount of `allowed` ( which carries over from older transactions ) which is set by the aforementioned `approve` function.

Due to this difference `transfer` is used in so called single transactions workflow, we use it to transfer a set amount of tokens form one address to another (the most basic kind of transaction transfer X tokens from May to Rom).

On the other hand `transferFrom` is used in so called two transaction workflow, it is used in the case where we want to delegate control over our tokens to another address, this is done by first calling the aforementioned `approve` function in order to delegate control to a given address, and then that address can preform transactions on our behalf (by calling `transferFrom` and passing our address to `_from` parameter). 

This functionality can be used for Initial Coin Offering (ICO), where you create a token that acts as a share, and a treader contract that accepts some form of currency and returns our token. But the token is a separate smart contract to the trader contract so in order to allow the trader contract to trade our tokens first need to call `approve` to delegate control over a certain amount of our tokens. 