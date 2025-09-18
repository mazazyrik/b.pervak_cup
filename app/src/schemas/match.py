from pydantic import BaseModel
from datetime import datetime


class MatchBase(BaseModel):
    team1_id: int
    team2_id: int
    date: datetime
    result: str
    stage_name: str
    stage_name: str


class MatchCreate(MatchBase):
    pass


class MatchUpdate(BaseModel):
    team1_id: int | None = None
    team2_id: int | None = None
    date: datetime | None = None
    result: str | None = None
    stage_name: str | None = None
    stage_name: str | None = None


class MatchOut(MatchBase):
    id: int

    class Config:
        from_attributes = True
