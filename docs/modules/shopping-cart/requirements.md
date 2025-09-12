<!--
文档说明：
- 内容：购物车模块的功能需求规范
- 使用方法：开发前查阅，理解购物车功能要求
- 更新方法：功能需求变更时更新
- 引用关系：引用 [功能需求规范](../../requirements/functional.md#3-购物车模块)
- 更新频率：功能迭代时
-->

# 购物车模块需求规范

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-12  
👤 **负责人**: AI开发助手  
🔄 **最后更新**: 2025-09-12  
📋 **版本**: v1.0.0  

## 功能需求概述

### 核心功能要求
基于 [功能需求规范](../../requirements/functional.md#3-购物车模块) 的具体实现要求：

1. **购物车操作**
   - 添加商品到购物车
   - 修改购物车商品数量
   - 删除购物车商品
   - 清空购物车

2. **实时库存验证**
   - 添加商品时验证库存
   - 数量变更时验证库存
   - 库存不足时提醒用户

3. **价格计算**
   - 实时商品价格更新
   - 优惠券计算集成
   - 运费计算支持

4. **数据持久化**
   - 基于Redis的高性能存储
   - 用户登录状态的购物车同步
   - 购物车数据过期管理

## 业务规则

### 购物车数据规则
遵循 [Redis缓存模块](../redis-cache/overview.md) 的数据管理规范：
- 购物车数据存储在Redis中，过期时间30天
- 每个用户最多100个商品项
- 每个商品项最大数量999
- 删除商品时自动清理过期数据

### 库存验证规则
- 添加商品时必须验证当前库存
- 数量超过库存时提示用户
- 商品下架时自动从购物车移除
- 价格变更时更新购物车价格

## API接口要求

### RESTful设计原则
严格遵循 [API设计标准](../../standards/api-standards.md#URL设计规范)：

```
GET    /api/v1/cart              # 获取购物车内容
POST   /api/v1/cart/items        # 添加商品到购物车
PUT    /api/v1/cart/items/{id}   # 更新购物车商品数量
DELETE /api/v1/cart/items/{id}   # 删除购物车商品
DELETE /api/v1/cart              # 清空购物车
POST   /api/v1/cart/validate     # 验证购物车有效性
```

### 权限要求
遵循 [API设计标准](../../standards/api-standards.md#认证授权)：
- 所有购物车操作需要用户认证
- 只能操作当前用户的购物车
- 支持游客购物车（基于session）

## 数据模型要求

### Redis数据结构设计
基于 [Redis缓存模块](../redis-cache/overview.md) 的设计规范：

```python
# 购物车数据结构
cart_data = {
    "user_id": 123,
    "items": [
        {
            "product_id": 456,
            "quantity": 2,
            "added_at": "2025-09-12T10:00:00Z"
        }
    ],
    "updated_at": "2025-09-12T10:30:00Z"
}

# Redis存储键规范 - 遵循 naming-conventions.md
CART_KEY_TEMPLATE = "cart:user:{user_id}"
GUEST_CART_KEY_TEMPLATE = "cart:guest:{session_id}"
```

### 数据库备份设计
虽然主要使用Redis，但需要数据库表作为备份：

```python
class Cart(BaseModel, TimestampMixin):
    """购物车模型 - 数据库备份"""
    __tablename__ = 'carts'
    
    user_id = Column(Integer, ForeignKey('users.id'))      # 用户ID
    product_id = Column(Integer, ForeignKey('products.id')) # 商品ID  
    quantity = Column(Integer, nullable=False)              # 数量
    
    # 关系映射
    user = relationship("User", back_populates="carts")
    product = relationship("Product", back_populates="cart_items")
```

## 性能要求

### 响应时间要求
- 获取购物车内容：< 100ms
- 添加/修改商品：< 50ms
- 删除商品：< 50ms
- 购物车验证：< 200ms

### 并发处理要求
- 支持5000并发购物车操作
- 支持1000并发库存验证
- 支持Redis集群部署

## 缓存策略要求

### Redis缓存设计
基于 [Redis缓存模块](../redis-cache/overview.md)：

```python
# 缓存键设计 - 遵循命名规范
CART_TTL = 30 * 24 * 3600  # 30天过期
GUEST_CART_TTL = 7 * 24 * 3600  # 游客购物车7天过期

# 缓存更新策略
class CartCacheStrategy:
    - 商品价格变更：批量更新相关购物车
    - 商品下架：自动清理购物车中的商品
    - 库存变更：更新购物车库存状态
```

## 安全要求

### 数据安全
- 用户只能访问自己的购物车
- 购物车数据不包含敏感信息
- Redis连接使用密码认证

### 防刷保护
- 购物车操作频率限制：每秒最多10次操作
- 商品数量限制：单个商品最多999件
- IP级别的操作频率监控

## 集成要求

### 商品模块集成
与 [商品管理模块](../product-catalog/overview.md) 的集成：
- 实时获取商品信息和价格
- 验证商品库存状态
- 处理商品下架情况

### 用户模块集成
与 [用户认证模块](../user-auth/overview.md) 的集成：
- 用户登录后同步购物车
- 游客购物车转换为用户购物车
- 用户注销后保留购物车数据

### 订单模块集成
与 [订单管理模块](../order-management/overview.md) 的集成：
- 购物车转订单功能
- 下单后清空购物车
- 订单失败后恢复购物车

## 测试要求

### 功能测试覆盖
- 购物车CRUD操作完整测试
- 库存验证功能测试
- 价格计算准确性测试
- 数据过期和清理测试

### 性能测试要求
- 高并发购物车操作测试
- Redis存储性能测试
- 大量商品购物车性能测试

### 集成测试要求
- 与商品模块集成测试
- 与用户模块集成测试
- 购物车转订单流程测试

参考：[测试规范](../../standards/testing-standards.md)