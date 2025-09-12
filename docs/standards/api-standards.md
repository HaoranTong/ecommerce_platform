<!--
文档说明：
- 内容：API设计的全局标准和规范，不包含具体API接口定义
- 使用方法：开发API时遵循的设计规范，确保API一致性
- 更新方法：API设计标准变更时更新，需要架构师确认
- 引用关系：被各模块的API文档引用，被workflow-standards.md引用
- 更新频率：设计标准变化时
-->

# API设计标准

## 设计原则

### RESTful 设计原则
1. **资源导向** - URL 表示资源，HTTP 方法表示操作
2. **无状态** - 每个请求包含完整的处理信息
3. **统一接口** - 一致的 API 设计风格
4. **分层系统** - 客户端无需关心服务端实现细节
5. **按需代码** - 支持按需扩展功能

### API 设计原则
- **一致性** - 统一的命名、结构、错误处理
- **简洁性** - 简单易懂的接口设计
- **完整性** - 完整的输入验证和输出信息
- **可扩展性** - 支持版本管理和向后兼容
- **安全性** - 完善的认证授权和数据保护

## URL 设计规范

### 基础规范
```
协议://域名/api版本/资源路径?查询参数
https://api.example.com/v1/products?category=rice&page=1
```

### 命名规范
- **资源名称**: 使用复数名词 (`products`, `orders`, `users`)
- **URL路径**: 小写字母 + 连字符 (`product-categories`)
- **查询参数**: 小写字母 + 下划线 (`page_size`, `created_at`)
- **避免动词**: URL 中不使用动词，用 HTTP 方法表示操作

### 路径结构
```
# 基础商品管理
GET    /api/v1/products           # 获取商品列表
GET    /api/v1/products/{id}      # 获取指定商品
POST   /api/v1/products           # 创建商品
PUT    /api/v1/products/{id}      # 更新商品
DELETE /api/v1/products/{id}      # 删除商品

# 嵌套资源
GET    /api/v1/products/{id}/reviews     # 获取商品评论
POST   /api/v1/products/{id}/reviews     # 创建商品评论

# 农产品电商特色API
GET    /api/v1/products/{id}/batches     # 获取商品批次信息
GET    /api/v1/batches/{id}/trace        # 获取批次溯源信息
POST   /api/v1/batches/{id}/trace        # 记录溯源信息

# 会员和积分系统
GET    /api/v1/members/{id}/points       # 获取会员积分
POST   /api/v1/members/{id}/points       # 增加积分记录
GET    /api/v1/members/{id}/rewards      # 获取会员奖励

# 分销商管理
GET    /api/v1/distributors              # 获取分销商列表
POST   /api/v1/distributors/applications # 提交分销商申请
GET    /api/v1/distributors/{id}/commissions # 获取分销佣金

# 社交电商功能
POST   /api/v1/products/{id}/share       # 分享商品
GET    /api/v1/group-orders              # 获取拼团订单
POST   /api/v1/group-orders              # 发起拼团
POST   /api/v1/group-orders/{id}/join    # 参与拼团

# 营销活动
GET    /api/v1/campaigns                 # 获取活动列表
GET    /api/v1/coupons                   # 获取优惠券
POST   /api/v1/coupons/{id}/claim        # 领取优惠券
```

## HTTP 方法使用

### 标准方法
| 方法 | 用途 | 幂等性 | 安全性 |
|------|------|--------|--------|
| GET | 查询资源 | ✅ | ✅ |
| POST | 创建资源 | ❌ | ❌ |
| PUT | 更新/替换资源 | ✅ | ❌ |
| PATCH | 部分更新资源 | ❌ | ❌ |
| DELETE | 删除资源 | ✅ | ❌ |

### 使用场景
```bash
# 查询操作
GET /api/v1/products                    # 获取商品列表
GET /api/v1/products/123                # 获取指定商品
GET /api/v1/products?category=rice      # 条件查询

# 创建操作
POST /api/v1/products                   # 创建新商品
POST /api/v1/orders                     # 创建订单

# 更新操作
PUT /api/v1/products/123                # 完整更新商品
PATCH /api/v1/products/123              # 部分更新商品

# 删除操作
DELETE /api/v1/products/123             # 删除商品
```

## 请求格式规范

### Content-Type
- **JSON**: `application/json` (主要格式)
- **表单**: `application/x-www-form-urlencoded`
- **文件上传**: `multipart/form-data`
- **文本**: `text/plain`

### 请求头标准
```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer {token}
X-Request-ID: {uuid}
X-Client-Version: 1.0.0
```

