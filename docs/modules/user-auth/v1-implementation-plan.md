# 用户认证模块设计文档 - V1.0版本

## 📋 版本规划

### 🟢 V1.0 当前版本 (Mini-MVP)
**目标**: 完整可用的基础认证系统，支撑电商核心流程

#### 已实现功能 ✅
- [x] 用户注册/登录 (JWT认证)
- [x] 密码管理 (修改密码)
- [x] 用户信息管理 (个人资料)
- [x] 基础权限验证

#### 本版本待完成功能 🔄
- [ ] **认证中间件集成** - 保护所有需要认证的API
- [ ] **角色权限控制** - 管理员vs普通用户区分
- [ ] **统一错误处理** - 认证失败的标准响应
- [ ] **会话管理优化** - 令牌刷新和安全登出

### 🔵 V2.0 下一版本 (完整功能)
- [ ] 微信登录集成
- [ ] 手机验证码登录
- [ ] 多因素认证 (2FA)
- [ ] 详细权限控制 (RBAC)

### ⚪ 未来版本
- [ ] OAuth2集成
- [ ] 生物识别认证
- [ ] 企业用户管理

## 🏗️ V1.0 技术架构

### 简化架构设计
```
认证模块 V1.0:
├── app/auth.py                 # 核心认证逻辑 ✅
├── app/api/user_routes.py      # 用户API端点 ✅
├── app/middleware/auth.py      # 认证中间件 🔄
└── app/models.py               # User模型 ✅
```

### 数据模型 (当前实现)
```python
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)        # 简化为Integer ID
    username = Column(String(50), unique=True)
    email = Column(String(200), unique=True) 
    password_hash = Column(String(255))
    is_active = Column(Boolean, default=True)
    
    # V1.0 新增字段
    role = Column(String(20), default='customer')  # 'customer', 'admin'
    
    # 预留字段 (V2.0)
    phone = Column(String(20), nullable=True)
    wx_openid = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

## 🚀 V1.0 实现计划

### 阶段1: 认证中间件集成 (2天)
```python
# app/middleware/auth.py
from fastapi import Depends, HTTPException
from app.auth import get_current_active_user, get_current_admin_user

# 保护普通用户API
@router.get("/api/carts")
async def get_cart(user: User = Depends(get_current_active_user)):
    pass

# 保护管理员API  
@router.post("/api/products")
async def create_product(user: User = Depends(get_current_admin_user)):
    pass
```

### 阶段2: 角色权限实现 (1天)
- 添加User.role字段迁移
- 实现get_current_admin_user函数
- 更新用户注册时的角色分配

### 阶段3: 集成测试 (1天)
- 测试所有受保护的API端点
- 验证权限控制正确性
- 完善错误处理

## 📊 API端点保护策略

### 公开端点 (无需认证)
```
GET  /api/products          # 商品列表
GET  /api/products/{id}     # 商品详情  
GET  /api/categories        # 分类列表
POST /api/auth/register     # 用户注册
POST /api/auth/login        # 用户登录
```

### 用户端点 (需要登录)
```
GET  /api/auth/me          # 当前用户信息
PUT  /api/auth/me          # 更新用户信息
GET  /api/carts            # 购物车
POST /api/carts/items      # 添加到购物车
GET  /api/orders           # 用户订单
POST /api/orders           # 创建订单
```

### 管理员端点 (需要管理员权限)
```
POST /api/products         # 创建商品
PUT  /api/products/{id}    # 更新商品
DELETE /api/products/{id}  # 删除商品
GET  /api/auth/users       # 用户列表
PUT  /api/orders/{id}/status # 更新订单状态
```

## 🔧 实现细节

### 认证流程
1. 用户登录 → 生成JWT令牌
2. 客户端携带令牌访问API
3. 中间件验证令牌有效性
4. 检查用户权限级别
5. 放行或拒绝请求

### 错误处理
```python
# 统一认证错误响应
{
    "detail": "认证失败",
    "error_code": "AUTHENTICATION_FAILED",
    "status_code": 401
}

{
    "detail": "权限不足", 
    "error_code": "INSUFFICIENT_PRIVILEGES",
    "status_code": 403
}
```

## 🧪 测试策略

### V1.0 测试范围
- [x] 用户注册/登录测试 ✅
- [ ] 认证中间件测试
- [ ] 权限控制测试
- [ ] API端点保护测试
- [ ] 令牌刷新测试

### 测试用例
```python
def test_protected_endpoint_requires_auth():
    # 未认证访问应返回401
    
def test_admin_endpoint_requires_admin_role():
    # 普通用户访问管理员API应返回403
    
def test_token_refresh():
    # 令牌刷新流程测试
```

## 📈 成功标准

### V1.0 验收标准
- [ ] 所有需要认证的API都有保护
- [ ] 管理员和普通用户权限正确区分  
- [ ] 错误处理统一规范
- [ ] 测试覆盖率 > 80%
- [ ] API响应时间 < 200ms

### 可用性验证
- [ ] 用户可以正常注册、登录
- [ ] 用户可以管理购物车和下单
- [ ] 管理员可以管理商品和订单
- [ ] 认证失败有友好提示

---

**文档版本**: V1.0  
**最后更新**: 2025-09-11  
**下次评估**: V1.0完成后
