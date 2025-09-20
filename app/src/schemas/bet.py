from pydantic import BaseModel, field_validator
import re


_score_re = re.compile(r'^[0-9]{1,2}:[0-9]{1,2}$')


class BetBase(BaseModel):
    user_id: int
    match_id: int
    result: str

    @field_validator('result')
    @classmethod
    def validate_result(cls, v: str) -> str:
        if not isinstance(v, str) or not _score_re.match(v):
            raise ValueError('invalid_result')
        left, right = v.split(':', 1)
        a = int(left)
        b = int(right)
        if a < 0 or a > 99 or b < 0 or b > 99:
            raise ValueError('invalid_result')
        return v


class BetCreate(BetBase):
    pass


class BetUpdate(BaseModel):
    result: str | None = None

    @field_validator('result')
    @classmethod
    def validate_result(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not isinstance(v, str) or not _score_re.match(v):
            raise ValueError('invalid_result')
        left, right = v.split(':', 1)
        a = int(left)
        b = int(right)
        if a < 0 or a > 99 or b < 0 or b > 99:
            raise ValueError('invalid_result')
        return v


class BetOut(BetBase):
    id: int

    class Config:
        from_attributes = True
