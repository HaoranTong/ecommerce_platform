# 质量控制模块 API 规范

## 模块概述
质量控制模块API负责农产品质量认证证书的管理，包括证书的创建、查询、验证和删除功能。

### 开发进度
- **设计阶段**: ✅ 已完成
- **开发阶段**: ✅ 已完成（基础功能）
- **测试阶段**: 🔄 进行中

## API 路径前缀
所有质量控制模块的API都使用统一的路径前缀：`/api/v1/quality-control`

## 认证要求
- 所有API端点都需要有效的JWT认证令牌
- 部分管理功能需要管理员权限

## 证书管理API

### 1. 创建证书
#### POST /api/v1/quality-control/certificates
创建新的质量认证证书记录

**请求参数**:
```json
{
    "name": "有机认证证书",
    "issuer": "中国有机产品认证中心", 
    "serial": "COFCC-R-2024-001234",
    "description": "有机蔬菜认证，有效期至2025年12月"
}
```

**参数说明**:
- `name` (string, 必填): 证书名称，最大长度200字符
- `issuer` (string, 可选): 发证机构名称，最大长度200字符
- `serial` (string, 必填): 证书序列号，必须唯一，最大长度200字符
- `description` (string, 可选): 证书描述信息

**响应示例**:
```json
{
    "id": 123,
    "name": "有机认证证书",
    "issuer": "中国有机产品认证中心",
    "serial": "COFCC-R-2024-001234",
    "description": "有机蔬菜认证，有效期至2025年12月"
}
```

**错误响应**:
```json
{
    "detail": "证书序列号已存在"
}
```

### 2. 获取证书列表
#### GET /api/v1/quality-control/certificates
获取质量认证证书列表，支持分页查询

**查询参数**:
- `skip` (int, 可选): 跳过的记录数，默认为0
- `limit` (int, 可选): 返回的记录数限制，默认为100

**请求示例**:
```http
GET /api/v1/quality-control/certificates?skip=0&limit=20
```

**响应示例**:
```json
[
    {
        "id": 123,
        "name": "有机认证证书",
        "issuer": "中国有机产品认证中心",
        "serial": "COFCC-R-2024-001234",
        "description": "有机蔬菜认证，有效期至2025年12月"
    },
    {
        "id": 124,
        "name": "绿色食品认证",
        "issuer": "中国绿色食品发展中心",
        "serial": "LB-2024-567890",
        "description": "绿色农产品认证"
    }
]
```

### 3. 获取证书详情
#### GET /api/v1/quality-control/certificates/{certificate_id}
根据证书ID获取特定证书的详细信息

**路径参数**:
- `certificate_id` (int, 必填): 证书的唯一标识ID

**请求示例**:
```http
GET /api/v1/quality-control/certificates/123
```

**响应示例**:
```json
{
    "id": 123,
    "name": "有机认证证书",
    "issuer": "中国有机产品认证中心",
    "serial": "COFCC-R-2024-001234",
    "description": "有机蔬菜认证，有效期至2025年12月"
}
```

**错误响应**:
```json
{
    "detail": "证书不存在"
}
```

### 4. 删除证书
#### DELETE /api/v1/quality-control/certificates/{certificate_id}
删除指定的质量认证证书记录

**路径参数**:
- `certificate_id` (int, 必填): 证书的唯一标识ID

**请求示例**:
```http
DELETE /api/v1/quality-control/certificates/123
```

**成功响应**: HTTP 204 No Content

**错误响应**:
```json
{
    "detail": "证书不存在"
}
```

## 常见错误码

| HTTP状态码 | 错误信息 | 说明 |
|------------|----------|------|
| 400 | 证书序列号已存在 | 创建证书时序列号重复 |
| 401 | Unauthorized | 认证令牌无效或缺失 |
| 403 | Forbidden | 权限不足 |
| 404 | 证书不存在 | 指定的证书ID不存在 |
| 422 | Validation Error | 请求参数验证失败 |
| 500 | Internal Server Error | 服务器内部错误 |

## 数据验证规则

### 证书创建验证
- **name**: 必填，长度1-200字符
- **serial**: 必填，长度1-200字符，必须唯一
- **issuer**: 可选，最大长度200字符
- **description**: 可选，无长度限制

### 业务规则
1. 证书序列号必须在系统中唯一
2. 证书名称不能为空字符串
3. 删除证书前需要检查是否被其他模块引用（未实现）

## 扩展功能（待开发）

### 1. 证书验证API
#### POST /api/v1/quality-control/certificates/{certificate_id}/verify
验证证书的真实性和有效性

### 2. 证书搜索API
#### GET /api/v1/quality-control/certificates/search
支持按证书名称、发证机构、序列号等条件搜索

### 3. 证书关联API
#### GET /api/v1/quality-control/certificates/by-product/{product_id}
获取指定商品相关的所有质量证书

#### GET /api/v1/quality-control/certificates/by-batch/{batch_id}
获取指定批次相关的所有质量证书

## 集成说明

### 与批次溯源模块集成
质量控制模块提供的证书信息将被批次溯源模块引用，用于展示每个批次的质量保证信息。

### 与商品管理模块集成
商品信息中可以关联相关的质量认证证书，提升消费者对商品质量的信任度。

### 与供应商管理模块集成
供应商的资质认证信息将通过质量控制模块进行管理和验证。

## 测试用例

### 单元测试覆盖
- ✅ 证书创建功能测试
- ✅ 证书查询功能测试
- ✅ 证书删除功能测试
- ✅ 错误处理测试
- 🔄 数据验证测试

### 集成测试覆盖
- 🔄 API端点集成测试
- ⏳ 与其他模块的集成测试
- ⏳ 性能测试

## 性能指标

### 响应时间要求
- 证书创建: < 500ms
- 证书查询: < 300ms
- 证书列表: < 1s (100条记录)
- 证书删除: < 200ms

### 并发支持
- 支持1000并发查询
- 支持100并发创建/删除操作

## 安全考虑

### 数据安全
- 所有API需要JWT认证
- 敏感操作记录审计日志
- 输入参数严格验证

### 权限控制
- 普通用户: 只能查询证书信息
- 管理员: 可以创建、修改、删除证书
- 供应商: 可以上传自己的认证证书（待实现）