# JWT Token格式标准文档

> **版本**: v1.0  
> **创建日期**: 2025-10-06  
> **负责人**: Development Team  
> **适用范围**: 所有测试和生产代码中的JWT token使用

## 🎯 标准概述

为了确保JWT token在整个系统中的一致性和兼容性，特制定此标准。所有代码（包括生产代码和测试代码）必须严格遵循此标准。

## 📋 JWT Token格式规范

### 🔐 标准Token结构

```json
{
  "sub": "12345",           // 必需：用户ID的字符串表示
  "type": "access",         // 必需：token类型（由create_access_token自动添加）
  "exp": 1234567890,        // 必需：过期时间戳（由create_access_token自动添加）
  "role": "user",           // 可选：用户角色
  "permissions": ["read"]   // 可选：用户权限列表
}
```

### 📏 字段规范

| 字段 | 类型 | 必需性 | 描述 | 示例 |
|------|------|--------|------|------|
| `sub` | string | **必需** | 用户ID的字符串表示，必须可转换为正整数 | `"12345"` |
| `type` | string | **必需** | token类型，固定为"access" | `"access"` |
| `exp` | number | **必需** | 过期时间戳 | `1234567890` |
| `role` | string | 可选 | 用户角色 | `"admin"`, `"user"` |
| `permissions` | array | 可选 | 权限列表 | `["read", "write"]` |

### ⚠️ 关键约束

1. **`sub`字段约束**：
   - 必须是字符串类型
   - 必须能够转换为正整数：`int(payload["sub"]) > 0`
   - 不能使用用户名、邮箱等非数字标识符

2. **兼容性约束**：
   - 所有token必须能通过`app.core.auth.decode_token()`正常解析
   - 认证系统会执行`user_id = int(payload.get("sub"))`

## 🛠️ 标准实现

### ✅ 正确的Token创建方式

#### 生产环境
```python
from app.core.auth import create_access_token

# 标准方式
access_token = create_access_token(data={"sub": str(user.id)})

# 带额外声明
access_token = create_access_token(
    data={"sub": str(user.id), "role": "admin"}
)
```

#### 测试环境
```python
from tests.utils.token_utils import create_test_token

# 推荐：使用统一工具函数
token = create_test_token(user_id=12345)

# 带额外声明
token = create_test_token(
    user_id=12345, 
    additional_claims={"role": "admin"}
)

# 便捷函数
admin_token = TEST_ADMIN_TOKEN()
user_token = TEST_USER_TOKEN()
```

### ❌ 错误的Token创建方式

```python
# 错误1：sub字段使用用户名
create_access_token(data={"sub": "username", "user_id": 123})

# 错误2：sub字段为整数
create_access_token(data={"sub": 123})

# 错误3：缺少sub字段
create_access_token(data={"user_id": 123, "username": "test"})

# 错误4：sub字段为非数字字符串
create_access_token(data={"sub": "non-numeric-id"})
```

## 🔍 验证和测试

### 自动化验证

所有测试中创建的token都应该通过格式验证：

```python
from tests.utils.token_utils import validate_test_token

# 创建token
token = create_test_token(user_id=12345)

# 验证格式
payload = validate_test_token(token)  # 抛出ValueError如果格式错误
```

### 测试覆盖要求

1. **单元测试**：验证token创建和格式
2. **集成测试**：验证token在认证流程中的使用
3. **性能测试**：验证token在并发场景下的行为

## 🚨 历史问题分析

### 问题根源
过去的"Invalid user ID in token"错误主要由以下原因导致：

1. **格式不一致**：不同代码模块使用不同的token格式
2. **错误的sub字段**：使用用户名而不是用户ID
3. **缺乏统一工具**：每处都重复实现token创建逻辑

### 解决方案
1. ✅ 建立统一的token创建工具
2. ✅ 强制格式验证
3. ✅ 全面的测试覆盖
4. ✅ 详细的文档标准

## 🔄 迁移指南

### 现有代码迁移

如果发现使用错误格式的代码：

```python
# 旧代码（错误）
token = create_access_token(data={"sub": user.username, "user_id": user.id})

# 新代码（正确）
token = create_access_token(data={"sub": str(user.id)})

# 或使用统一工具（推荐）
from tests.utils.token_utils import create_test_token
token = create_test_token(user_id=user.id)
```

### 测试代码迁移

```python
# 旧的测试fixture（错误）
@pytest.fixture
def auth_token():
    return create_access_token(data={"sub": "test_user", "user_id": 123})

# 新的测试fixture（正确）
@pytest.fixture
def auth_token():
    from tests.utils.token_utils import create_test_token
    return create_test_token(user_id=123)
```

## 📊 合规性检查

### 自动检查脚本

可以使用以下脚本检查代码中的token格式：

```bash
# 检查可能的错误格式
grep -r "sub.*username" tests/
grep -r "sub.*[^s]tr(" tests/
```

### 持续集成

在CI/CD流程中添加token格式验证测试：

```yaml
- name: Validate JWT Token Format
  run: python -m pytest tests/unit/test_token_format_validation.py -v
```

## 🎯 最佳实践

1. **始终使用统一的工具函数**
2. **在创建token后立即验证格式**
3. **在测试中包含格式验证**
4. **定期审查token创建代码**
5. **更新时同步所有相关模块**

## 📞 支持和反馈

如果遇到token格式相关问题：

1. 首先检查是否符合此标准
2. 使用`validate_test_token()`验证格式
3. 查看相关测试用例
4. 提交issue包含详细的错误信息

---

**记住**: 统一的标准是系统稳定性的基础。严格遵循此文档可以避免99%的JWT相关认证问题。