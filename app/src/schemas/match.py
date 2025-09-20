from pydantic import BaseModel, field_validator
from datetime import datetime
import re


_score_re = re.compile(r'^[0-9]{1,2}:[0-9]{1,2}$')


class MatchBase(BaseModel):
    team1_id: int
    team2_id: int
    date: datetime
    result: str | None = None
    stage_name: str

    @field_validator('result')
    @classmethod
    def validate_result(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if isinstance(v, str) and v.lower() == 'null':
            return None
        if not isinstance(v, str) or not _score_re.match(v):
            raise ValueError('invalid_result')
        left, right = v.split(':', 1)
        a = int(left)
        b = int(right)
        if a < 0 or a > 99 or b < 0 or b > 99:
            raise ValueError('invalid_result')
        return v


class MatchCreate(MatchBase):
    pass


class MatchUpdate(BaseModel):
    result: str | None = None

    @field_validator('result')
    @classmethod
    def validate_result(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if isinstance(v, str) and v.lower() == 'null':
            return None
        if not isinstance(v, str) or not _score_re.match(v):
            raise ValueError('invalid_result')
        left, right = v.split(':', 1)
        a = int(left)
        b = int(right)
        if a < 0 or a > 99 or b < 0 or b > 99:
            raise ValueError('invalid_result')
        return v


class MatchOut(MatchBase):
    id: int

    class Config:
        from_attributes = True
