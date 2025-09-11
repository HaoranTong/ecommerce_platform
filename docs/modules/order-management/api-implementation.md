# 订单管理API实现文档

## 文档说明
- **内容**: 订单管理API的详细实现和认证集成
- **使用方法**: 订单API开发和认证集成的技术指南
- **更新方法**: API实现变更时同步更新
- **引用关系**: 实现overview.md中的API规范
- **更新频率**: API变更时

## 认证集成实现

### 权限体系
本模块基于用户角色(role)字段实现权限控制：
- `user` - 普通用户：只能操作自己的订单
- `admin` - 管理员：可以操作所有订单和管理功能
- `super_admin` - 超级管理员：拥有所有权限

### 认证依赖
```python
from app.auth import (
    get_current_active_user,     # 用户认证
    get_current_admin_user,      # 管理员认证
    require_ownership           # 所有权验证
)
```

## API端点实现

### 1. 创建订单

**端点**: `POST /api/orders`  
**认证**: 用户认证 + 所有权验证  
**权限检查**: 用户只能为自己创建订单，管理员可为任何人创建

```python
@router.post("/api/orders")
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # 用户认证
):
```

**权限验证逻辑**:
```python
# 验证用户是否有权为指定用户创建订单
if order_data.user_id != current_user.id:
    # 检查是否是管理员
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(403, "只能为自己创建订单")
```

### 2. 获取订单列表

**端点**: `GET /api/orders`  
**认证**: 用户认证 + 数据隔离  
**权限检查**: 用户只能查看自己的订单，管理员可查看所有

```python
@router.get("/api/orders")
async def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # 用户认证
):
```

**数据隔离逻辑**:
```python
query = db.query(Order)

# 普通用户只能查看自己的订单
if current_user.role not in ['admin', 'super_admin']:
    query = query.filter(Order.user_id == current_user.id)
```

### 3. 获取订单详情

**端点**: `GET /api/orders/{order_id}`  
**认证**: 用户认证 + 所有权验证  
**权限检查**: 用户只能查看自己的订单，管理员可查看所有

```python
@router.get("/api/orders/{order_id}")
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # 用户认证
):
```

**所有权验证**:
```python
# 验证所有权
if not require_ownership(order.user_id, current_user):
    raise HTTPException(403, "无权访问此订单")
```

### 4. 更新订单状态

**端点**: `PATCH /api/orders/{order_id}/status`  
**认证**: 管理员权限  
**权限检查**: 仅管理员可以更新订单状态

```python
@router.patch("/api/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)  # 管理员权限
):
```

### 5. 取消订单

**端点**: `DELETE /api/orders/{order_id}`  
**认证**: 用户认证 + 所有权验证  
**权限检查**: 用户可取消自己的订单，管理员可取消任何订单

```python
@router.delete("/api/orders/{order_id}")
async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # 用户认证
):
```

**权限验证**:
```python
# 所有权验证
if not require_ownership(order.user_id, current_user):
    raise HTTPException(403, "无权取消此订单")
```

### 6. 获取订单商品

**端点**: `GET /api/orders/{order_id}/items`  
**认证**: 用户认证 + 所有权验证  
**权限检查**: 用户只能查看自己订单的商品，管理员可查看所有

```python
@router.get("/api/orders/{order_id}/items")
async def get_order_items(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # 用户认证
):
```

## 权限矩阵

| API端点 | 匿名用户 | 普通用户 | 管理员 | 说明 |
|---------|---------|---------|--------|------|
| `POST /api/orders` | ❌ | ✅(自己) | ✅(任意) | 创建订单 |
| `GET /api/orders` | ❌ | ✅(自己) | ✅(所有) | 订单列表 |
| `GET /api/orders/{id}` | ❌ | ✅(自己) | ✅(所有) | 订单详情 |
| `PATCH /api/orders/{id}/status` | ❌ | ❌ | ✅ | 状态管理 |
| `DELETE /api/orders/{id}` | ❌ | ✅(自己) | ✅(所有) | 取消订单 |
| `GET /api/orders/{id}/items` | ❌ | ✅(自己) | ✅(所有) | 订单商品 |

## 错误处理

### 认证错误
- `401 Unauthorized` - 用户未认证或token无效
- `403 Forbidden` - 权限不足或无权访问资源

### 业务错误
- `404 Not Found` - 订单不存在
- `400 Bad Request` - 订单状态不允许操作

## 安全措施

### 数据隔离
- 普通用户查询自动添加`user_id`过滤条件
- 所有权验证通过`require_ownership`函数统一处理

### 权限检查
- 管理员操作使用`get_current_admin_user`依赖
- 用户操作使用`get_current_active_user`依赖
- 所有权验证集成到业务逻辑中

### 审计日志
- 所有订单状态变更记录操作用户
- 重要操作保留IP地址和时间戳

---

**实现版本**: V1.0 Mini-MVP  
**最后更新**: 2025-09-11  
**下次评审**: 订单功能扩展时
