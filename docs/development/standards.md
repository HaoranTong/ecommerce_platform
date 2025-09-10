<!--
文档说明：
- 内容：开发过程中使用的标准、规范和最佳实践
- 使用方法：开发时作为编码规范参考，代码审查时对照检查
- 更新方法：团队讨论确定新标准后更新，需要全员确认
- 引用关系：被workflow.md引用，指导日常开发工作
- 更新频率：技术栈升级或最佳实践变更时
-->

# 开发标准与规范

## 项目架构规范

### 目录结构标准
```
app/
├── main.py              # FastAPI应用入口
├── config.py            # 配置管理
├── database.py          # 数据库连接配置
├── models/             # 数据模型层
│   ├── __init__.py
│   ├── base.py         # 基础模型
│   ├── user.py         # 用户模型
│   ├── product.py      # 商品模型
│   └── order.py        # 订单模型
├── schemas/            # API数据模式
│   ├── __init__.py
│   ├── base.py         # 基础模式
│   ├── user.py         # 用户相关模式
│   ├── product.py      # 商品相关模式
│   └── order.py        # 订单相关模式
├── api/                # API路由层
│   ├── __init__.py
│   ├── v1/             # API版本1
│   │   ├── __init__.py
│   │   ├── users.py    # 用户相关API
│   │   ├── products.py # 商品相关API
│   │   └── orders.py   # 订单相关API
│   └── dependencies.py # 依赖注入
├── services/           # 业务逻辑层
│   ├── __init__.py
│   ├── user_service.py
│   ├── product_service.py
│   └── order_service.py
├── utils/              # 工具函数
│   ├── __init__.py
│   ├── security.py     # 安全相关工具
│   ├── validators.py   # 验证工具
│   └── helpers.py      # 通用助手函数
└── tests/              # 测试文件
    ├── __init__.py
    ├── test_models.py
    ├── test_services.py
    └── test_api/
        ├── test_users.py
        ├── test_products.py
        └── test_orders.py
```

### 分层架构原则
1. **API层 (api/)** - 处理HTTP请求，数据序列化
2. **服务层 (services/)** - 业务逻辑实现，事务管理
3. **模型层 (models/)** - 数据库模型定义
4. **模式层 (schemas/)** - 数据验证和序列化
5. **工具层 (utils/)** - 通用功能组件

### 依赖关系规则
```
API层 -> 服务层 -> 模型层
     \-> 模式层 -> 模型层
           \-> 工具层
```

## 编码规范

### Python代码规范
遵循 PEP 8 和项目特定规范：

#### 命名约定
```python
# 类名使用大驼峰命名
class ProductService:
    pass

class UserModel:
    pass

# 函数和变量使用小写下划线命名
def create_product(product_data):
    pass

user_name = "example"
product_list = []

# 常量使用大写下划线命名
MAX_PAGE_SIZE = 100
DEFAULT_TIMEOUT = 30
API_VERSION = "v1"

# 私有属性和方法使用单下划线前缀
class Service:
    def __init__(self):
        self._internal_state = {}
    
    def _helper_method(self):
        pass
```

#### 文档字符串规范
```python
def create_product(
    db: Session, 
    product_data: ProductCreateRequest,
    current_user: User
) -> Product:
    """
    创建新商品
    
    Args:
        db (Session): 数据库会话
        product_data (ProductCreateRequest): 商品创建数据
        current_user (User): 当前用户
    
    Returns:
        Product: 创建的商品对象
    
    Raises:
        ValidationError: 数据验证失败
        PermissionError: 权限不足
        IntegrityError: 数据完整性约束违反
    
    Example:
        >>> product_data = ProductCreateRequest(
        ...     name="新商品",
        ...     price=99.99,
        ...     category_id=1
        ... )
        >>> product = create_product(db, product_data, user)
        >>> print(product.id)
        123
    """
    pass
```

