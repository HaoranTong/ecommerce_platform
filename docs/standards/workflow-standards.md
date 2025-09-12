<!--
文档说明：
- 内容：标准化开发工作流程，从需求到部署的完整流程
- 使用方法：每次开发新功能时严格按照此流程执行
- 更新方法：开发流程优化时更新，需要团队确认
- 引用关系：被MASTER.md引用，是开发工作的核心指导
- 更新频率：开发流程改进时
-->

# 开发工作流程

## 开发阶段划分

### Phase 1: 需求准备阶段
**目标**: 确保需求清晰明确，技术方案可行

#### 1.1 需求分析
- [ ] 阅读 [业务需求](../requirements/business.md) 理解项目背景
- [ ] 查看 [功能需求](../requirements/functional.md) 了解具体功能要求
- [ ] 确认 [非功能需求](../requirements/non-functional.md) 的技术约束
- [ ] 识别功能依赖关系和集成点

#### 1.2 技术方案设计
- [ ] 遵循 [架构总览](../architecture/overview.md) 的技术栈选择
- [ ] 按照 [API设计标准](api-standards.md) 设计接口
- [ ] 遵循 [数据库设计规范](database-standards.md) 设计数据结构
- [ ] 考虑 [安全架构](../architecture/security.md) 要求
- [ ] 规划 [第三方集成](../architecture/integration.md) 需求

#### 1.3 模块文档创建
- [ ] 在 `docs/modules/{module-name}/` 创建模块目录
- [ ] 编写 `requirements.md` - 详细功能需求
- [ ] 编写 `design.md` - 技术设计方案
- [ ] 编写 `api-spec.md` - API接口规范
- [ ] 创建 `implementation.md` - 开发记录文档

### Phase 2: 开发实施阶段
**目标**: 高质量代码实现，完整测试覆盖

#### 2.1 环境准备
```powershell
# 1. 配置开发环境
. .\dev_env.ps1

# 2. 检查数据库连接
.\dev_tools.ps1 check-db

# 3. 创建功能分支
git checkout -b feature/{module-name}

# 4. 更新依赖
pip install -r requirements.txt
```

#### 2.2 代码开发标准
- [ ] **数据模型** - 在 `app/models.py` 中定义 SQLAlchemy 模型
- [ ] **API路由** - 在 `app/api/{module}_routes.py` 中实现路由
- [ ] **数据验证** - 在 `app/api/schemas.py` 中定义 Pydantic 模式
- [ ] **业务逻辑** - 在 `app/services/` 中实现服务层
- [ ] **错误处理** - 统一异常处理和错误响应

#### 2.3 代码质量要求
```python
# 示例：完整的功能实现结构
# app/models.py
class Product(Base):
    __tablename__ = 'products'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(200), nullable=False)
    # ... 完整字段定义

# app/api/schemas.py
class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    price: Decimal = Field(..., gt=0)
    # ... 完整验证规则

# app/api/product_routes.py
@router.post("/products", response_model=ProductResponse)
async def create_product(product_data: ProductCreateRequest):
    # 完整的业务逻辑实现
    pass

# app/services/product_service.py
class ProductService:
    @staticmethod
    def create_product(product_data: ProductCreateRequest) -> Product:
        # 完整的业务逻辑实现
        pass
```

#### 2.4 实时记录和更新
- [ ] 更新 `docs/modules/{module}/implementation.md` 记录开发进展
- [ ] 更新 `docs/status/daily-log.md` 记录每日工作
- [ ] 遇到问题时更新 `docs/status/issues-tracking.md`

### Phase 3: 测试验证阶段
**目标**: 确保功能正确性和系统稳定性

#### 3.1 单元测试
```python
# tests/test_{module}.py
import pytest
from app.services.product_service import ProductService

class TestProductService:
    def test_create_product_success(self):
        # 测试正常情况
        product_data = ProductCreateRequest(
            name="测试商品",
            price=99.99,
            category_id=1
        )
        result = ProductService.create_product(product_data)
        assert result.id is not None
        assert result.name == "测试商品"
    
    def test_create_product_invalid_price(self):
        # 测试异常情况
        with pytest.raises(ValidationError):
            ProductCreateRequest(
                name="测试商品",
                price=-1,  # 无效价格
                category_id=1
            )
```

#### 3.2 集成测试
```python
# tests/test_integration_{module}.py
import pytest
from fastapi.testclient import TestClient

class TestProductAPI:
    def test_create_product_api(self, client: TestClient):
        response = client.post("/api/v1/products", json={
            "name": "测试商品",
            "price": 99.99,
            "category_id": 1
        })
        assert response.status_code == 201
        assert response.json()["data"]["name"] == "测试商品"
```

#### 3.3 API测试
```powershell
# 运行API测试
.\dev_tools.ps1 test-api

# 运行特定模块测试
pytest tests/test_products.py -v

# 运行覆盖率测试
pytest --cov=app tests/
```

#### 3.4 系统测试
```powershell
# 烟雾测试
.\scripts\smoke_test.ps1

# 性能测试（如果需要）
# 使用locust或类似工具进行负载测试
```

