# Repository 层单元测试

本目录包含所有模块的 Repository 层（数据访问层）单元测试文件。

## 📋 测试策略

### 四层架构 - Repository 层定位
```
Router → Service → Repository → Model
                      ↑
                   测试焦点
```

Repository 层负责：
- 数据库CRUD操作
- 复杂查询逻辑
- 数据过滤和排序
- 事务管理
- 数据持久化

## 🎯 测试重点

### 1. CRUD 操作测试
- **Create**: 验证数据正确插入，ID自动生成，时间戳设置
- **Read**: 验证查询条件、过滤逻辑、数据完整性
- **Update**: 验证字段更新、事务提交、乐观锁
- **Delete**: 验证软删除/硬删除、级联删除、数据清理

### 2. 查询逻辑测试
- 单条记录查询（by ID, by unique field）
- 列表查询（分页、排序、过滤）
- 聚合查询（count, sum, avg）
- 关联查询（join, eager loading）

### 3. 事务处理测试
- 事务提交成功
- 事务回滚（错误场景）
- 并发事务处理
- 死锁处理

### 4. 边界情况测试
- 记录不存在
- 重复数据插入
- 外键约束违反
- 数据验证失败

## 💾 数据库策略

**使用 SQLite 内存数据库 (unit_test_db fixture)**

优势：
- ✅ 快速执行（内存操作）
- ✅ 测试隔离（每个测试独立数据库）
- ✅ 真实SQL操作（非Mock）
- ✅ 支持事务和外键约束

```python
def test_category_repository_create(unit_test_db: Session):
    """测试 CategoryRepository.create - 成功创建"""
    # 准备测试数据
    category = Category(name="电子产品", slug="electronics")
    
    # 执行Repository方法
    result = CategoryRepository.create(unit_test_db, category)
    
    # 验证结果
    assert result.id is not None  # ID已生成
    assert result.created_at is not None  # 时间戳已设置
    
    # 验证数据已持久化
    db_category = unit_test_db.query(Category).filter_by(id=result.id).first()
    assert db_category is not None
    assert db_category.name == "电子产品"
```

## 📝 测试文件组织

```
test_repositories/
├── README.md (本文件)
├── test_product_catalog_repositories.py  # 产品目录 Repository 测试
├── test_user_auth_repositories.py        # 用户认证 Repository 测试
├── test_order_management_repositories.py # 订单管理 Repository 测试
└── test_inventory_repositories.py        # 库存管理 Repository 测试
```

## 🔧 测试模板

### 基本结构
```python
"""
产品目录模块 Repository 层测试

测试类型: 单元测试 - Repository 数据访问层
数据策略: SQLite 内存数据库
测试重点: CRUD操作、查询逻辑、事务处理
"""

import pytest
from sqlalchemy.orm import Session
from app.modules.product_catalog.models import Category
from app.modules.product_catalog.repository import CategoryRepository


@pytest.mark.repositories
@pytest.mark.unit
class TestCategoryRepository:
    """CategoryRepository 测试类"""
    
    def test_create_success(self, unit_test_db: Session):
        """测试 create - 成功创建"""
        # 准备测试数据
        category = Category(name="测试分类")
        
        # 执行操作
        result = CategoryRepository.create(unit_test_db, category)
        
        # 验证结果
        assert result.id is not None
        assert result.name == "测试分类"
    
    def test_get_by_id_found(self, unit_test_db: Session):
        """测试 get_by_id - 查询到数据"""
        # 准备数据
        category = Category(name="测试分类")
        unit_test_db.add(category)
        unit_test_db.commit()
        
        # 执行查询
        result = CategoryRepository.get_by_id(unit_test_db, category.id)
        
        # 验证结果
        assert result is not None
        assert result.id == category.id
    
    def test_get_by_id_not_found(self, unit_test_db: Session):
        """测试 get_by_id - 数据不存在"""
        result = CategoryRepository.get_by_id(unit_test_db, 99999)
        assert result is None
```

## 🚀 运行测试

```bash
# 运行所有 Repository 测试
pytest tests/unit/test_repositories/ -v

# 运行特定模块的 Repository 测试
pytest tests/unit/test_repositories/test_product_catalog_repositories.py -v

# 运行特定测试方法
pytest tests/unit/test_repositories/test_product_catalog_repositories.py::TestCategoryRepository::test_create_success -v

# 显示详细输出
pytest tests/unit/test_repositories/ -v -s

# 仅运行 repositories 标记的测试
pytest -m repositories -v
```

## ⚠️ 注意事项

### 1. 不要 Mock 数据库操作
❌ **错误**：使用 Mock 模拟 `db.add()`, `db.commit()`
```python
# 错误示例
def test_create_with_mock(mocker):
    mock_db = mocker.Mock()
    mock_db.add.return_value = None  # 不要这样做！
```

✅ **正确**：使用真实的 SQLite 内存数据库
```python
# 正确示例
def test_create_with_real_db(unit_test_db: Session):
    category = Category(name="测试")
    unit_test_db.add(category)
    unit_test_db.commit()  # 真实的数据库操作
```

### 2. 测试隔离
- 每个测试使用独立的数据库会话
- `unit_test_db` fixture 自动处理数据清理
- 不依赖其他测试的数据

### 3. 测试数据准备
- 使用真实的 Model 对象
- 避免硬编码 ID
- 测试完整的业务场景

### 4. 断言验证
- 验证返回值正确性
- 验证数据库状态变更
- 验证事务提交成功
- 验证错误处理逻辑

## 📚 相关文档

- [测试标准文档](../../../docs/standards/testing-standards.md)
- [四层架构规范](../../../docs/architecture/)
- [产品目录模块设计](../../../docs/design/product-catalog/)
- [conftest.py 配置](../../conftest.py)

## 🎓 最佳实践

1. **测试命名清晰**：`test_{方法名}_{场景}_{预期结果}`
2. **AAA 模式**：Arrange（准备）- Act（执行）- Assert（断言）
3. **测试独立性**：每个测试可独立运行
4. **覆盖边界情况**：成功、失败、边界、异常
5. **性能意识**：单个测试 < 2秒

---

**符合标准**: [CHECK:TEST-001] [CHECK:DEV-009]
**架构层级**: Repository 层（数据访问层）
**测试类型**: 单元测试 - SQLite 内存数据库
