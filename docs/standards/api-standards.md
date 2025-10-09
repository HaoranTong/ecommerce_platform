<!--version info: v1.0.0, created: 2025-09-23, level: L2, dependencies: naming-conventions-standards.md,../../PROJECT-FOUNDATION.md-->

# API设计标准 (API Standards)

## 概述

本文档定义RESTful API设计、FastAPI实现和接口规范的具体标准，属于L2领域标准。

## 依赖标准

本标准依赖以下L1核心标准：
- **[命名规范标准](naming-conventions-standards.md)** - API路由路径命名（RESTful路径规则）、参数命名（请求响应字段）、端点命名标准（HTTP动词映射）
- **[项目基础定义](../../PROJECT-FOUNDATION.md)** - 模块组织结构（业务模块边界）、目录结构标准（API文档存放位置）、模块命名映射关系

## 具体标准
⬆️ **模块命名映射**: 参见 [PROJECT-FOUNDATION.md](../../PROJECT-FOUNDATION.md#业务模块标准结构-垂直切片)

## 📋 文档说明

本文档定义API设计原则、HTTP规范、响应格式、认证授权等技术实施标准，基于L1核心标准制定具体的API开发规范。

### 🎯 文档职责
- **API设计原则**: RESTful设计、模块化架构、独立性原则
- **HTTP协议规范**: 方法使用、状态码、请求响应格式
- **认证授权标准**: JWT Token、权限验证、安全控制
- **版本管理策略**: API版本控制、向后兼容、废弃管理
- **性能优化指导**: 缓存、压缩、限流等性能优化标准

---

## 🎯 API设计核心原则

### RESTful架构原则
1. **资源导向设计** - URL表示资源，HTTP方法表示操作
2. **无状态通信** - 每个请求包含完整的处理信息
3. **统一接口约定** - 一致的API设计风格和交互模式
4. **分层系统架构** - 客户端与服务端实现解耦
5. **按需代码扩展** - 支持功能动态扩展和插件化

### 模块化设计原则
- **独立性原则** - 各模块独立管理API设计，避免跨模块依赖
- **一致性标准** - 通过文档标准确保接口一致性，禁止运行时共享
- **业务内聚性** - API设计与业务模块边界对齐
- **技术分离性** - 接口设计与具体实现技术解耦
- **可扩展性** - 支持模块独立版本管理和功能演进

### API路径命名统一标准 ⭐ 重要

**强制规则**: API路径前缀 = 完整业务模块名（kebab-case）

```
标准格式:
/api/v1/{完整业务模块名}/{资源名}[/{资源id}][/{子资源或操作}]

命名原则:
✅ 使用完整业务概念名（如 product-catalog, shopping-cart, user-auth）
✅ 模块名使用 kebab-case（小写-连字符）
✅ 与模块目录名保持一致（product_catalog → product-catalog）
❌ 禁止使用简化名称（products, cart, auth）
❌ 禁止省略模块前缀

正确示例:
✅ /api/v1/product-catalog/products
✅ /api/v1/shopping-cart/items
✅ /api/v1/order-management/orders

错误示例:
❌ /api/v1/products  (缺少模块前缀)
❌ /api/v1/cart/items  (使用简化名)
❌ /api/v1/auth/login  (应为 user-auth)
```

**统一性要求**:
- 业务概念名: `product-catalog` (文档中)
- 技术实现名: `product_catalog` (Python模块名)
- API路径名: `/product-catalog/` (URL路径)
- 保持三者语义一致，仅格式转换

## 🌐 API架构设计规范

### 模块化路由架构
平台采用模块化单体架构，支持向微服务演进的API设计：

**路由组织原则**:
```python
# 全局路由注册 - main.py
app.include_router(
    module_router,
    prefix="/api/v1",              # 统一全局API版本前缀
    tags=["{模块业务名称}"],         # 模块标识用于API文档分组
    dependencies=[Depends(...)]     # 全局依赖注入
)
```

**业务端点设计模式**:
```bash
# API端点组织规则（完整格式）
/api/v1/{完整业务模块名}/{资源集合}[/{资源id}][/{操作}]

# 示例
/api/v1/user-auth/register          # 用户认证：用户注册
/api/v1/product-catalog/products    # 商品管理：商品列表
/api/v1/order-management/orders     # 订单管理：订单操作

# 说明：
# - 完整业务模块名：使用kebab-case，如 user-auth, product-catalog
# - 资源名使用复数形式
# - 避免使用简化名称（如 /auth/, /products/）
```

### 资源导向设计
- **集合资源设计**: 统一的CRUD操作模式
- **嵌套资源管理**: 父子关系资源的路径设计
- **业务操作映射**: 复杂业务逻辑的RESTful表达
- **跨模块资源**: 避免直接跨模块API调用，使用事件或消息

### 领域驱动API设计

**核心原则**: API路径前缀 = 完整业务模块名（kebab-case）

```bash
# 用户认证领域 (user-auth)
POST   /api/v1/user-auth/register           # 用户注册
POST   /api/v1/user-auth/login              # 用户登录
GET    /api/v1/user-auth/profile            # 用户资料
PUT    /api/v1/user-auth/profile            # 更新资料
POST   /api/v1/user-auth/logout             # 用户登出

# 商品目录领域 (product-catalog)
GET    /api/v1/product-catalog/products              # 商品列表
POST   /api/v1/product-catalog/products              # 创建商品
GET    /api/v1/product-catalog/products/{id}         # 商品详情
GET    /api/v1/product-catalog/categories            # 分类列表
GET    /api/v1/product-catalog/brands                # 品牌列表

# 购物车领域 (shopping-cart)
GET    /api/v1/shopping-cart/items                   # 购物车列表
POST   /api/v1/shopping-cart/items                   # 添加商品
DELETE /api/v1/shopping-cart/items/{id}              # 删除商品

# 订单管理领域 (order-management)
POST   /api/v1/order-management/orders               # 创建订单
GET    /api/v1/order-management/orders/{id}          # 订单详情
PUT    /api/v1/order-management/orders/{id}/pay      # 订单支付
PUT    /api/v1/order-management/orders/{id}/ship     # 订单发货
PUT    /api/v1/order-management/orders/{id}/cancel   # 取消订单

# 支付服务领域 (payment-service)
POST   /api/v1/payment-service/transactions          # 创建支付
GET    /api/v1/payment-service/transactions/{id}     # 支付详情
POST   /api/v1/payment-service/refunds               # 申请退款

# 库存管理领域 (inventory-management)
GET    /api/v1/inventory-management/stock/{sku_id}   # 查询库存
POST   /api/v1/inventory-management/inbound          # 入库操作
POST   /api/v1/inventory-management/outbound         # 出库操作
GET    /api/v1/inventory-management/reservations     # 库存预留

# 会员系统领域 (member-system)
GET    /api/v1/member-system/levels                  # 会员等级
GET    /api/v1/member-system/points                  # 积分查询
POST   /api/v1/member-system/points/exchange         # 积分兑换

# 营销活动领域 (marketing-campaigns)
GET    /api/v1/marketing-campaigns/campaigns         # 活动列表
GET    /api/v1/marketing-campaigns/coupons           # 优惠券列表
POST   /api/v1/marketing-campaigns/coupons/claim     # 领取优惠券

# 批次溯源领域 (batch-traceability)
GET    /api/v1/batch-traceability/products/{id}/origin     # 溯源信息
POST   /api/v1/batch-traceability/batches                  # 批次管理
GET    /api/v1/batch-traceability/certifications          # 认证信息

# 物流管理领域 (logistics-management)
POST   /api/v1/logistics-management/shipments              # 创建物流单
GET    /api/v1/logistics-management/shipments/{id}/track   # 物流跟踪

# 通知服务领域 (notification-service)
GET    /api/v1/notification-service/notifications          # 通知列表
POST   /api/v1/notification-service/notifications/send     # 发送通知
PUT    /api/v1/notification-service/notifications/{id}/read # 标记已读
```

**命名规范说明**:
- ✅ 使用完整业务模块名（如 `product-catalog`，而非 `products`）
- ✅ 模块名使用 kebab-case（小写-连字符）
- ✅ 资源名使用复数形式
- ✅ 统一添加 `/api/v1` 版本前缀
- ❌ 避免使用简化名称或缩写

## 🔧 HTTP协议规范

### HTTP方法语义
| 方法 | 语义 | 幂等性 | 安全性 | 使用场景 |
|------|------|--------|--------|----------|
| GET | 查询资源 | ✅ | ✅ | 资源检索、列表查询、详情获取 |
| POST | 创建资源/非幂等操作 | ❌ | ❌ | 资源创建、业务操作、数据提交 |
| PUT | 完整更新/替换资源 | ✅ | ❌ | 整体资源替换、幂等更新操作 |
| PATCH | 部分更新资源 | ❌ | ❌ | 增量更新、字段级别修改 |
| DELETE | 删除资源 | ✅ | ❌ | 资源删除、软删除操作 |

### 业务操作映射原则
```bash
# 资源CRUD操作映射（标准RESTful）
GET    /api/v1/product-catalog/products           # 查询商品列表 (安全、幂等)
POST   /api/v1/product-catalog/products           # 创建新商品 (非幂等)
GET    /api/v1/product-catalog/products/{id}      # 查询商品详情 (安全、幂等)
PUT    /api/v1/product-catalog/products/{id}      # 替换商品信息 (幂等)
PATCH  /api/v1/product-catalog/products/{id}      # 更新部分字段 (非幂等)
DELETE /api/v1/product-catalog/products/{id}      # 删除商品 (幂等)

# 复杂业务操作映射（模块前缀 + 业务动作）
POST   /api/v1/order-management/orders/{id}/pay          # 支付订单 (业务操作)
PUT    /api/v1/order-management/orders/{id}/status       # 更新订单状态 (状态变更)
POST   /api/v1/order-management/orders/{id}/cancel       # 取消订单 (业务操作)
POST   /api/v1/product-catalog/products/{id}/favorite    # 收藏商品 (关系操作)
DELETE /api/v1/product-catalog/products/{id}/favorite    # 取消收藏 (关系删除)

# 注意：所有API路径必须包含完整模块前缀
```

### 幂等性设计考虑
- **GET操作**: 必须保证无副作用，支持缓存
- **PUT操作**: 相同请求多次执行结果一致
- **DELETE操作**: 删除不存在资源返回成功（204或404根据业务需要）
- **POST操作**: 通过业务标识符防止重复创建

## 📨 请求规范标准

### Content-Type规范
- **主要格式**: `application/json` - API主要交互格式
- **表单提交**: `application/x-www-form-urlencoded` - 简单表单数据
- **文件上传**: `multipart/form-data` - 文件上传和复合数据
- **纯文本**: `text/plain` - 特殊场景文本传输

### 标准请求头
```http
# 必需请求头
Content-Type: application/json          # 内容类型声明
Accept: application/json                # 接受响应类型
Authorization: Bearer {jwt_token}       # 认证令牌

# 推荐请求头
X-Request-ID: {uuid}                   # 请求链路追踪ID
X-Client-Version: {version}            # 客户端版本标识
X-Forwarded-For: {client_ip}           # 客户端真实IP
User-Agent: {client_info}              # 客户端信息
```

### 请求体设计模式
```json
{
  "data": {
    // 业务数据载荷 - 具体业务字段
    "name": "五常大米",
    "price": 99.99,
    "category_id": 1,
    "description": "优质五常大米",
    "tags": ["有机", "产地直供"]
  },
  "context": {
    // 请求上下文信息 - 可选
    "request_id": "req_123456789",
    "client_version": "1.2.0",
    "trace_id": "trace_abc123"
  }
}
```

### 特殊场景请求格式
```json
# 批量操作请求
{
  "action": "batch_update",
  "items": [
    {"id": 1, "status": "active"},
    {"id": 2, "status": "inactive"}
  ],
  "options": {
    "validate_only": false,
    "ignore_errors": true
  }
}

# 文件上传请求 (multipart/form-data)
{
  "file": {binary_data},
  "metadata": {
    "filename": "product.jpg",
    "size": 1024000,
    "type": "image/jpeg"
  }
}
```

## 📤 响应格式规范

### 统一响应结构标准
```json
{
  "success": true,                    # 业务执行状态标识
  "code": 200,                       # HTTP状态码
  "message": "操作成功",              # 用户友好的响应消息
  "data": {
    // 具体业务数据载荷
    "id": 123,
    "name": "商品名称",
    "created_at": "2025-09-23T10:00:00Z"
  },
  "metadata": {
    // 响应元数据信息
    "request_id": "req_123456789",   # 请求追踪ID
    "timestamp": "2025-09-23T10:00:00Z",  # 响应时间戳
    "execution_time": 150,           # 执行时间(毫秒)
    "api_version": "v1"              # API版本标识
  }
}
```

### 分页响应标准结构
```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "items": [
      // 分页数据项列表
    ],
    "pagination": {
      "current_page": 1,             # 当前页码
      "page_size": 20,               # 每页条数
      "total_pages": 5,              # 总页数
      "total_items": 100,            # 总记录数
      "has_next_page": true,         # 是否有下一页
      "has_prev_page": false,        # 是否有上一页
      "next_page_url": "...",        # 下一页链接(可选)
      "prev_page_url": null          # 上一页链接(可选)
    }
  },
  "metadata": {
    "request_id": "req_123456789",
    "timestamp": "2025-09-23T10:00:00Z",
    "query_time": 50                 # 查询耗时
  }
}
```

### 模块独立实现原则

**🎯 核心实现策略**:
**架构原则**: 通过**文档标准**确保API一致性，各模块**完全独立实现**，严禁运行时跨模块共享

**📋 模块内Schema定义**:
```python
# app/modules/{module_name}/schemas.py - 每个模块独立定义
from pydantic import BaseModel
from typing import Optional, Any, List
from datetime import datetime

class StandardResponse(BaseModel):
    """模块内标准响应格式 - 独立定义"""
    success: bool = True
    code: int = 200
    message: str = "操作成功"
    data: Optional[Any] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PaginatedResponse(BaseModel):
    """模块内分页响应格式 - 独立定义"""
    success: bool = True
    code: int = 200
    message: str = "查询成功"
    data: dict  # 包含items和pagination
    
    @classmethod
    def create(cls, items: List[Any], total: int, page: int, size: int):
        return cls(
            data={
                "items": items,
                "pagination": {
                    "current_page": page,
                    "page_size": size,
                    "total_pages": (total + size - 1) // size,
                    "total_items": total,
                    "has_next_page": page * size < total,
                    "has_prev_page": page > 1
                }
            }
        )
```

**✅ 正确实践 vs ❌ 禁止行为**:
```python
# ✅ 正确：模块内独立定义响应格式
from app.modules.user_auth.schemas import StandardResponse

def login_endpoint():
    return StandardResponse(data={"token": "..."})

# ❌ 禁止：跨模块导入共享响应格式
from app.shared.schemas import StandardResponse  # 禁止
from app.core.schemas import ApiResponse         # 禁止
from app.common.response import BaseResponse     # 禁止

# ✅ 正确：通过代码生成工具避免重复
# 使用模板生成各模块的schemas文件，而非运行时共享
```

## 📊 HTTP状态码规范

### 成功状态码标准
| 状态码 | 语义 | 使用场景 | 响应体要求 |
|--------|------|----------|-----------|
| **200 OK** | 请求成功 | 查询、更新操作成功 | 必须包含data字段 |
| **201 Created** | 资源创建成功 | POST创建操作成功 | 包含新创建资源信息 |
| **202 Accepted** | 请求已接受 | 异步处理任务提交 | 包含任务状态信息 |
| **204 No Content** | 请求成功无内容 | DELETE操作成功 | 空响应体或最小元数据 |

### 客户端错误状态码
| 状态码 | 语义 | 常见场景 | 错误处理 |
|--------|------|----------|----------|
| **400 Bad Request** | 请求参数错误 | 参数格式、类型错误 | 详细字段验证信息 |
| **401 Unauthorized** | 认证失败 | Token无效、过期 | 引导重新登录 |
| **403 Forbidden** | 权限不足 | 无操作权限 | 权限说明信息 |
| **404 Not Found** | 资源不存在 | 资源ID不存在 | 资源标识说明 |
| **409 Conflict** | 资源冲突 | 唯一性约束冲突 | 冲突字段说明 |
| **422 Unprocessable Entity** | 语义错误 | 业务规则验证失败 | 业务规则说明 |
| **429 Too Many Requests** | 频率限制 | API调用超限 | 限制信息和重试时间 |

### 服务器错误状态码
| 状态码 | 语义 | 处理策略 | 监控要求 |
|--------|------|----------|----------|
| **500 Internal Server Error** | 服务器内部错误 | 记录错误日志，返回通用错误信息 | 立即告警 |
| **502 Bad Gateway** | 网关错误 | 上游服务异常 | 服务健康检查 |
| **503 Service Unavailable** | 服务不可用 | 服务维护、过载 | 负载监控 |
| **504 Gateway Timeout** | 网关超时 | 上游服务超时 | 性能监控 |

## 🚨 错误处理标准

### 标准错误响应结构
```json
{
  "success": false,
  "code": 400,
  "message": "请求参数验证失败",          # 用户友好错误信息
  "error": {
    "type": "VALIDATION_ERROR",        # 错误类型标识
    "code": "E400001",                 # 内部错误编码
    "details": [                       # 详细错误信息
      {
        "field": "price",              # 错误字段
        "value": "-10.5",              # 错误值
        "message": "价格必须大于0",     # 字段错误描述
        "constraint": "min_value"      # 约束类型
      }
    ],
    "help": "https://docs.api.com/errors/E400001"  # 错误帮助链接
  },
  "metadata": {
    "request_id": "req_123456789",
    "timestamp": "2025-09-23T10:00:00Z",
    "error_id": "err_987654321"        # 错误追踪ID
  }
}
```

### 业务错误分类标准
```python
# 错误类型枚举 - 各模块可独立定义类似结构
class ErrorCategory:
    # 输入验证错误
    VALIDATION_ERROR = "VALIDATION_ERROR"           # 参数格式、类型错误
    BUSINESS_RULE_ERROR = "BUSINESS_RULE_ERROR"     # 业务规则验证失败
    
    # 认证授权错误  
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"   # 身份认证失败
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"     # 权限授权失败
    
    # 资源相关错误
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"       # 资源不存在
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"         # 资源冲突
    RESOURCE_LOCKED = "RESOURCE_LOCKED"             # 资源被锁定
    
    # 系统级错误
    SYSTEM_ERROR = "SYSTEM_ERROR"                   # 系统内部错误
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_ERROR"       # 外部服务错误
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"          # 频率限制错误
```

### 错误处理最佳实践
```python
# 模块内错误处理示例
from fastapi import HTTPException, status
from app.modules.{module}/schemas import ErrorResponse

def handle_validation_error(error_details: list):
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorResponse(
            success=False,
            code=400,
            message="参数验证失败",
            error={
                "type": "VALIDATION_ERROR",
                "code": "E400001",
                "details": error_details
            }
        ).dict()
    )

def handle_business_error(message: str, code: str):
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=ErrorResponse(
            success=False,
            code=422,
            message=message,
            error={
                "type": "BUSINESS_RULE_ERROR", 
                "code": code,
                "details": []
            }
        ).dict()
    )
```

## 🔐 认证授权标准

### JWT Token认证规范
```http
# 标准认证头格式
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# 可选认证头格式
X-API-Key: {api_key}                    # API密钥认证
X-Client-Token: {client_token}          # 客户端令牌
```

### JWT载荷标准结构
```json
{
  "header": {
    "alg": "HS256",                     # 签名算法
    "typ": "JWT",                       # Token类型
    "kid": "key_id_001"                 # 密钥标识符
  },
  "payload": {
    "sub": "user_123456",               # 用户唯一标识
    "username": "user@example.com",     # 用户名
    "roles": ["user", "premium"],       # 用户角色列表
    "permissions": ["read", "write"],   # 权限列表
    "exp": 1640995200,                  # 过期时间戳
    "iat": 1640908800,                  # 签发时间戳
    "jti": "token_uuid",                # Token唯一标识
    "iss": "api.ecommerce.com",         # 签发者
    "aud": ["mobile", "web"]            # 目标受众
  }
}
```

### 权限分级验证
| 权限级别 | 认证要求 | 适用场景 | 验证机制 |
|----------|----------|----------|----------|
| **公开接口** | 无需认证 | 商品查询、公开信息 | 无验证或API限流 |
| **用户接口** | 有效Token | 个人信息、订单管理 | JWT Token验证 |
| **管理接口** | 管理员权限 | 后台管理、数据操作 | 角色权限验证 |
| **敏感操作** | 双重验证 | 支付、密码修改 | Token+验证码/生物识别 |
| **系统接口** | 服务凭证 | 内部服务调用 | 服务间认证 |

## 📈 API版本管理

### 版本控制策略
- **URL版本控制** (推荐): `/api/v1/`, `/api/v2/` - 版本明确可见
- **Header版本控制** (备选): `API-Version: v1` - 保持URL简洁
- **语义化版本**: `major.minor.patch` (1.0.0) - 兼容性语义明确
- **向后兼容原则**: 同一主版本内保持向后兼容

### 版本演进管理
```http
# 版本并行支持
GET /api/v1/products                    # 稳定版本
GET /api/v2/products                    # 新版本
GET /api/beta/products                  # 测试版本

# Header版本控制
GET /api/products
API-Version: v1                         # 指定版本
Accept: application/vnd.api+json        # 内容协商
```

### 版本废弃管理
```http
# 废弃版本响应头
Deprecated: true
Sunset: Wed, 31 Dec 2025 23:59:59 GMT  # 版本停用时间
Link: </api/v2/products>; rel="successor-version"  # 升级版本
```

## ⚡ 性能优化标准

### HTTP缓存策略
```http
# 静态资源缓存
Cache-Control: public, max-age=31536000, immutable
ETag: "abc123def456"
Last-Modified: Wed, 23 Sep 2025 10:00:00 GMT

# 动态内容缓存
Cache-Control: private, max-age=300
Vary: Accept, Authorization
X-Cache-Key: user_123_products_page_1

# 禁止缓存敏感数据
Cache-Control: no-cache, no-store, must-revalidate
Pragma: no-cache
Expires: 0
```

### 内容压缩传输
```http
# 客户端压缩支持声明
Accept-Encoding: gzip, deflate, br, zstd

# 服务端压缩响应
Content-Encoding: gzip
Vary: Accept-Encoding
X-Compressed-Size: 1024
X-Original-Size: 4096
```

### API限流控制
```http
# 限流信息响应头
X-RateLimit-Limit: 1000                # 限制总数
X-RateLimit-Remaining: 999             # 剩余请求数
X-RateLimit-Reset: 1640995200          # 重置时间戳
X-RateLimit-Window: 3600               # 时间窗口(秒)
Retry-After: 60                        # 重试等待时间

# 限流策略标识
X-RateLimit-Policy: user               # 限流策略类型
X-RateLimit-Scope: user_123456         # 限流范围标识
```

### 性能监控响应头
```http
# 性能指标
X-Response-Time: 150ms                 # 响应耗时
X-Database-Queries: 3                  # 数据库查询次数
X-Cache-Status: HIT                    # 缓存命中状态
X-Server-ID: srv_001                   # 服务器标识
X-Trace-ID: trace_abc123               # 链路追踪ID
```

## 📚 API文档标准

### OpenAPI规范要求
- **规范版本**: 使用OpenAPI 3.1规范确保最新特性支持
- **文档完整性**: 包含完整的接口、参数、响应、错误说明
- **自动化生成**: 通过代码注解自动生成，确保文档与实现同步
- **交互式调试**: 支持Swagger UI在线调试功能

### 文档结构标准
```yaml
# openapi.yaml 结构示例
openapi: 3.1.0
info:
  title: E-commerce Platform API
  version: 1.0.0
  description: 农产品电商平台API文档
  contact:
    name: API Support
    email: api@ecommerce.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.ecommerce.com/v1
    description: 生产环境
  - url: https://staging.api.ecommerce.com/v1
    description: 测试环境

paths:
  /user-auth/login:
    post:
      tags: [用户认证]
      summary: 用户登录
      description: 用户通过邮箱密码进行登录认证
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginRequest'
            example:
              email: "user@example.com"
              password: "password123"
      responses:
        '200':
          description: 登录成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginResponse'
```

### 文档内容质量标准
| 文档部分 | 质量要求 | 必需内容 |
|----------|----------|----------|
| **接口描述** | 业务功能清晰说明 | 用途、业务场景、注意事项 |
| **参数定义** | 类型、约束、示例完整 | 数据类型、格式、验证规则 |
| **响应规范** | 成功和错误情况完整 | 状态码、数据结构、错误类型 |
| **示例代码** | 真实可用的示例 | 请求示例、响应示例、错误示例 |
| **业务规则** | 业务逻辑和限制说明 | 权限要求、业务约束、使用限制 |

### 模块化文档管理
```tree
docs/
├── api/
│   ├── openapi.yaml                    # 全局API契约
│   └── modules/
│       ├── user-auth/
│       │   ├── api-spec.md            # 用户认证API规范
│       │   └── examples/              # 请求响应示例
│       ├── product-catalog/
│       │   ├── api-spec.md            # 商品管理API规范
│       │   └── examples/
│       └── ...                        # 其他模块API文档
```

### 文档维护流程
1. **开发阶段**: 编写API时同步更新文档注解
2. **代码审查**: 检查文档完整性和准确性
3. **自动化验证**: CI/CD中验证文档与实现一致性
4. **版本发布**: 生成版本化的API文档
5. **持续改进**: 收集用户反馈，持续优化文档质量

### 文档自动化工具
```python
# FastAPI自动文档生成示例
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="E-commerce API",
    description="农产品电商平台API",
    version="1.0.0",
    docs_url="/docs",          # Swagger UI地址
    redoc_url="/redoc"         # ReDoc地址
)

class LoginRequest(BaseModel):
    """用户登录请求"""
    email: str = Field(..., example="user@example.com", description="用户邮箱")
    password: str = Field(..., min_length=6, example="password123", description="用户密码")

@app.post("/user-auth/login", 
          summary="用户登录",
          description="用户通过邮箱密码进行登录认证",
          response_description="返回JWT Token和用户信息")
async def login(request: LoginRequest):
    """
    用户登录接口
    
    - **email**: 用户注册邮箱
    - **password**: 用户密码，最少6位字符
    
    返回包含JWT Token的标准响应格式
    """
    pass
```