### Phase 4: 文档完善阶段
**目标**: 完整准确的技术文档

#### 4.1 API文档更新
- [ ] 更新 `docs/modules/{module}/api-spec.md`
- [ ] 确保OpenAPI规范同步更新
- [ ] 添加完整的请求响应示例
- [ ] 说明错误处理和状态码

#### 4.2 模块文档完善
- [ ] 完善 `docs/modules/{module}/design.md` 技术设计
- [ ] 更新 `docs/modules/{module}/implementation.md` 实现细节
- [ ] 记录已知问题和解决方案
- [ ] 添加使用示例和最佳实践

#### 4.3 总结文档
- [ ] 创建 `docs/modules/{module}/summary.md` 完成总结
- [ ] 包含功能清单、技术要点、测试结果
- [ ] 记录经验教训和改进建议

### Phase 5: 代码提交阶段
**目标**: 规范化代码提交和版本管理

#### 5.1 提交前检查
```powershell
# 1. 运行所有测试
pytest tests/ -v

# 2. 检查代码质量
# (如果配置了flake8等工具)

# 3. 确保数据库迁移正确
alembic upgrade head

# 4. 运行烟雾测试
.\scripts\smoke_test.ps1
```

#### 5.2 自动化提交
```powershell
# 使用自动化脚本提交功能
.\scripts\feature_finish.ps1

# 脚本会自动执行：
# - 代码提交和推送
# - 运行测试验证
# - 合并到dev分支
# - 运行集成测试
```

#### 5.3 手动提交流程
```powershell
# 如果不使用自动化脚本
git add .
git commit -m "feat: 实现{模块名}功能

- 完成{具体功能1}
- 完成{具体功能2}
- 添加相关测试用例
- 更新API文档

Closes #issue_number"

git push origin feature/{module-name}

# 切换到dev分支并合并
git checkout dev
git pull origin dev
git merge feature/{module-name}
git push origin dev
```

## 开发规范和约束

### 代码质量标准
1. **功能完整性** - 所有功能按需求规范实现
2. **错误处理** - 完善的异常处理和错误响应
3. **数据验证** - 严格的输入验证和数据校验
4. **性能考虑** - 合理的数据库查询和缓存使用
5. **安全性** - 遵循安全规范和最佳实践

### 禁止的做法
- ❌ 为通过测试而简化业务逻辑
- ❌ 跳过必要的数据验证
- ❌ 硬编码配置信息
- ❌ 忽略错误处理
- ❌ 不更新相关文档

### 必须的做法
- ✅ 完整的字段验证
- ✅ 完整的错误处理
- ✅ 完整的业务逻辑实现
- ✅ 完整的测试覆盖
- ✅ 及时更新文档

### 数据库操作规范
```python
# 正确的数据库操作示例
def create_product(db: Session, product_data: ProductCreateRequest) -> Product:
    # 1. 数据验证
    if db.query(Product).filter(Product.sku == product_data.sku).first():
        raise HTTPException(status_code=400, detail="SKU已存在")
    
    # 2. 创建对象
    product = Product(**product_data.dict())
    
    # 3. 事务处理
    try:
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="创建商品失败")
```

### API设计规范
```python
# 正确的API设计示例
@router.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(
    product_data: ProductCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建商品
    
    - **name**: 商品名称，必填，1-200字符
    - **price**: 商品价格，必填，大于0
    - **category_id**: 分类ID，必填，必须存在
    """
    # 权限检查
    if not current_user.has_permission("create:products"):
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 业务逻辑
    try:
        product = ProductService.create_product(db, product_data)
        return ProductResponse.from_orm(product)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建商品失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")
```

## 故障排除流程

### 开发问题排查
1. **检查日志** - 查看应用和数据库日志
2. **验证配置** - 确认环境变量和配置文件
3. **测试连接** - 验证数据库和Redis连接
4. **运行诊断** - 使用开发工具进行检查

### 常见问题解决
```powershell
# 数据库连接问题
.\dev_tools.ps1 check-db

# 重置开发环境
.\dev_tools.ps1 reset-env

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f
```

### 测试失败处理
1. **分析失败原因** - 查看测试输出和错误信息
2. **检查测试数据** - 确认测试数据是否正确
3. **验证业务逻辑** - 检查实现是否符合需求
4. **修复并重测** - 修复问题后重新运行测试

## 版本发布流程

### 开发版本发布
```powershell
# 发布到主分支（预览模式）
.\scripts\release_to_main.ps1 -DryRun

# 确认无误后正式发布
.\scripts\release_to_main.ps1 -RunNow
```

### 版本标记
```powershell
# 创建版本标签
git tag -a v1.1.0 -m "Release version 1.1.0

新增功能:
- 商品管理模块
- 购物车功能优化
- API性能提升

修复问题:
- 修复库存同步问题
- 修复用户权限验证

其他改进:
- 优化数据库查询
- 完善错误处理"

git push origin v1.1.0
```

### 发布后验证
1. **运行烟雾测试** - 验证核心功能正常
2. **检查监控指标** - 确认系统运行正常
3. **更新状态文档** - 记录发布信息和状态
4. **通知相关人员** - 发布完成通知
