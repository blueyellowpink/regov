import json

from fastapi import APIRouter, HTTPException, Request
from indy import IndyError
from indy.error import ErrorCode
from pydantic import BaseModel

from utils import StewardAgent

router = APIRouter(prefix="/steward", tags=["steward"])


class CreateVerinym(BaseModel):
    did: str
    verkey: str
    role: str


@router.post("/create-verinym")
async def create_verinym(request: Request, body: CreateVerinym):
    try:
        await request.app.steward.send_nym(body.did, body.verkey, body.role)
    except IndyError as ex:
        print(ex.message)
        raise HTTPException(status_code=500, detail=ex.message)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500)

    return {"success": True, "message": "Successfully created NYM"}
