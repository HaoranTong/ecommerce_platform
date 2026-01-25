# API Schemas

> 自动生成于 schemas.py，勿手动修改

## `PasswordResetConfirm`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `email` | `str` | ❌ | `` | 邮箱地址 |
| `verification_code` | `str` | ❌ | `` | 邮箱验证码 |
| `new_password` | `str` | ❌ | `` | 新密码（至少8位，包含字母和数字） |

---

## `PasswordResetRequest`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `email` | `str` | ❌ | `` | 邮箱地址 |

---

## `PhoneLogin`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `phone` | `str` | ❌ | `` | 手机号 |
| `verification_code` | `str` | ❌ | `` | 短信验证码 |

---

## `Token`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `access_token` | `str` | ✅ | `` |  |
| `refresh_token` | `Optional[str]` | ❌ | `` |  |
| `token_type` | `str` | ❌ | `bearer` |  |
| `expires_in` | `int` | ✅ | `` |  |

---

## `UserChangePassword`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `old_password` | `str` | ❌ | `` | 原密码 |
| `new_password` | `str` | ❌ | `` | 新密码（至少8位，包含字母和数字） |

---

## `UserCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `username` | `str` | ❌ | `` | 用户名 |
| `email` | `str` | ❌ | `` | 邮箱地址 |
| `password` | `Optional[str]` | ❌ | `` | 密码（至少8位，包含字母和数字） |
| `phone` | `Optional[str]` | ❌ | `` | 手机号 |
| `real_name` | `Optional[str]` | ❌ | `` | 真实姓名 |
| `role` | `Optional[str]` | ❌ | `` | 用户角色 |
| `is_active` | `Optional[bool]` | ❌ | `` | 是否激活 |

---

## `UserLogin`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `username` | `str` | ❌ | `` | 用户名或邮箱 |
| `password` | `str` | ❌ | `` | 密码 |
| `verification_code` | `Optional[str]` | ❌ | `` | 验证码（登录失败3次后必填） |

---

## `UserProfile`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `username` | `str` | ✅ | `` |  |
| `email` | `str` | ✅ | `` |  |
| `phone` | `Optional[str]` | ❌ | `` |  |
| `real_name` | `Optional[str]` | ❌ | `` |  |
| `role` | `str` | ✅ | `` |  |
| `status` | `str` | ✅ | `` |  |
| `is_active` | `bool` | ✅ | `` |  |
| `email_verified` | `bool` | ❌ | `False` |  |
| `phone_verified` | `bool` | ❌ | `False` |  |
| `two_factor_enabled` | `bool` | ❌ | `False` |  |
| `wx_openid` | `Optional[str]` | ❌ | `` |  |
| `wx_unionid` | `Optional[str]` | ❌ | `` |  |
| `last_login_at` | `Optional[datetime]` | ❌ | `` |  |

---

## `UserPublic`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `username` | `str` | ✅ | `` |  |
| `real_name` | `Optional[str]` | ❌ | `` |  |
| `role` | `str` | ✅ | `` |  |
| `created_at` | `datetime` | ✅ | `` |  |

---

## `UserRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `username` | `str` | ✅ | `` |  |
| `email` | `str` | ✅ | `` |  |
| `phone` | `Optional[str]` | ❌ | `` |  |
| `real_name` | `Optional[str]` | ❌ | `` |  |
| `role` | `str` | ✅ | `` |  |
| `status` | `str` | ✅ | `` |  |
| `is_active` | `bool` | ✅ | `` |  |
| `email_verified` | `bool` | ❌ | `False` |  |
| `phone_verified` | `bool` | ❌ | `False` |  |
| `two_factor_enabled` | `bool` | ❌ | `False` |  |
| `wx_openid` | `Optional[str]` | ❌ | `` |  |
| `wx_unionid` | `Optional[str]` | ❌ | `` |  |
| `last_login_at` | `Optional[datetime]` | ❌ | `` |  |

---

## `UserRegister`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `username` | `str` | ❌ | `` | 用户名 |
| `email` | `str` | ❌ | `` | 邮箱地址 |
| `password` | `str` | ❌ | `` | 密码（至少8位，包含字母和数字） |
| `phone` | `Optional[str]` | ❌ | `` | 手机号 |
| `verification_code` | `str` | ❌ | `` | 验证码 |
| `real_name` | `Optional[str]` | ❌ | `` | 真实姓名 |

---

## `UserRegisterResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `user` | `UserRead` | ✅ | `` |  |
| `access_token` | `str` | ✅ | `` |  |
| `refresh_token` | `Optional[str]` | ❌ | `` |  |
| `token_type` | `str` | ❌ | `bearer` |  |

---

## `UserStats`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `total_users` | `int` | ✅ | `` |  |
| `active_users` | `int` | ✅ | `` |  |
| `new_users_today` | `int` | ✅ | `` |  |
| `new_users_this_week` | `int` | ✅ | `` |  |
| `new_users_this_month` | `int` | ✅ | `` |  |
| `user_roles_distribution` | `dict` | ✅ | `` |  |

---

## `UserUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `email` | `Optional[str]` | ❌ | `` | 邮箱地址 |
| `phone` | `Optional[str]` | ❌ | `` | 手机号 |
| `real_name` | `Optional[str]` | ❌ | `` | 真实姓名 |

---

