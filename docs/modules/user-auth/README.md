# 用户认证模块 (User Authentication Module)

> 🔐 用户身份验证、权限管理和会话控制的核心模块

## 📋 模块导航

### 📚 设计文档
- **[模块概览](overview.md)** - 模块架构设计和技术规范
- **[API实现](api-implementation.md)** - REST API接口完整文档
- **[认证详情](authentication-details.md)** - 认证机制和安全设计

### 🔧 实现代码
- **用户路由**: `app/api/user_routes.py` - 用户管理API端点
- **认证逻辑**: `app/auth.py` - JWT认证和权限控制
- **数据模型**: `app/data_models.py` - User相关数据模型

### 🧪 测试用例
- **单元测试**: `tests/test_users.py` - 用户功能测试
- **集成测试**: 认证流程端到端测试

## 🎯 模块功能概要

### 核心功能
- ✅ **用户注册登录** - 完整的用户注册和认证流程
- ✅ **JWT认证** - 基于令牌的安全认证机制
- ✅ **权限管理** - 基于角色的访问控制
- ✅ **密码管理** - 安全的密码修改和重置
- ✅ **会话控制** - 用户会话管理和安全控制

### API端点
```
POST /api/auth/register     # 用户注册
POST /api/auth/login        # 用户登录  
POST /api/auth/refresh      # 令牌刷新
GET  /api/auth/me           # 获取当前用户
PUT  /api/auth/me           # 更新当前用户
POST /api/auth/logout       # 用户登出
PUT  /api/users/password    # 修改密码
GET  /api/auth/users        # 用户列表(管理员)
GET  /api/auth/users/{id}   # 用户详情(管理员)
```

## 🔄 开发状态

### ✅ 已完成
- [x] 基础认证功能 (注册、登录、JWT)
- [x] 用户信息管理
- [x] 基础权限控制
- [x] API文档完善
- [x] 单元测试覆盖

### 🔄 进行中
- [ ] 认证中间件集成
- [ ] 角色权限扩展
- [ ] 多因素认证
- [ ] 会话管理优化

### 📋 待开发
- [ ] OAuth2集成
- [ ] 微信登录集成
- [ ] 生物识别认证
- [ ] 风控和安全加固

## 🔗 相关模块

### 依赖模块
- **数据库核心模块** - 用户数据存储
- **Redis缓存模块** - 会话和令牌存储

### 被依赖模块
- **购物车模块** - 需要用户认证
- **订单管理模块** - 需要用户认证
- **通知服务模块** - 需要用户身份
- **分销商管理模块** - 需要权限控制

## 📖 快速开始

### 开发者指南
1. 阅读 [模块概览](overview.md) 了解架构设计
2. 查看 [API实现文档](api-implementation.md) 了解接口规范
3. 检查 `app/api/user_routes.py` 查看具体实现
4. 运行 `pytest tests/test_users.py` 验证功能

### 集成指南
```python
# 在其他模块中使用用户认证
from app.auth import get_current_active_user

@router.get("/protected-endpoint")
async def protected_route(
    current_user: User = Depends(get_current_active_user)
):
    # 受保护的端点逻辑
    pass
```

---

**最后更新**: 2025-09-11  
**文档版本**: v1.2.0  
**维护者**: 开发团队
