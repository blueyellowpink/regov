from pydantic import BaseModel


class WalletConfig(BaseModel):
    id: str


class WalletCredentials(BaseModel):
    key: str


class WalletId(BaseModel):
    wallet_id: int
