# 购物车系统技术文档

## 版本信息
- **文档版本**: v1.0
- **创建日期**: 2025-09-09
- **最后更新**: 2025-09-09
- **开发分支**: feature/add-shopping-cart

## 系统概述

购物车系统是电商平台的核心功能模块，提供用户购物车管理功能，包括商品添加、修改、删除和统计等操作。系统采用Redis作为缓存存储，提供高性能的购物车操作体验。

## 技术架构

### 后端技术栈
- **Web框架**: FastAPI 0.104.1
- **数据库**: MySQL 8.0 (主存储)
- **缓存**: Redis 7 (购物车存储)
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT Bearer Token
- **API文档**: OpenAPI 3.0

### 核心组件
1. **RedisCartManager** - 购物车缓存管理器
2. **CartRoutes** - 购物车API路由
3. **CartSchemas** - 数据验证模型
4. **ProductModel** - 商品数据模型

## 数据模型

### Product表结构
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    category_id INTEGER,
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    attributes TEXT,
    images TEXT,
    image_url VARCHAR(500),  -- 主图URL
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Redis数据结构
```
# 购物车Key格式
cart:user:{user_id} -> Hash
  {product_id} -> {quantity}

# 示例
cart:user:123 -> {
  "1": "2",
  "5": "1",
  "10": "3"
}
```

## API接口规范

### 基础信息
- **Base URL**: `http://localhost:8000/api`
- **认证方式**: Bearer Token
- **内容类型**: `application/json`

### 接口列表

#### 1. 添加商品到购物车
```http
POST /cart/add
Authorization: Bearer {token}
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2
}
```

**响应示例**:
```json
{
  "message": "商品已添加到购物车",
  "cart_count": 1,
  "total_quantity": 2
}
```

#### 2. 获取购物车详情
```http
GET /cart
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "user_id": 123,
  "items": [
    {
      "product_id": 1,
      "product_name": "测试商品",
      "product_sku": "TEST-001",
      "price": 99.99,
      "quantity": 2,
      "subtotal": 199.98,
      "stock_quantity": 50,
      "image_url": "https://example.com/image.jpg"
    }
  ],
  "total_items": 1,
  "total_quantity": 2,
  "total_amount": 199.98
}
```

#### 3. 更新商品数量
```http
PUT /cart/items/{product_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "quantity": 3
}
```

#### 4. 删除商品
```http
DELETE /cart/items/{product_id}
Authorization: Bearer {token}
```

#### 5. 清空购物车
```http
DELETE /cart/clear
Authorization: Bearer {token}
```

#### 6. 获取购物车统计
```http
GET /cart/count
Authorization: Bearer {token}
```

## 业务逻辑

### 核心业务规则
1. **用户隔离**: 每个用户只能访问自己的购物车
2. **商品验证**: 只能添加状态为'active'的商品
3. **库存检查**: 添加数量不能超过商品库存
4. **数量累加**: 重复添加同一商品时数量自动累加
5. **数据清理**: 自动清理已下架或删除的商品

### 数据一致性
- Redis购物车数据7天过期
- 获取购物车时验证商品有效性
- 自动清理无效商品引用

## 错误处理

### 错误码规范
- `400` - 请求参数错误（库存不足、数量无效等）
- `401` - 认证失败
- `404` - 商品不存在或不在购物车中
- `500` - 服务器内部错误

### 错误响应格式
```json
{
  "detail": "错误详细描述"
}
```

## 性能考虑

### 缓存策略
- 购物车数据存储在Redis中，提供高速访问
- 商品详情从MySQL实时查询，保证数据准确性
- 购物车数据7天TTL，平衡性能与存储成本

### 并发处理
- 使用Redis原子操作避免数据竞争
- 商品库存检查在添加时执行
- 支持用户并发购物车操作

## 安全机制

### 认证授权
- 使用JWT Bearer Token认证
- 用户只能操作自己的购物车
- Token过期时间30分钟

### 数据验证
- Pydantic模型验证请求参数
- 商品ID和数量范围检查
- SQL注入防护（SQLAlchemy ORM）

## 测试策略

### 测试覆盖
- **单元测试**: 核心业务逻辑
- **集成测试**: API端点功能
- **端到端测试**: 完整购物车流程

### 测试用例
1. 用户认证测试
2. 商品添加测试（正常、重复、库存不足）
3. 购物车查看测试
4. 数量更新测试
5. 商品删除测试
6. 购物车清空测试
7. 边界条件测试

## 部署配置

### 环境变量
```bash
DATABASE_URL=mysql+pymysql://root:rootpass@localhost:3307/ecommerce_platform
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Docker服务
```yaml
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: ecommerce_platform
    ports:
      - "3307:3306"
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

## 监控与日志

### 关键指标
- 购物车操作响应时间
- Redis连接状态
- 数据库查询性能
- 错误率统计

### 日志记录
- API请求日志
- 错误异常日志
- 性能指标日志

## 未来扩展

### 短期计划
1. 购物车商品推荐
2. 价格变动提醒
3. 库存预占机制
4. 购物车分享功能

### 长期规划
1. 多端同步（小程序、App）
2. 购物车数据分析
3. 个性化推荐引擎
4. 分布式缓存集群

## 相关文档

- [开发工具使用指南](development_tools_guide.md)
- [开发工作流程规范](development_workflow.md)
- [代码审查报告](cart_code_review_report.md)
- [API测试文档](../tests/)
