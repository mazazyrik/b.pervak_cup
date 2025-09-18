from pydantic import BaseModel


class TokenIn(BaseModel):
    telegram_id: str


class TokenOut(BaseModel):
    token: str
