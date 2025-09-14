"""
质量控制模块数据模式

定义API请求和响应的数据结构
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CertificateBase(BaseModel):
    """证书基础模式"""
    serial: str
    name: str
    issuer: str
    description: Optional[str] = None
    issued_at: datetime
    expires_at: datetime
    is_active: bool = True


class CertificateCreate(CertificateBase):
    """创建证书请求模式"""
    pass


class CertificateRead(CertificateBase):
    """证书响应模式 - 使用int类型主键符合BigInteger标准"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