#### 类型注解规范
```python
from typing import List, Optional, Dict, Any, Union
from decimal import Decimal
from datetime import datetime

# 函数参数和返回值必须有类型注解
def get_products(
    db: Session,
    category_id: Optional[int] = None,
    page: int = 1,
    size: int = 20
) -> List[Product]:
    pass

# 类属性类型注解
class ProductResponse:
    id: int
    name: str
    price: Decimal
    created_at: datetime
    category: Optional[str] = None
    
# 复杂类型注解
ProductDict = Dict[str, Any]
ProductList = List[Product]
ProductFilter = Optional[Dict[str, Union[str, int, bool]]]
```

### API设计规范

#### REST API标准
```python
# 资源路径设计
@router.get("/products")                    # 获取商品列表
@router.post("/products")                   # 创建商品
@router.get("/products/{product_id}")       # 获取指定商品
@router.put("/products/{product_id}")       # 更新指定商品
@router.delete("/products/{product_id}")    # 删除指定商品

# 嵌套资源路径
@router.get("/categories/{category_id}/products")     # 获取分类下的商品
@router.post("/orders/{order_id}/items")              # 向订单添加商品

# 操作性端点
@router.post("/products/{product_id}/activate")       # 激活商品
@router.post("/orders/{order_id}/cancel")             # 取消订单
```

#### 请求响应格式
```python
# 统一响应格式
class APIResponse(BaseModel):
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    meta: Optional[Dict[str, Any]] = None

# 分页响应格式
class PaginatedResponse(APIResponse):
    data: List[Any]
    meta: Dict[str, Any] = Field(default_factory=lambda: {
        "page": 1,
        "size": 20,
        "total": 0,
        "pages": 0
    })

# 错误响应格式
class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: List[str]
    error_code: Optional[str] = None
```

#### 状态码使用规范
```python
# 成功响应
@router.post("/products", status_code=201)    # 创建成功
@router.get("/products", status_code=200)     # 查询成功
@router.put("/products/{id}", status_code=200) # 更新成功
@router.delete("/products/{id}", status_code=204) # 删除成功

# 错误响应处理
try:
    result = service.create_product(data)
    return APIResponse(data=result)
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))  # 请求错误
except PermissionError as e:
    raise HTTPException(status_code=403, detail=str(e))  # 权限不足
except NotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))  # 资源不存在
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="内部服务器错误")  # 服务器错误
```

### 数据库规范

#### 模型定义规范
```python
from sqlalchemy import Column, String, Integer, BigInteger, Boolean, DateTime, Decimal, Text
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    """商品模型"""
    __tablename__ = 'products'
    
    # 主键使用BigInteger
    id = Column(BigInteger, primary_key=True, index=True)
    
    # 字符串字段明确长度
    name = Column(String(200), nullable=False, comment='商品名称')
    sku = Column(String(100), unique=True, nullable=False, comment='商品编码')
    description = Column(Text, comment='商品描述')
    
    # 数值字段使用合适类型
    price = Column(Decimal(10, 2), nullable=False, comment='商品价格')
    stock_quantity = Column(Integer, default=0, comment='库存数量')
    
    # 布尔字段有默认值
    is_active = Column(Boolean, default=True, comment='是否启用')
    is_deleted = Column(Boolean, default=False, comment='是否删除')
    
    # 时间字段
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment='更新时间')
    
    # 外键关系
    category_id = Column(BigInteger, ForeignKey('categories.id'), nullable=False, comment='分类ID')
    
    # 关系定义
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    
    # 表级约束
    __table_args__ = (
        Index('idx_product_category', 'category_id'),
        Index('idx_product_sku', 'sku'),
        Index('idx_product_active', 'is_active', 'is_deleted'),
        {'comment': '商品信息表'}
    )
```

#### 查询优化规范
```python
# 避免N+1查询问题
def get_products_with_category(db: Session) -> List[Product]:
    return db.query(Product).options(
        joinedload(Product.category)
    ).filter(
        Product.is_active == True,
        Product.is_deleted == False
    ).all()

# 分页查询
def get_products_paginated(
    db: Session, 
    page: int = 1, 
    size: int = 20
) -> Tuple[List[Product], int]:
    offset = (page - 1) * size
    
    query = db.query(Product).filter(
        Product.is_active == True,
        Product.is_deleted == False
    )
    
    total = query.count()
    products = query.offset(offset).limit(size).all()
    
    return products, total

# 复杂查询使用查询构建器
def search_products(
    db: Session,
    filters: ProductSearchFilters
) -> List[Product]:
    query = db.query(Product)
    
    if filters.category_id:
        query = query.filter(Product.category_id == filters.category_id)
    
    if filters.name:
        query = query.filter(Product.name.ilike(f"%{filters.name}%"))
    
    if filters.price_min:
        query = query.filter(Product.price >= filters.price_min)
    
    if filters.price_max:
        query = query.filter(Product.price <= filters.price_max)
    
    return query.all()
```

