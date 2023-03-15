import json

from fastapi import APIRouter, HTTPException, Request
from indy import IndyError, anoncreds
from indy import wallet as indy_wallet
from indy.error import ErrorCode
from pydantic import BaseModel

from models import WalletConfig, WalletCredentials
from utils import Actor, open_wallet

router = APIRouter(prefix="/wallet", tags=["wallet"])


class CreateWallet(BaseModel):
    name: str
    wallet_config: str
    wallet_credentials: str
    role: str = "ENDORSER"


class CreateWalletMasterkey(BaseModel):
    wallet_config: str
    wallet_credentials: str


@router.post("/create")
async def create_wallet_controller(request: Request, body: CreateWallet):
    identity = dict(body)
    identity = {
        "name": body.name,
        "wallet_config": json.dumps({"id": body.wallet_config}),
        "wallet_credentials": json.dumps({"key": body.wallet_credentials}),
    }
    try:
        actor = Actor(identity)
        await actor.create_wallet(body.wallet_config, body.wallet_credentials)
        await actor.create_did()
        request.app.wallets[body.wallet_credentials] = actor.identity["wallet"]
        return actor.identity
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyOpenedError:
            raise HTTPException(status_code=400, detail="Wallet Already Opened")
        elif ex.error_code == ErrorCode.WalletAlreadyExistsError:
            raise HTTPException(status_code=400, detail="Wallet Already Existed")
        else:
            raise HTTPException(status_code=400, detail=ex.error_code)


@router.get("/open")
async def open_wallet_controller(
    request: Request, wallet_config: str, wallet_credentials: str
):
    try:
        wallet_handle = await open_wallet(wallet_config, wallet_credentials)
        request.app.wallets[wallet_credentials] = wallet_handle
        return {"wallet_handle": wallet_handle}
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyOpenedError:
            return {"wallet_handle": request.app.wallets[wallet_credentials]}
        elif ex.error_code == ErrorCode.WalletNotFoundError:
            raise HTTPException(status_code=400, detail="Wallet Not Found")
        else:
            raise HTTPException(status_code=400, detail=ex.message)


@router.post("/create-masterkey")
async def create_master_key(request: Request, body: CreateWalletMasterkey):
    try:
        wallet_handle = None
        try:
            wallet_handle = await open_wallet(
                body.wallet_config, body.wallet_credentials
            )
            request.app.wallets[body.wallet_credentials] = wallet_handle
        except IndyError as ex:
            if ex.error_code == ErrorCode.WalletAlreadyOpenedError:
                pass

        master_secret_id = await anoncreds.prover_create_master_secret(
            wallet_handle or request.app.wallets[body.wallet_credentials], None
        )
        return {"master_secret_id": master_secret_id}
    except Exception as ex:
        raise HTTPException(status_code=400, detail=ex)
