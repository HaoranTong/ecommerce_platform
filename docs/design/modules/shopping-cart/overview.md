<!--
文档说明：
- 内容：模块文档标准模板，用于创建新的模块文档  
- 使用方法：复制此模板，替换模板变量，填入具体内容
- 更新方法：模板规范变更时由架构师更新
- 引用关系：被所有模块文档使用
- 更新频率：模板标准变化时

⚠️ 强制文档要求：
每个模块必须包含以下7个文档（无可选项）：
1. README.md - 模块导航（简洁版入口）
2. overview.md - 模块概述（本模板，详细版）
3. requirements.md - 业务需求文档（强制）
4. design.md - 设计决策文档（强制）
5. api-spec.md - API规范文档（强制）
6. api-implementation.md - API实施记录（强制）
7. implementation.md - 实现细节文档（强制）
-->

# 购物车模块 (Shopping Cart)

📝 **状态**: 🔄 开发中  
📅 **创建日期**: 2025-09-16  
👤 **负责人**: 开发团队  
🔄 **最后更新**: 2025-09-16  
📋 **版本**: v1.0.0  

## 模块概述

### 主要职责
购物车模块是电商平台的核心交易准备模块，负责管理用户购物意向：
- **购物车管理**: 提供完整的购物车CRUD操作功能
- **库存验证**: 实时验证商品库存状态，防止超卖
- **价格计算**: 动态计算商品小计和购物车总价
- **数据持久化**: 基于Redis+MySQL的高性能数据存储
- **用户体验**: 提供流畅的购物车操作体验

### 业务价值
- **核心价值**: 作为购物到订单的关键桥梁，直接影响电商平台转化率和用户体验
- **用户收益**: 方便用户收集心仪商品、比较选择、批量结算，提升购物效率
- **系统收益**: 缓存用户购买意向、减少重复商品查询、为推荐系统提供数据支持

### 模块边界
- **包含功能**: 购物车CRUD、库存验证、价格计算、缓存管理、数据同步
- **排除功能**: 订单创建、支付处理、商品管理、用户认证、促销计算
- **依赖模块**: user_auth(认证)、product_catalog(商品)、inventory_management(库存)
- **被依赖**: order_management(订单)、recommendation_system(推荐)

## 技术架构

### 架构图
```mermaid
graph TB
    subgraph "购物车模块架构"
        A[API Router] --> B[Service Layer]
        B --> C[Repository Layer]
        C --> D[Redis Cache]
        C --> E[MySQL Database]
        
        B --> F[Dependencies]
        F --> G[User Auth]
        F --> H[Product Catalog]
        F --> I[Inventory Service]
        
        J[Models & Schemas] --> B
        K[Utils & Helpers] --> B
    end
    
    subgraph "外部系统"
        L[用户请求] --> A
        A --> M[响应数据]
    end
```

### 核心组件
```
shopping_cart/
├── router.py           # 购物车API路由：CRUD接口定义
├── service.py          # 业务逻辑层：购物车操作、库存验证、价格计算
├── models.py           # 数据模型：Cart、CartItem实体定义
├── schemas.py          # 请求响应模型：API输入输出格式
├── dependencies.py     # 依赖注入：认证、权限、服务依赖
└── README.md           # 模块简介和快速导航
```

### 模块化单体架构
- **架构模式**: 模块化单体架构 (Modular Monolith)
- **垂直切片**: 每个模块包含完整的业务功能
- **依赖原则**: 依赖注入和接口抽象

### 核心基础设施
```
app/core/               # 核心基础设施
├── database.py         # 数据库连接管理
├── redis_client.py     # Redis缓存客户端  
├── auth.py             # 认证中间件
└── __init__.py         # 核心组件导出
```

### 适配器集成
```
app/adapters/           # 第三方服务适配器
├── {service_type}/     # 服务类型目录
│   ├── {provider}_adapter.py
│   └── config.py
```

