from pydantic import BaseModel, Field
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., max_length=50)
    email: str


class UserRead(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True