### 异常处理规范

#### 自定义异常类
```python
# app/exceptions.py
class BaseAPIException(Exception):
    """API异常基类"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(BaseAPIException):
    """数据验证异常"""
    pass

class NotFoundError(BaseAPIException):
    """资源不存在异常"""
    pass

class PermissionError(BaseAPIException):
    """权限不足异常"""
    pass

class BusinessLogicError(BaseAPIException):
    """业务逻辑异常"""
    pass
```

#### 异常处理装饰器
```python
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def handle_service_exceptions(func):
    """服务层异常处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError:
            raise  # 重新抛出，由API层处理
        except NotFoundError:
            raise  # 重新抛出，由API层处理
        except Exception as e:
            logger.error(f"Service error in {func.__name__}: {e}")
            raise BusinessLogicError("业务处理失败")
    return wrapper

# 使用示例
@handle_service_exceptions
def create_product(db: Session, product_data: ProductCreateRequest) -> Product:
    # 业务逻辑实现
    pass
```

### 测试规范

#### 测试文件组织
```python
# tests/test_services/test_product_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.product_service import ProductService
from app.schemas.product import ProductCreateRequest
from app.exceptions import ValidationError, NotFoundError

class TestProductService:
    """商品服务测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.db_mock = Mock()
        self.service = ProductService()
    
    def test_create_product_success(self):
        """测试成功创建商品"""
        # Arrange
        product_data = ProductCreateRequest(
            name="测试商品",
            price=99.99,
            category_id=1
        )
        
        # Act
        result = self.service.create_product(self.db_mock, product_data)
        
        # Assert
        assert result.name == "测试商品"
        assert result.price == 99.99
        self.db_mock.add.assert_called_once()
        self.db_mock.commit.assert_called_once()
    
    def test_create_product_duplicate_sku(self):
        """测试创建重复SKU商品"""
        # Arrange
        product_data = ProductCreateRequest(
            name="测试商品",
            sku="TEST001",
            price=99.99,
            category_id=1
        )
        self.db_mock.query().filter().first.return_value = Mock()  # 模拟已存在
        
        # Act & Assert
        with pytest.raises(ValidationError, match="SKU已存在"):
            self.service.create_product(self.db_mock, product_data)
    
    @patch('app.services.product_service.logger')
    def test_create_product_database_error(self, mock_logger):
        """测试数据库错误处理"""
        # Arrange
        product_data = ProductCreateRequest(
            name="测试商品",
            price=99.99,
            category_id=1
        )
        self.db_mock.commit.side_effect = Exception("数据库错误")
        
        # Act & Assert
        with pytest.raises(BusinessLogicError):
            self.service.create_product(self.db_mock, product_data)
        
        self.db_mock.rollback.assert_called_once()
        mock_logger.error.assert_called_once()
```

#### 测试数据管理
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Product, Category

