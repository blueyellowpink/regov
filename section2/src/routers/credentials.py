import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from indy import IndyError, anoncreds, ledger
from indy import wallet as indy_wallet
from indy.error import ErrorCode
from pydantic import BaseModel

from utils import get_cred_def, get_schema, open_wallet

router = APIRouter(prefix="/credentials", tags=["credentials"])


class CreateCredentialsDefinition(BaseModel):
    did: str
    wallet_config: str
    wallet_credentials: str
    schema_id: str


class CreateCredentialsOffer(BaseModel):
    wallet_config: str
    wallet_credentials: str
    credentials_definition_id: str


class CreateCredentialsRequest(BaseModel):
    did: str
    wallet_config: str
    wallet_credentials: str
    credentials_definition_id: str
    credentials_offer: str
    master_secret_id: str


class CredentialsValue(BaseModel):
    raw: str
    encode: str


class CredentialsKeyValue(BaseModel):
    string: CredentialsValue


class CreateCredentials(BaseModel):
    wallet_config: str
    wallet_credentials: str
    credentials_offer: str
    credentials_request: str
    credentials_values: CredentialsKeyValue


class SaveCredentials(BaseModel):
    did: str
    wallet_config: str
    wallet_credentials: str
    credentials_definition_id: str
    credentials_request_metadata: str
    credentials: str


@router.post("/definition")
async def create_credentials_definition_controller(
    request: Request, body: CreateCredentialsDefinition
):
    cred_definition = {
        "tag": "TAG1",
        "type": "CL",
        "config": {"support_revocation": False},
    }
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
        wallet_handle = wallet_handle or request.app.wallets[body.wallet_credentials]

        _, schema = await get_schema(
            body.did, body.schema_id, request.app.pool["handle"]
        )
        cred_def_id, cred_def = await anoncreds.issuer_create_and_store_credential_def(
            wallet_handle,
            body.did,
            schema,
            cred_definition["tag"],
            cred_definition["type"],
            json.dumps(cred_definition["config"]),
        )

        cred_def_request = await ledger.build_cred_def_request(body.did, cred_def)
        await ledger.sign_and_submit_request(
            request.app.pool["handle"], wallet_handle, body.did, cred_def_request
        )
        return {"credentials_id": cred_def_id}
    except IndyError as ex:
        if ex.error_code == ErrorCode.AnoncredsCredDefAlreadyExistsError:
            raise HTTPException(
                status_code=400, detail="Credentials Definition Already Exists"
            )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=ex)


@router.post("/request")
async def create_credentials_request_controller(
    request: Request, body: CreateCredentialsRequest
):
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
        wallet_handle = wallet_handle or request.app.wallets[body.wallet_credentials]

        _, cred_def = await get_cred_def(
            body.did, body.credentials_definition_id, request.app.pool["handle"]
        )
        (
            cred_request,
            cred_request_metadata,
        ) = await anoncreds.prover_create_credential_req(
            wallet_handle,
            body.did,
            body.credentials_offer,
            cred_def,
            body.master_secret_id,
        )

        return {
            "credentials_request": cred_request,
            "credentials_request_metadata": cred_request_metadata,
        }
    except Exception as ex:
        raise HTTPException(status_code=400, detail=ex)


@router.post("/offer")
async def create_credentials_offer_controller(
    request: Request, body: CreateCredentialsOffer
):
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
        wallet_handle = wallet_handle or request.app.wallets[body.wallet_credentials]

        cred_offer = await anoncreds.issuer_create_credential_offer(
            wallet_handle, body.credentials_definition_id
        )
        return {"offer": cred_offer}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=ex)


@router.post("/")
async def create_credentials_controller(request: Request, body: CreateCredentials):
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
        wallet_handle = wallet_handle or request.app.wallets[body.wallet_credentials]

        cred_values = json.dumps(
            {
                "string": {
                    "raw": "Alice",
                    "encoded": "1139481716457488690172217916278103335",
                }
            }
        )
        credentials, _, _ = await anoncreds.issuer_create_credential(
            wallet_handle,
            body.credentials_offer,
            body.credentials_request,
            cred_values,
            None,
            None,
        )
        print(credentials)

        return {"credentials": json.dumps(credentials)}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=ex)


@router.post("/save")
async def save_credentials_controller(request: Request, body: SaveCredentials):
    print(json.dumps(json.loads(body.credentials)))
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
        wallet_handle = wallet_handle or request.app.wallets[body.wallet_credentials]

        _, cred_def = await get_cred_def(
            body.did, body.credentials_definition_id, request.app.pool["handle"]
        )
        await anoncreds.prover_store_credential(
            wallet_handle,
            None,
            json.dumps(json.loads(body.credentials_request_metadata)),
            json.loads(body.credentials),
            cred_def,
            None,
        )

        return {"success": True, "message": "Successfully store credentials"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=ex)
