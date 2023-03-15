import asyncio
import json
import time
from abc import ABC, abstractmethod

from indy import IndyError, anoncreds, did, ledger, pool, wallet
from indy.error import ErrorCode


class ConnectionPool:
    def __init__(self):
        self.pool_ = {
            "name": "pool1",
            "config": json.dumps(
                {"genesis_txn": "/home/indy/sandbox/pool_transactions_genesis"}
            ),
        }

    async def open_pool_ledger(self):
        print("Open Pool Ledger: {}".format(self.pool_["name"]))
        try:
            await pool.create_pool_ledger_config(
                self.pool_["name"], self.pool_["config"]
            )
        except IndyError as ex:
            if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
                pass
        self.pool_["handle"] = await pool.open_pool_ledger(self.pool_["name"], None)
        return self.pool_


class Actor:
    def __init__(self, info: dict):
        self.identity = info

    def get_info(self) -> dict:
        return self.identity

    async def create_wallet(self, wallet_config: str, wallet_credentials: str) -> None:
        print('"{}" -> Create wallet'.format(self.identity["name"]))
        try:
            await wallet.create_wallet(
                self.identity["wallet_config"], self.identity["wallet_credentials"]
            )
            wallet_handle = await open_wallet(wallet_config, wallet_credentials)
            self.identity["wallet"] = wallet_handle
        except IndyError as ex:
            if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
                pass
            else:
                raise ex

    async def create_did(self) -> None:
        self.identity["did"], self.identity["key"] = await did.create_and_store_my_did(
            self.identity["wallet"], "{}"
        )

    async def send_schema(self, did: str, schema: dict) -> None:
        schema_request = await ledger.build_schema_request(did, schema)
        await ledger.sign_and_submit_request(
            self.identity["pool"],
            self.identity["wallet"],
            self.identity["did"],
            schema_request,
        )


class StewardAgent(Actor):
    def __init__(self, info: dict):
        super().__init__(info)

    async def create_did(self) -> None:
        await self.open_wallet()
        self.identity["did_identity"] = json.dumps({"seed": self.identity["seed"]})
        self.identity["did"], self.identity["key"] = await did.create_and_store_my_did(
            self.identity["wallet"], self.identity["did_identity"]
        )

    async def send_nym(self, new_did: str, new_key: str, new_role: str):
        try:
            nym_request = await ledger.build_nym_request(
                self.identity["did"], new_did, new_key, None, new_role
            )
            await self.open_wallet()
            await ledger.sign_and_submit_request(
                self.identity["pool"],
                self.identity["wallet"],
                self.identity["did"],
                nym_request,
            )
        except Exception as e:
            raise e

    async def open_wallet(self):
        try:
            print(dict(json.loads(self.identity["wallet_config"])))
            print(dict(json.loads(self.identity["wallet_credentials"])))

            self.identity["wallet"] = await open_wallet(
                dict(json.loads(self.identity["wallet_config"]))["id"],
                dict(json.loads(self.identity["wallet_credentials"]))["key"],
            )
            print(self.identity["wallet"])
        except IndyError as ex:
            if ex.error_code == ErrorCode.WalletAlreadyOpenedError:
                pass
            else:
                raise ex


async def open_wallet(wallet_config: str, wallet_credentials: str):
    identity = {
        "wallet_config": json.dumps({"id": wallet_config}),
        "wallet_credentials": json.dumps({"key": wallet_credentials}),
    }
    try:
        handle = await wallet.open_wallet(
            identity["wallet_config"], identity["wallet_credentials"]
        )
        return handle
    except IndyError as ex:
        raise ex


async def get_schema(caller_did: str, schema_id: str, pool_handle: int):
    get_schema_request = await ledger.build_get_schema_request(caller_did, schema_id)
    get_schema_response = await ledger.submit_request(pool_handle, get_schema_request)
    return await ledger.parse_get_schema_response(get_schema_response)


async def get_cred_def(caller_did: str, cred_def_id: str, pool_handle: int):
    get_cred_def_request = await ledger.build_get_cred_def_request(
        caller_did, cred_def_id
    )
    get_cred_def_response = await ledger.submit_request(
        pool_handle, get_cred_def_request
    )
    return await ledger.parse_get_cred_def_response(get_cred_def_response)


async def get_credential_for_referent(search_handle, referent):
    credentials = json.loads(
        await anoncreds.prover_fetch_credentials_for_proof_req(
            search_handle, referent, 10
        )
    )
    return credentials[0]["cred_info"]


async def prover_get_entities_from_ledger(
    pool_handle: int, _did: str, identifiers: dict
):
    schemas = {}
    cred_defs = {}
    rev_states = {}
    for item in identifiers.values():
        (received_schema_id, received_schema) = await get_schema(
            _did, item["schema_id"], pool_handle
        )
        schemas[received_schema_id] = json.loads(received_schema)

        (received_cred_def_id, received_cred_def) = await get_cred_def(
            _did, item["cred_def_id"], pool_handle
        )
        cred_defs[received_cred_def_id] = json.loads(received_cred_def)

        if "rev_reg_seq_no" in item:
            pass

    return json.dumps(schemas), json.dumps(cred_defs), json.dumps(rev_states)


async def verifier_get_entities_from_ledger(
    pool_handle: int, _did: str, identifiers: dict
):
    schemas = {}
    cred_defs = {}
    rev_reg_defs = {}
    rev_regs = {}
    for item in identifiers:
        (received_schema_id, received_schema) = await get_schema(
            _did, item["schema_id"], pool_handle
        )
        schemas[received_schema_id] = json.loads(received_schema)

        (received_cred_def_id, received_cred_def) = await get_cred_def(
            _did, item["cred_def_id"], pool_handle
        )
        cred_defs[received_cred_def_id] = json.loads(received_cred_def)

        if "rev_reg_seq_no" in item:
            pass

    return (
        json.dumps(schemas),
        json.dumps(cred_defs),
        json.dumps(rev_reg_defs),
        json.dumps(rev_regs),
    )
