"""
文件名：base.py
文件路径：app/models/base.py
功能描述：SQLAlchemy基础配置和公共模型基类
主要功能：
- 声明式基类定义
- 公共字段和方法定义
- 数据库基础配置
使用说明：
- 导入：from app.models.base import Base
- 继承：class YourModel(Base)
依赖模块：
- sqlalchemy.orm: ORM基础功能
- sqlalchemy: 数据库操作核心
"""

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, BigInteger, DateTime
from sqlalchemy.sql import func

# SQLAlchemy声明式基类
Base = declarative_base()


class TimestampMixin:
    """时间戳混合类，提供创建和更新时间字段"""
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class BaseModel(Base):
    """抽象基础模型类"""
    __abstract__ = True
    
    id = Column(BigInteger, primary_key=True, index=True)