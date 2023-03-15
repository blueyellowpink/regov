import json
from typing import List

from fastapi import APIRouter, HTTPException, Request
from indy import IndyError, anoncreds, ledger
from indy import wallet as indy_wallet
from indy.error import ErrorCode
from pydantic import BaseModel

from utils import get_schema, open_wallet

router = APIRouter(prefix="/schema", tags=["schema"])


class CreateSchema(BaseModel):
    issuer_did: str
    schema_name: str
    schema_version: str
    schema_attributes: List[str]
    wallet_config: str
    wallet_credentials: str


@router.post("/create")
async def create_schema_controller(request: Request, body: CreateSchema):
    try:
        _, schema = await anoncreds.issuer_create_schema(
            body.issuer_did,
            body.schema_name,
            body.schema_version,
            json.dumps(body.schema_attributes),
        )

        wallet_handle = None
        try:
            wallet_handle = await open_wallet(
                body.wallet_config, body.wallet_credentials
            )
            request.app.wallets[body.wallet_credentials] = wallet_handle
        except IndyError as ex:
            if ex.error_code == ErrorCode.WalletAlreadyOpenedError:
                pass

        wallet_handle = wallet_handle or request.app.wallets[body.wallet_credentials]
        schema_request = await ledger.build_schema_request(body.issuer_did, schema)
        await ledger.sign_and_submit_request(
            request.app.pool["handle"],
            wallet_handle or request.app.wallets[body.wallet_credentials],
            body.issuer_did,
            schema_request,
        )
        return dict(json.loads(schema))
    except Exception as ex:
        raise HTTPException(status_code=500, detail=ex)


@router.get("/")
async def get_schema_controller(request: Request, did: str, schema_id: str):
    schema_id, schema = await get_schema(did, schema_id, request.app.pool["handle"])
    return {"schema_id": schema_id, "schema": dict(json.loads(schema))}
