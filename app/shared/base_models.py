"""
共享数据模型和基础组件

提供跨模块共享的基础模型类和通用数据结构
根据 docs/modules/data-models/overview.md 文档规范实现
"""

import json
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean, func
from sqlalchemy.types import TypeDecorator, TEXT

# 从技术基础设施层导入统一的Base类
from app.core.database import Base


class TimestampMixin:
    """时间戳混入"""
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class SoftDeleteMixin:
    """软删除混入"""
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    def soft_delete(self):
        """执行软删除"""
        self.is_deleted = True
        self.deleted_at = func.now()
        
    def restore(self):
        """恢复已软删除的记录"""
        self.is_deleted = False
        self.deleted_at = None


class BaseModel(Base):
    """基础模型类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        """转换为字典格式"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def from_dict(self, data):
        """从字典创建实例"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class JSONType(TypeDecorator):
    """JSON数据类型"""
    impl = TEXT
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value, ensure_ascii=False)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value


class ModelRegistry:
    """模型注册表"""
    _models = {}
    
    @classmethod
    def register(cls, model_class):
        cls._models[model_class.__name__] = model_class
        return model_class
    
    @classmethod
    def get_model(cls, name):
        return cls._models.get(name)
    
    @classmethod
    def get_all_models(cls):
        return list(cls._models.values())


__all__ = ['Base', 'BaseModel', 'TimestampMixin', 'SoftDeleteMixin', 'JSONType', 'ModelRegistry']