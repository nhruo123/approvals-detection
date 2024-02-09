import asyncio
from itertools import chain
from aiohttp import ClientConnectorError
from fastapi import FastAPI, Depends, HTTPException
from functools import lru_cache
from util import config, models
from contextlib import asynccontextmanager
from typing import Annotated
from web3service import web3service


@lru_cache
def get_settings():
    return config.Settings()


@lru_cache
def get_web3service(settings: Annotated[config.Settings, Depends(get_settings)]):
    return web3service(settings.infra_key)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not await get_web3service(get_settings()).check_connection():
        raise Exception(
            "failed to initialize web3service is your api key correct?")
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/approvals")
async def get_approvals(input: models.AddressesList, web3service: Annotated[web3service, Depends(get_web3service)]) -> list[models.ApprovalStatus]:
    try:
        results = await asyncio.gather(*[web3service.get_all_approvals_events(x) for x in input.addresses])
        return list(chain.from_iterable(results)) 
    except ValueError as err:
        # return a basic internal server error, there are too many error codes for now,
        # TODO: implement better error reporting, follow https://docs.infura.io/api/networks/ethereum/json-rpc-methods#error-codes for docs
        raise HTTPException(status_code=500, detail=str(err))
    except ClientConnectorError:
        raise HTTPException(status_code=500, detail="failed to reach node please try again later")