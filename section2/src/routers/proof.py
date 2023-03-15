import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from indy import IndyError, anoncreds, ledger
from indy import wallet as indy_wallet
from indy.error import ErrorCode
from pydantic import BaseModel

from utils import (get_credential_for_referent, open_wallet,
                   prover_get_entities_from_ledger,
                   verifier_get_entities_from_ledger)

router = APIRouter(prefix="/proof", tags=["proof"])


class CreateProofRequest(BaseModel):
    credentials_definition_id: str
    proof_request_name: str


class CreateProof(BaseModel):
    did: str
    wallet_config: str
    wallet_credentials: str
    proof_request: str
    master_secret_id: str


class VerifyProof(BaseModel):
    did: str
    proof: str
    proof_request: str


@router.post("/proof-request")
async def create_proof_request(body: CreateProofRequest):
    try:
        nonce = await anoncreds.generate_nonce()
        request = json.dumps(
            {
                "nonce": nonce,
                "name": body.proof_request_name,
                "version": "0.1",
                "requested_attributes": {
                    "attr1_referent": {
                        "name": "string",
                    }
                },
                "requested_predicates": {},
            }
        )
        return {"proof_request": request}
    except Exception as ex:
        raise HTTPException(status_code=400, detail=ex)


@router.post("/")
async def create_proof(request: Request, body: CreateProof):
    print(body)
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

        search_for_proof_request = (
            await anoncreds.prover_search_credentials_for_proof_req(
                wallet_handle, json.dumps(json.loads(body.proof_request)), None
            )
        )

        cred_for_attr1 = await get_credential_for_referent(
            search_for_proof_request, "attr1_referent"
        )

        await anoncreds.prover_close_credentials_search_for_proof_req(
            search_for_proof_request
        )

        cred_for_proof = {
            cred_for_attr1["referent"]: cred_for_attr1,
        }
        schemas, cred_defs, revoc_states = await prover_get_entities_from_ledger(
            request.app.pool["handle"], body.did, cred_for_proof
        )

        requested_creds = json.dumps(
            {
                "self_attested_attributes": {
                    "attr1_referent": "Alice",
                },
                "requested_attributes": {},
                "requested_predicates": {},
            }
        )
        proof = await anoncreds.prover_create_proof(
            wallet_handle,
            json.dumps(json.loads(body.proof_request)),
            requested_creds,
            body.master_secret_id,
            schemas,
            cred_defs,
            revoc_states,
        )
        return {"proof": proof}
    except Exception as ex:
        raise HTTPException(status_code=400, detail=ex)


@router.post("/verify")
async def verify_proof(request: Request, body: VerifyProof):
    try:
        proof = dict(json.loads(body.proof))
        (
            schemas,
            cred_defs,
            rev_ref_defs,
            rev_regs,
        ) = await verifier_get_entities_from_ledger(
            request.app.pool["handle"], body.did, proof["identifiers"]
        )

        assert (
            "Alice" == proof["requested_proof"]["self_attested_attrs"]["attr1_referent"]
        )

        assert await anoncreds.verifier_verify_proof(
            json.dumps(json.loads(body.proof_request)),
            json.dumps(json.loads(body.proof)),
            schemas,
            cred_defs,
            rev_ref_defs,
            rev_regs,
        )

        return {"success": True, "message": "Successfully verified"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=ex)
