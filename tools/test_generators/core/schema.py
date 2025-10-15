"""
数据模型定义 - 测试生成器使用的核心数据结构

包含:
- FieldInfo: 字段信息
- RelationshipInfo: 关系信息
- ModelInfo: 完整模型信息
- RepositoryMethodInfo: Repository方法信息
- RepositoryInfo: Repository类信息
- ModuleStructure: 模块结构信息

版本: v1.0
从generate_test_template.py第104-182行提取
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class FieldInfo:
    """数据模型字段信息"""

    name: str
    column_type: str
    python_type: str
    nullable: bool
    primary_key: bool
    foreign_key: Optional[str]
    unique: bool
    default: Any
    server_default: Any = None  # 数据库默认值
    constraints: List[str] = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []


@dataclass
class RelationshipInfo:
    """数据模型关系信息"""

    name: str
    related_model: str
    relationship_type: str
    back_populates: Optional[str]
    cascade: Optional[str]
    foreign_keys: List[str]


@dataclass
class ModelInfo:
    """完整的数据模型信息"""

    name: str
    tablename: str
    fields: List[FieldInfo]
    relationships: List[RelationshipInfo]
    mixins: List[str]
    docstring: Optional[str]
    primary_keys: List[str]
    unique_constraints: List[List[str]]
    module_name: Optional[str] = None  # 所属模块名（如product_catalog）


@dataclass
class RepositoryMethodInfo:
    """Repository方法信息"""
    
    name: str
    method_type: str  # "create" | "read" | "update" | "delete" | "query" | "count"
    parameters: List[Tuple[str, str, str]]  # [(name, type, kind), ...] kind: 'positional' | 'keyword-only'
    return_type: str
    is_static: bool
    docstring: Optional[str]
    has_transaction: bool  # 是否需要事务测试
    is_soft_delete: bool = False  # 是否是软删除方法（设置is_deleted/is_active）
    is_specialized_update: bool = False  # 是否是专用更新方法（如update_login_info）


@dataclass
class RepositoryInfo:
    """Repository类信息"""
    
    name: str  # CategoryRepository
    model_name: str  # Category
    methods: List[RepositoryMethodInfo]
    docstring: Optional[str]
    
    
@dataclass
class ModuleStructure:
    """模块完整结构信息（四层架构标准）
    
    项目标准要求所有模块必须实现完整的四层架构：
    - Router层: 处理HTTP请求和响应
    - Service层: 实现业务逻辑
    - Repository层: 处理数据访问（必需）
    - Model层: 定义数据模型
    """
    
    models: Dict[str, ModelInfo]
    repositories: Dict[str, RepositoryInfo]  # 必需，不可为空