### 技术栈
- **编程语言**: Python 3.11+
- **Web框架**: FastAPI (异步支持、自动文档)
- **数据库**: MySQL 8.0 (主存储) + Redis (缓存)
- **ORM**: SQLAlchemy 2.0 (异步支持)
- **缓存**: Redis 7.0 (分布式缓存、会话存储)
- **认证**: JWT Token + FastAPI Security

### 设计模式
- **使用的设计模式**: 如Repository、Factory、Strategy等
- **架构模式**: 如Clean Architecture、DDD等
- **代码组织**: 分层架构说明

## 核心功能

### 功能列表
| 功能名称 | 优先级 | 状态 | 描述 |
|---------|--------|------|------|
| 添加商品到购物车 | P0 | ⏳ 待开始 | 验证库存后将商品添加到购物车 |
| 查看购物车内容 | P0 | ⏳ 待开始 | 显示购物车所有商品和价格信息 |
| 修改商品数量 | P0 | ⏳ 待开始 | 更新购物车商品数量并重新计算价格 |
| 删除购物车商品 | P0 | ⏳ 待开始 | 移除购物车中的指定商品 |
| 清空购物车 | P1 | ⏳ 待开始 | 一键清空整个购物车 |
| 批量操作 | P2 | ⏳ 待开始 | 支持批量添加、删除商品 |

### 核心业务流程
```mermaid
graph TD
    A[用户选择商品] --> B[点击加入购物车]
    B --> C[验证用户登录状态]
    C --> D{用户已登录?}
    D -->|否| E[跳转登录页面]
    D -->|是| F[验证商品库存]
    F --> G{库存充足?}
    G -->|否| H[提示库存不足]
    G -->|是| I[检查购物车商品限制]
    I --> J{是否超出限制?}
    J -->|是| K[提示商品数量限制]
    J -->|否| L[添加/更新购物车]
    L --> M[更新Redis缓存]
    M --> N[同步MySQL数据]
    N --> O[返回购物车最新状态]
    O --> P[更新前端显示]
```

### 业务规则
1. **用户权限规则**: 只有登录用户才能操作购物车，每个用户只能访问自己的购物车数据
2. **库存验证规则**: 添加商品前必须验证库存，库存不足时禁止添加并提示用户
3. **数量限制规则**: 单个SKU最大数量999个，购物车最多包含50个不同商品
4. **价格计算规则**: 实时计算商品小计和总价，保留2位小数精度
5. **数据一致性规则**: Redis和MySQL双写保证数据一致性，Redis故障时降级到MySQL
6. **缓存策略规则**: 购物车数据优先从Redis读取，写操作同时更新缓存和数据库

## 数据模型

### 核心实体
```python
# 购物车主表
class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

# 购物车商品项
class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Decimal(10, 2), nullable=False)  # 加入时的单价
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 唯一约束
    __table_args__ = (UniqueConstraint('cart_id', 'sku_id'),)
    
    # 关联关系
    cart = relationship("Cart", back_populates="items")
```

### 数据关系图
```mermaid
erDiagram
    USERS ||--|| CARTS : "1:1"
    CARTS ||--o{ CART_ITEMS : "1:N"
    PRODUCTS ||--o{ CART_ITEMS : "1:N"
    
    USERS {
        int id PK
        string username
        string email
    }
    
    CARTS {
        int id PK
        int user_id FK
        datetime created_at
        datetime updated_at
    }
    
    CART_ITEMS {
        int id PK
        int cart_id FK
        int sku_id FK
        int quantity
        decimal unit_price
        datetime created_at
        datetime updated_at
    }
    
    PRODUCTS {
        int id PK
        string name
        decimal price
        int stock_quantity
    }
```

### 数据约束
- **唯一性约束**: 每个用户只有一个购物车(user_id唯一)，购物车中每个SKU只有一条记录
- **外键约束**: cart_id关联购物车表，sku_id关联商品表，user_id关联用户表
- **业务约束**: 商品数量必须大于0且小于等于999，单价必须大于0

## API接口

