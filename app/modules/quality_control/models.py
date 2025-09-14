"""
质量控制模块数据模型

定义证书管理相关的数据模型
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, BigInteger
from sqlalchemy.sql import func

from app.core.database import Base
from app.shared.base_models import TimestampMixin


class Certificate(Base, TimestampMixin):
    """证书模型 - 质量控制证书管理"""
    __tablename__ = 'certificates'

    # 主键 - 严格遵循docs/standards/database-standards.md规定
    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    
    # 证书信息
    serial = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # 有效期
    issued_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<Certificate(id={self.id}, serial='{self.serial}', name='{self.name}')>"