from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    telegram_id: str
    name: str
    fav_team_id: int | None = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: str | None = None
    telegram_id: str | None = None
    name: str | None = None
    fav_team_id: int | None = None


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True
