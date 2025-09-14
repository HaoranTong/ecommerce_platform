# 用户认证模块

用户注册、登录、权限管理和JWT认证功能。

**对应文档**: [docs/modules/user-auth/](../../docs/modules/user-auth/)

## 功能概览

- ✅ 用户注册和邮箱验证
- ✅ 用户登录和JWT认证
- ✅ 访问令牌和刷新令牌管理
- ✅ 基于角色的权限控制
- ✅ 用户信息管理

## 模块结构

```
user_auth/
├── router.py           # API路由定义
├── service.py          # 业务逻辑处理
├── models.py           # 用户数据模型
├── schemas.py          # 请求/响应模型
├── dependencies.py     # 模块依赖注入
└── __init__.py         # 模块导出
```

## API端点

- `POST /api/user-auth/register` - 用户注册
- `POST /api/user-auth/login` - 用户登录
- `POST /api/user-auth/refresh` - 刷新令牌
- `GET /api/user-auth/me` - 获取当前用户信息

## 相关文档

- [API规范](../../docs/modules/user-auth/api-spec.md)
- [数据模型](../../docs/modules/user-auth/data-models.md)
- [业务流程](../../docs/modules/user-auth/business-logic.md)