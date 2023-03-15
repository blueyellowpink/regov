import json

import requests as r

base_url = "http://localhost:5000"

wallet_config = {"prover": "prover28", "issuer": "issuer28", "verifier": "verifer28"}

# Create Prover's wallet
prover_wallet_resp = r.post(
    base_url + "/wallet/create",
    data=json.dumps(
        {
            "name": "prover",
            "wallet_config": wallet_config["prover"],
            "wallet_credentials": "prover",
        }
    ),
).json()
print(prover_wallet_resp)

# Create Prover's master key
prover_masterkey_resp = r.post(
    base_url + "/wallet/create-masterkey",
    data=json.dumps(
        {
            "wallet_config": wallet_config["prover"],
            "wallet_credentials": "prover",
        }
    ),
).json()
print(prover_masterkey_resp)

# Create Verifier's wallet
verifier_wallet_resp = r.post(
    base_url + "/wallet/create",
    data=json.dumps(
        {
            "name": "verifier",
            "wallet_config": wallet_config["verifier"],
            "wallet_credentials": "verifier",
        }
    ),
).json()
print(verifier_wallet_resp)

# Create Issuer's wallet
issuer_wallet_resp = r.post(
    base_url + "/wallet/create",
    data=json.dumps(
        {
            "name": "issuer",
            "wallet_config": wallet_config["issuer"],
            "wallet_credentials": "issuer",
        }
    ),
).json()
print(issuer_wallet_resp)

# Steward creates Verinym for Issuer and Verifier
create_verinym_for_issuer_resp = r.post(
    base_url + "/steward/create-verinym",
    data=json.dumps(
        {
            "did": issuer_wallet_resp["did"],
            "verkey": issuer_wallet_resp["key"],
            "role": "TRUST_ANCHOR",
        }
    ),
).json()
print(create_verinym_for_issuer_resp)

create_verinym_for_verifier_resp = r.post(
    base_url + "/steward/create-verinym",
    data=json.dumps(
        {
            "did": verifier_wallet_resp["did"],
            "verkey": verifier_wallet_resp["key"],
            "role": "TRUST_ANCHOR",
        }
    ),
).json()
print(create_verinym_for_verifier_resp)

# Issuer issues a schema for credentials
cred_schema_resp = r.post(
    base_url + "/schema/create",
    data=json.dumps(
        {
            "issuer_did": issuer_wallet_resp["did"],
            "schema_name": "Test Schema",
            "schema_version": "1.0",
            "schema_attributes": ["string"],
            "wallet_config": wallet_config["issuer"],
            "wallet_credentials": "issuer",
        }
    ),
).json()
print(cred_schema_resp)

# Issuer create credentials definition
cred_definition_resp = r.post(
    base_url + "/credentials/definition",
    data=json.dumps(
        {
            "did": issuer_wallet_resp["did"],
            "wallet_config": wallet_config["issuer"],
            "wallet_credentials": "issuer",
            "schema_id": cred_schema_resp["id"],
        }
    ),
).json()
print(cred_definition_resp)

# Issuer create credentials offer for Prover
cred_offer_resp = r.post(
    base_url + "/credentials/offer",
    data=json.dumps(
        {
            "wallet_config": wallet_config["issuer"],
            "wallet_credentials": "issuer",
            "credentials_definition_id": cred_definition_resp["credentials_id"],
        }
    ),
).json()
print(cred_offer_resp)

# Prover create credentials request to Issuer
cred_request_resp = r.post(
    base_url + "/credentials/request",
    data=json.dumps(
        {
            "did": prover_wallet_resp["did"],
            "wallet_config": wallet_config["prover"],
            "wallet_credentials": "prover",
            "credentials_definition_id": cred_definition_resp["credentials_id"],
            "credentials_offer": cred_offer_resp["offer"],
            "master_secret_id": prover_masterkey_resp["master_secret_id"],
        }
    ),
).json()
print(cred_request_resp)

# With Prover's credentials request, Issuer create credentials for Prover
cred_resp = r.post(
    base_url + "/credentials/",
    data=json.dumps(
        {
            "wallet_config": wallet_config["issuer"],
            "wallet_credentials": "issuer",
            "credentials_offer": cred_offer_resp["offer"],
            "credentials_request": cred_request_resp["credentials_request"],
            "credentials_values": {
                "string": {
                    "raw": "Alice",
                    "encode": "1139481716457488690172217916278103335",
                }
            },
        }
    ),
).json()
print(cred_resp)

# Prover save credentials to wallet
saved = r.post(
    base_url + "/credentials/save",
    data=json.dumps(
        {
            "did": prover_wallet_resp["did"],
            "wallet_config": wallet_config["prover"],
            "wallet_credentials": "prover",
            "credentials_definition_id": cred_definition_resp["credentials_id"],
            "credentials_request_metadata": cred_request_resp[
                "credentials_request_metadata"
            ],
            "credentials": cred_resp["credentials"],
        }
    ),
).json()
print(saved)

# Create a proof request
proof_request = r.post(
    base_url + "/proof/proof-request",
    data=json.dumps(
        {
            "credentials_definition_id": cred_definition_resp["credentials_id"],
            "proof_request_name": "Test Proof Request",
        }
    ),
).json()
print(proof_request)

# Prover provides proof
proof = r.post(
    base_url + "/proof/",
    data=json.dumps(
        {
            "did": prover_wallet_resp["did"],
            "wallet_config": wallet_config["prover"],
            "wallet_credentials": "prover",
            "proof_request": proof_request["proof_request"],
            "master_secret_id": prover_masterkey_resp["master_secret_id"],
        }
    ),
).json()
print(proof)

# Verifier verify proof
verified = r.post(
    base_url + "/proof/verify",
    data=json.dumps(
        {
            "did": verifier_wallet_resp["did"],
            "proof": proof["proof"],
            "proof_request": proof_request["proof_request"],
        }
    ),
).json()
print(verified)
