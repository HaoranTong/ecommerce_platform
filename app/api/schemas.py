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


class ProductCreate(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None


class ProductRead(BaseModel):
    id: int
    name: str
    sku: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class CertificateCreate(BaseModel):
    name: str
    issuer: Optional[str] = None
    serial: str
    description: Optional[str] = None


class CertificateRead(BaseModel):
    id: int
    name: str
    issuer: Optional[str] = None
    serial: str
    description: Optional[str] = None

    class Config:
        orm_mode = True
