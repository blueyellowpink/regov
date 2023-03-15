import json

import uvicorn
from fastapi import FastAPI
from indy import pool as indy_pool

from routers import credentials, did, proof, schema, steward, wallet
from utils import ConnectionPool, StewardAgent

app = FastAPI()

app.include_router(steward.router)
app.include_router(wallet.router)
app.include_router(did.router)
app.include_router(schema.router)
app.include_router(credentials.router)
app.include_router(proof.router)

app.pool = {}
app.steward = {}
app.wallets = {}


@app.on_event("startup")
async def startup_event():
    await indy_pool.set_protocol_version(2)
    connection_pool = ConnectionPool()
    app.pool = await connection_pool.open_pool_ledger()

    steward_iden = {
        "name": "Steward",
        "wallet_config": json.dumps({"id": "sovrin_steward_wallet"}),
        "wallet_credentials": json.dumps({"key": "steward_wallet_key"}),
        "pool": app.pool["handle"],
        "seed": "000000000000000000000000Steward1",
        "wallet": 5,
        "did_identity": json.dumps({"seed": "000000000000000000000000Steward1"}),
        "did": "Th7MpTaRZVRYnPiabds81Y",
        "key": "FYmoFw55GeQH7SRFa37dkx1d2dZ3zUF8ckg7wmL7ofN4",
    }
    app.steward = StewardAgent(steward_iden)
    try:
        await app.steward.create_wallet("sovrin_steward_wallet", "steward_wallet_key")
        await app.steward.create_did()
        print(app.steward.identity)
    except:
        pass


@app.get("/")
async def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, log_level="info", reload=True)
