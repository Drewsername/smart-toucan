from pydantic import BaseModel


class PairingCodeCreate(BaseModel):
    code: str


class PairingCodeUse(BaseModel):
    code: str


class PairingOut(BaseModel):
    code: str
    used: bool

    class Config:
        orm_mode = True