### 接口列表
| 接口 | 方法 | 路径 | 描述 | 状态 |
|------|------|------|------|------|
| 添加商品到购物车 | POST | /api/v1/shopping-cart/items | 添加商品到购物车或更新数量 | ⏳ 待开发 |
| 获取购物车 | GET | /api/v1/shopping-cart/cart | 获取当前用户的购物车内容 | ⏳ 待开发 |
| 更新商品数量 | PUT | /api/v1/shopping-cart/items/{item_id} | 修改购物车中商品的数量 | ⏳ 待开发 |
| 删除商品 | DELETE | /api/v1/shopping-cart/items/{item_id} | 从购物车删除指定商品 | ⏳ 待开发 |
| 批量删除 | DELETE | /api/v1/shopping-cart/items | 批量删除购物车商品 | ⏳ 待开发 |
| 清空购物车 | DELETE | /api/v1/shopping-cart/cart | 清空整个购物车 | ⏳ 待开发 |

### 接口详情示例
```yaml
/api/v1/shopping-cart/items:
  post:
    summary: 添加商品到购物车
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              sku_id:
                type: integer
                description: 商品SKU ID
              quantity:
                type: integer
                minimum: 1
                maximum: 999
                description: 商品数量
    responses:
      200:
        description: 添加成功
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CartResponse'
      400:
        description: 请求参数错误或库存不足
```

### 错误码
| 错误码 | 状态码 | 描述 | 解决方案 |
|--------|--------|------|----------|
| CART_001 | 400 | 商品数量参数错误 | 检查数量范围1-999 |
| CART_002 | 400 | 商品库存不足 | 减少商品数量或选择其他商品 |
| CART_003 | 400 | 购物车商品数量超限 | 购物车最多50个不同商品 |
| CART_004 | 404 | 商品不存在 | 确认商品ID正确性 |
| CART_005 | 409 | 商品已下架 | 选择其他在售商品 |

## 测试策略

### 测试覆盖率目标
- **单元测试**: ≥ 85%
- **集成测试**: ≥ 70%
- **端到端测试**: 核心业务流程100%

### 测试类型
```python
# 单元测试示例
class TestCartService:
    def test_add_item_success(self):
        # 测试成功添加商品到购物车
        pass
    
    def test_add_item_insufficient_stock(self):
        # 测试库存不足情况
        pass
    
    def test_update_item_quantity(self):
        # 测试更新商品数量
        pass

# 集成测试示例  
class TestCartAPI:
    def test_cart_crud_workflow(self):
        # 测试购物车完整CRUD流程
        pass
        
    def test_inventory_integration(self):
        # 测试与库存系统的集成
        pass
```

### 性能测试
- **响应时间**: API响应时间 < 100ms (P95)
- **并发处理**: 支持8000并发用户操作
- **数据量**: 支持100万活跃购物车，单购物车50个商品

### 测试数据
- **测试数据生成**: Factory Boy或自定义工厂
- **数据清理**: 每个测试后清理测试数据
- **Mock策略**: 外部依赖的Mock策略

## 部署和运维

### 环境要求
- **开发环境**: 本地开发环境配置
- **测试环境**: 测试环境配置要求
- **生产环境**: 生产环境配置要求

### 配置管理
```python
# 购物车模块环境变量配置
CART_REDIS_URL=redis://localhost:6379/1
CART_CACHE_TTL=3600  # 购物车缓存过期时间(秒)
CART_MAX_ITEMS=50    # 购物车最大商品种类数
CART_MAX_QUANTITY=999 # 单商品最大数量
CART_DATABASE_URL=mysql://user:pass@localhost/ecommerce
```

### 监控指标
- **业务指标**: 购物车转化率、平均商品数量、添加/删除操作频率
- **技术指标**: API响应时间、Redis命中率、数据库查询时间、错误率
- **资源指标**: Redis内存使用、数据库连接池、CPU和内存使用率

### 告警规则
- **错误率**: > 1% 触发告警 (购物车操作失败率)
- **响应时间**: > 100ms 触发告警 (API响应时间)
- **缓存命中率**: < 85% 触发告警 (Redis缓存效果)
- **资源使用**: > 80% 触发告警 (Redis内存、数据库连接)

