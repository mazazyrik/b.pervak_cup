from pydantic import BaseModel
from datetime import datetime


class PostBase(BaseModel):
    user_id: int
    photo_url: str
    checked: bool = False


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    photo_url: str | None = None
    checked: bool | None = None


class PostOut(PostBase):
    id: int
    created_at: datetime
    checked: bool

    class Config:
        from_attributes = True
