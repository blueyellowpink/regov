import json

from fastapi import APIRouter, HTTPException, Request
from indy import IndyError
from indy import did as indy_did
from indy.error import ErrorCode

from models import WalletId
from utils import Actor

router = APIRouter(prefix="/did", tags=["did"])


@router.post("/create")
async def create_did(request: Request, body: WalletId):
    try:
        did, key = await indy_did.create_and_store_my_did(body.wallet_id, "{}")
        return {"did": did, "key": key}
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyOpenedError:
            raise HTTPException(status_code=400, detail="Wallet Already Opened")
        elif ex.error_code == ErrorCode.WalletAlreadyExistsError:
            raise HTTPException(status_code=400, detail="Wallet Already Existed")
        else:
            raise HTTPException(status_code=400, detail=ex.error_code)