## 安全考虑

### 认证授权
- **身份认证**: JWT Token验证
- **权限控制**: 基于角色的访问控制
- **API安全**: Rate Limiting、CORS等

### 数据安全
- **数据加密**: 敏感数据加密存储
- **传输安全**: HTTPS传输
- **输入验证**: 严格的输入验证

### 审计日志
- **操作日志**: 记录关键操作
- **访问日志**: 记录API访问
- **安全日志**: 记录安全相关事件

## 性能优化

### 缓存策略
- **Redis缓存**: 购物车数据优先存储在Redis，TTL设置为1小时
- **本地缓存**: 商品信息和价格数据本地缓存10分钟
- **查询缓存**: 频繁查询结果缓存，减少数据库压力

### 数据库优化
- **索引优化**: user_id、sku_id、cart_id建立索引，复合索引(cart_id, sku_id)
- **查询优化**: 批量查询减少数据库往返，使用JOIN优化关联查询
- **连接池**: 配置最大20个连接，最小5个连接的连接池

### 扩展性设计
- **水平扩展**: 支持多实例部署，Redis集群化，数据库读写分离
- **垂直扩展**: 根据负载自动调整资源配置，支持容器化部署
- **降级策略**: Redis故障时降级到MySQL，保证基本功能可用

## 问题和风险

### 已知问题
| 问题ID | 描述 | 优先级 | 状态 | 解决方案 |
|--------|------|--------|------|----------|
| CART-001 | 高并发下库存数据不一致 | 高 | 🔄 待处理 | 使用Redis分布式锁+乐观锁机制 |

### 技术风险
- **Redis故障风险**: Redis缓存不可用影响性能，缓解措施：实现降级到MySQL+Redis集群
- **库存超卖风险**: 高并发场景下可能超卖，缓解措施：分布式锁+事务控制
- **数据一致性风险**: 缓存与数据库数据不一致，缓解措施：双写策略+最终一致性保证

### 技术债务
- **缓存预热机制**: 需要实现系统启动时的缓存预热，提升首次访问性能
- **批量操作优化**: 当前单个操作较多，需要实现批量添加/删除功能

## 开发计划

### 里程碑
- **M1**: 核心CRUD功能开发 (预计: 第1周)
- **M2**: 库存集成和缓存实现 (预计: 第2周)  
- **M3**: 性能优化和测试完善 (预计: 第3周)

### 任务分解
- [ ] 数据模型设计和实现 (负责人: 后端开发, 预计: 2天)
- [ ] Redis缓存集成 (负责人: 后端开发, 预计: 2天)
- [ ] API接口实现 (负责人: 后端开发, 预计: 3天)
- [ ] 库存服务集成 (负责人: 后端开发, 预计: 2天)
- [ ] 单元测试和集成测试 (负责人: 测试工程师, 预计: 2天)
- [ ] 性能测试和优化 (负责人: 全栈开发, 预计: 2天)

## 相关文档

### 架构文档
- [系统架构总览](../architecture/overview.md)
- [API设计规范](../architecture/api-standards.md)
- [数据模型规范](../architecture/data-models.md)

### 开发文档
- [开发规范](../development/development-standards.md)
- [测试指南](../development/testing.md)
- [部署指南](../operations/deployment.md)

### 需求文档
- [功能需求规范](../requirements/functional.md)
- [购物车业务需求](./requirements.md)

### 依赖模块
- [用户认证模块](../user_auth/overview.md)
- [商品目录模块](../product_catalog/overview.md)
- [库存管理模块](../inventory_management/overview.md)

### 被依赖模块
- [订单管理模块](../order_management/overview.md)
- [推荐系统模块](../recommendation_system/overview.md)

---

📝 **模板使用说明**:
1. 复制此模板创建新的模块文档
2. 替换所有 `{变量}` 为实际值
3. 删除不适用的章节
4. 根据模块特点调整章节内容
5. 保持文档及时更新