### 请求体结构
```json
{
  "data": {
    "name": "五常大米",
    "price": 99.99,
    "category_id": 1,
    "description": "优质五常大米"
  },
  "metadata": {
    "request_id": "req_123456789",
    "timestamp": "2025-09-10T10:00:00Z"
  }
}
```

## 响应格式规范

### 统一响应结构
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    // 具体业务数据
  },
  "metadata": {
    "request_id": "req_123456789",
    "timestamp": "2025-09-10T10:00:00Z",
    "execution_time": 150
  }
}
```

### 分页响应结构
```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "items": [
      // 数据列表
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_pages": 5,
      "total_items": 100,
      "has_next": true,
      "has_prev": false
    }
  },
  "metadata": {
    "request_id": "req_123456789",
    "timestamp": "2025-09-10T10:00:00Z"
  }
}
```

## 状态码规范

### 成功状态码
- **200 OK** - 请求成功，有返回数据
- **201 Created** - 资源创建成功
- **202 Accepted** - 请求已接受，异步处理
- **204 No Content** - 请求成功，无返回数据

### 客户端错误状态码
- **400 Bad Request** - 请求参数错误
- **401 Unauthorized** - 认证失败
- **403 Forbidden** - 权限不足
- **404 Not Found** - 资源不存在
- **409 Conflict** - 资源冲突
- **422 Unprocessable Entity** - 请求格式正确，但语义错误
- **429 Too Many Requests** - 请求频率限制

### 服务器错误状态码
- **500 Internal Server Error** - 服务器内部错误
- **502 Bad Gateway** - 网关错误
- **503 Service Unavailable** - 服务不可用
- **504 Gateway Timeout** - 网关超时

## 错误处理规范

### 错误响应结构
```json
{
  "success": false,
  "code": 400,
  "message": "请求参数错误",
  "error": {
    "type": "VALIDATION_ERROR",
    "details": [
      {
        "field": "price",
        "message": "价格必须大于0",
        "code": "INVALID_VALUE"
      }
    ]
  },
  "metadata": {
    "request_id": "req_123456789",
    "timestamp": "2025-09-10T10:00:00Z"
  }
}
```

### 错误类型定义
```python
# 错误类型枚举
class ErrorType:
    VALIDATION_ERROR = "VALIDATION_ERROR"       # 参数验证错误
    AUTHENTICATION_ERROR = "AUTH_ERROR"        # 认证错误
    AUTHORIZATION_ERROR = "AUTHZ_ERROR"        # 授权错误
    RESOURCE_NOT_FOUND = "NOT_FOUND"          # 资源不存在
    BUSINESS_ERROR = "BUSINESS_ERROR"         # 业务逻辑错误
    SYSTEM_ERROR = "SYSTEM_ERROR"             # 系统错误
```

## 认证授权规范

### JWT Token 规范
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token 结构
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "123456",
    "username": "user@example.com",
    "roles": ["user", "premium"],
    "exp": 1640995200,
    "iat": 1640908800
  }
}
```

### 权限验证
- **公开接口** - 无需认证
- **用户接口** - 需要有效 Token
- **管理接口** - 需要管理员权限
- **敏感操作** - 需要额外验证

## 版本管理规范

### 版本策略
- **URL版本控制**: `/api/v1/`, `/api/v2/`
- **语义化版本**: 主版本.次版本.修订版本 (1.0.0)
- **向后兼容**: 同一主版本内保持向后兼容
- **废弃声明**: 提前通知版本废弃计划

### 版本切换
```http
# URL 版本控制
GET /api/v1/products
GET /api/v2/products

# Header 版本控制 (备选)
GET /api/products
API-Version: v1
```

## 性能优化规范

### 缓存策略
```http
# 响应头缓存控制
Cache-Control: public, max-age=3600
ETag: "abc123"
Last-Modified: Wed, 10 Sep 2025 10:00:00 GMT
```

### 压缩传输
```http
# 请求头
Accept-Encoding: gzip, deflate, br

# 响应头
Content-Encoding: gzip
```

### 限流控制
```http
# 响应头
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## 文档规范

### OpenAPI 规范
- 使用 OpenAPI 3.0 规范
- 完整的接口文档和示例
- 自动生成和更新
- 支持在线调试

### 文档内容
- **接口描述** - 清晰的功能说明
- **参数说明** - 详细的参数定义
- **示例代码** - 完整的请求响应示例
- **错误说明** - 可能的错误情况和处理

### 文档维护
- 代码变更同步更新文档
- 定期审查文档准确性
- 版本变更记录
- 用户反馈收集和改进
