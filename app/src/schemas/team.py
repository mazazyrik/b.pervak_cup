from pydantic import BaseModel


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: str | None = None


class TeamOut(TeamBase):
    id: int

    class Config:
        from_attributes = True
