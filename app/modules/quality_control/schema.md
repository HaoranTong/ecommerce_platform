# API Schemas

> 自动生成于 schemas.py，勿手动修改

## `CertificateBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `serial` | `str` | ✅ | `` |  |
| `name` | `str` | ✅ | `` |  |
| `issuer` | `str` | ✅ | `` |  |
| `description` | `Optional[str]` | ❌ | `` |  |
| `issued_at` | `datetime` | ✅ | `` |  |
| `expires_at` | `datetime` | ✅ | `` |  |
| `is_active` | `bool` | ❌ | `True` |  |

---

## `CertificateCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `serial` | `str` | ✅ | `` |  |
| `name` | `str` | ✅ | `` |  |
| `issuer` | `str` | ✅ | `` |  |
| `description` | `Optional[str]` | ❌ | `` |  |
| `issued_at` | `datetime` | ✅ | `` |  |
| `expires_at` | `datetime` | ✅ | `` |  |
| `is_active` | `bool` | ❌ | `True` |  |

---

## `CertificateRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `serial` | `str` | ✅ | `` |  |
| `name` | `str` | ✅ | `` |  |
| `issuer` | `str` | ✅ | `` |  |
| `description` | `Optional[str]` | ❌ | `` |  |
| `issued_at` | `datetime` | ✅ | `` |  |
| `expires_at` | `datetime` | ✅ | `` |  |
| `is_active` | `bool` | ❌ | `True` |  |
| `id` | `int` | ✅ | `` |  |
| `created_at` | `datetime` | ✅ | `` |  |
| `updated_at` | `datetime` | ✅ | `` |  |

---