@pytest.fixture(scope="session")
def test_db():
    """测试数据库会话"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    
    # 创建测试数据
    test_category = Category(name="测试分类")
    db.add(test_category)
    db.commit()
    
    yield db
    
    db.close()

@pytest.fixture
def sample_product_data():
    """示例商品数据"""
    return {
        "name": "测试商品",
        "sku": "TEST001",
        "price": 99.99,
        "category_id": 1,
        "description": "这是一个测试商品"
    }
```

### 安全规范

#### 输入验证
```python
# 数据模式验证
class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, regex=r'^[^<>]*$')
    price: Decimal = Field(..., gt=0, le=999999.99)
    category_id: int = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=2000)
    
    @validator('name')
    def validate_name(cls, v):
        if '<script>' in v.lower() or '</script>' in v.lower():
            raise ValueError('商品名称包含非法字符')
        return v.strip()
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('价格必须大于0')
        return round(v, 2)  # 保留两位小数
```

#### 权限控制
```python
# 权限检查装饰器
def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user or not current_user.has_permission(permission):
                raise HTTPException(status_code=403, detail="权限不足")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# 使用示例
@router.post("/products")
@require_permission("create:products")
async def create_product(
    product_data: ProductCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass
```

#### 数据脱敏
```python
# 敏感数据脱敏
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    @validator('email')
    def mask_email(cls, v):
        if '@' in v:
            username, domain = v.split('@', 1)
            if len(username) > 2:
                masked_username = username[:2] + '*' * (len(username) - 2)
                return f"{masked_username}@{domain}"
        return v
```

### 性能规范

#### 数据库优化
```python
# 批量操作
def bulk_create_products(db: Session, products_data: List[ProductCreateRequest]):
    products = [Product(**data.dict()) for data in products_data]
    db.bulk_save_objects(products)
    db.commit()

# 查询优化
def get_products_optimized(db: Session, filters: ProductFilters):
    # 使用索引字段进行查询
    query = db.query(Product).filter(Product.is_active == True)
    
    # 避免使用函数在WHERE子句中
    if filters.created_after:
        query = query.filter(Product.created_at >= filters.created_after)
    
    # 只查询需要的字段
    if filters.fields_only:
        query = query.options(load_only('id', 'name', 'price'))
    
    return query.all()
```

#### 缓存策略
```python
from functools import lru_cache
import redis

# 内存缓存
@lru_cache(maxsize=128)
def get_category_tree():
    """获取分类树结构，使用内存缓存"""
    # 实现分类树查询逻辑
    pass

# Redis缓存
class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    def get_product(self, product_id: int) -> Optional[Product]:
        cache_key = f"product:{product_id}"
        cached_data = self.redis_client.get(cache_key)
        
        if cached_data:
            return Product.parse_raw(cached_data)
        
        return None
    
    def set_product(self, product: Product, expire_seconds: int = 3600):
        cache_key = f"product:{product.id}"
        self.redis_client.setex(
            cache_key, 
            expire_seconds, 
            product.json()
        )
```

## 代码审查标准

### 审查清单
#### 功能实现
- [ ] 功能完整实现，满足需求规范
- [ ] 边界条件和异常情况处理完善
- [ ] 业务逻辑正确，符合设计文档
- [ ] API接口设计合理，响应格式统一

#### 代码质量
- [ ] 代码风格符合项目规范
- [ ] 变量和函数命名清晰有意义
- [ ] 函数职责单一，复杂度合理
- [ ] 注释和文档字符串完整

#### 安全性
- [ ] 输入验证充分，防止注入攻击
- [ ] 权限控制到位，防止越权访问
- [ ] 敏感数据处理正确，日志脱敏
- [ ] 错误信息不暴露系统内部信息

#### 性能
- [ ] 数据库查询优化，避免N+1问题
- [ ] 合理使用缓存，减少重复计算
- [ ] 批量操作代替循环单个操作
- [ ] 内存使用合理，避免内存泄漏

#### 测试
- [ ] 单元测试覆盖核心逻辑
- [ ] 测试用例包含正常和异常情况
- [ ] 集成测试覆盖关键业务流程
- [ ] 测试数据独立，不依赖外部环境

### 审查流程
1. **自审** - 开发者提交前自我审查
2. **同行审查** - 其他开发者代码审查
3. **架构审查** - 技术负责人架构设计审查
4. **安全审查** - 安全相关变更的专项审查
5. **性能审查** - 性能关键变更的专项审查

## 工具和配置

### 开发工具配置
```python
# .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}

# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.pylint]
max-line-length = 88
good-names = ["i", "j", "k", "db", "id"]
```

### 质量检查工具
```powershell
# 安装开发工具
pip install black isort pylint mypy pytest pytest-cov

# 代码格式化
black app/ tests/

# 导入排序
isort app/ tests/

# 代码检查
pylint app/

# 类型检查
mypy app/

# 运行测试
pytest tests/ --cov=app --cov-report=html
```
