# 质量控制模块API规范文档

## 文档信息
- **模块名称**: 质量控制模块 (Quality Control Module)
- **API版本**: v1.0.0
- **OpenAPI规范**: 3.0.3
- **创建时间**: 2024-01-20
- **维护人员**: API开发团队

## API基础信息
- **Base URL**: `/quality-control`
- **协议**: HTTPS
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

## 全局配置

### OpenAPI规范定义
```yaml
openapi: 3.0.3
info:
  title: 质量控制模块API
  description: 农产品质量认证管理系统API
  version: 1.0.0
  contact:
    name: API支持
    email: api-support@company.com
servers:
  - url: https://api.company.com/quality-control
    description: 生产环境
  - url: https://api-dev.company.com/quality-control
    description: 开发环境
```

### 认证配置
```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: JWT认证令牌

security:
  - BearerAuth: []
```

## 数据模型定义

### Certificate模型
```yaml
components:
  schemas:
    Certificate:
      type: object
      required:
        - id
        - serial
        - name
        - issuer
        - issued_at
        - expires_at
        - is_active
        - created_at
        - updated_at
      properties:
        id:
          type: integer
          format: int32
          description: 证书唯一标识
          example: 1
        serial:
          type: string
          maxLength: 100
          description: 证书序列号（全局唯一）
          example: "QC2024001"
        name:
          type: string
          maxLength: 255
          description: 证书名称
          example: "有机农产品认证"
        issuer:
          type: string
          maxLength: 255
          description: 颁发机构
          example: "国家农业部质量监督中心"
        description:
          type: string
          nullable: true
          description: 证书描述信息
          example: "符合GB/T 19630-2019有机产品认证标准"
        issued_at:
          type: string
          format: date-time
          description: 证书颁发时间
          example: "2024-01-15T10:30:00Z"
        expires_at:
          type: string
          format: date-time
          description: 证书过期时间
          example: "2025-01-15T10:30:00Z"
        is_active:
          type: boolean
          description: 证书是否有效
          example: true
        created_at:
          type: string
          format: date-time
          description: 记录创建时间
          example: "2024-01-15T10:30:00Z"
        updated_at:
          type: string
          format: date-time
          description: 记录更新时间
          example: "2024-01-15T10:30:00Z"

    CertificateCreate:
      type: object
      required:
        - serial
        - name
        - issuer
        - issued_at
        - expires_at
      properties:
        serial:
          type: string
          maxLength: 100
          description: 证书序列号（全局唯一）
          example: "QC2024001"
        name:
          type: string
          maxLength: 255
          description: 证书名称
          example: "有机农产品认证"
        issuer:
          type: string
          maxLength: 255
          description: 颁发机构
          example: "国家农业部质量监督中心"
        description:
          type: string
          nullable: true
          description: 证书描述信息
          example: "符合GB/T 19630-2019有机产品认证标准"
        issued_at:
          type: string
          format: date-time
          description: 证书颁发时间
          example: "2024-01-15T10:30:00Z"
        expires_at:
          type: string
          format: date-time
          description: 证书过期时间（必须晚于颁发时间）
          example: "2025-01-15T10:30:00Z"
        is_active:
          type: boolean
          default: true
          description: 证书是否有效
          example: true

    CertificateList:
      type: array
      items:
        $ref: '#/components/schemas/Certificate'

    ErrorResponse:
      type: object
      required:
        - error
      properties:
        error:
          type: object
          required:
            - code
            - message
          properties:
            code:
              type: string
              description: 错误代码
              example: "QC_CERT_001"
            message:
              type: string
              description: 错误消息
              example: "证书序列号已存在"
            details:
              type: object
              description: 错误详细信息
              example:
                field: "serial"
                value: "QC2024001"

    SuccessResponse:
      type: object
      required:
        - message
      properties:
        message:
          type: string
          description: 成功消息
          example: "操作成功"
        data:
          type: object
          description: 返回数据

## API端点定义

### 1. 创建证书
```yaml
paths:
  /certificates:
    post:
      summary: 创建新的质量证书
      description: 为农产品创建质量认证证书
      operationId: createCertificate
      tags:
        - 证书管理
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CertificateCreate'
            examples:
              organic_cert:
                summary: 有机产品认证
                value:
                  serial: "QC2024001"
                  name: "有机农产品认证"
                  issuer: "国家农业部质量监督中心"
                  description: "符合GB/T 19630-2019有机产品认证标准"
                  issued_at: "2024-01-15T10:30:00Z"
                  expires_at: "2025-01-15T10:30:00Z"
                  is_active: true
      responses:
        '201':
          description: 证书创建成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Certificate'
              examples:
                created_cert:
                  summary: 创建成功的证书
                  value:
                    id: 1
                    serial: "QC2024001"
                    name: "有机农产品认证"
                    issuer: "国家农业部质量监督中心"
                    description: "符合GB/T 19630-2019有机产品认证标准"
                    issued_at: "2024-01-15T10:30:00Z"
                    expires_at: "2025-01-15T10:30:00Z"
                    is_active: true
                    created_at: "2024-01-15T10:30:00Z"
                    updated_at: "2024-01-15T10:30:00Z"
        '400':
          description: 请求数据无效
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
              examples:
                duplicate_serial:
                  summary: 序列号重复错误
                  value:
                    error:
                      code: "QC_CERT_001"
                      message: "证书序列号已存在"
                      details:
                        field: "serial"
                        value: "QC2024001"
                invalid_date:
                  summary: 日期无效错误
                  value:
                    error:
                      code: "QC_CERT_004"
                      message: "过期时间必须晚于颁发时间"
                      details:
                        field: "expires_at"
        '401':
          description: 未授权访问
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '422':
          description: 数据验证失败
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: 服务器内部错误
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
```

### 2. 获取证书列表
```yaml
    get:
      summary: 获取证书列表
      description: 分页获取质量证书列表，支持多种筛选条件
      operationId: listCertificates
      tags:
        - 证书管理
      security:
        - BearerAuth: []
      parameters:
        - name: skip
          in: query
          description: 跳过的记录数（分页用）
          required: false
          schema:
            type: integer
            minimum: 0
            default: 0
            example: 0
        - name: limit
          in: query
          description: 每页返回的记录数
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
            example: 20
        - name: issuer
          in: query
          description: 按颁发机构筛选
          required: false
          schema:
            type: string
            maxLength: 255
            example: "国家农业部质量监督中心"
        - name: is_active
          in: query
          description: 按证书状态筛选
          required: false
          schema:
            type: boolean
            example: true
        - name: serial
          in: query
          description: 按序列号筛选
          required: false
          schema:
            type: string
            maxLength: 100
            example: "QC2024001"
      responses:
        '200':
          description: 获取成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    $ref: '#/components/schemas/CertificateList'
                  total:
                    type: integer
                    description: 总记录数
                  skip:
                    type: integer
                    description: 跳过的记录数
                  limit:
                    type: integer
                    description: 每页记录数
              examples:
                cert_list:
                  summary: 证书列表
                  value:
                    data:
                      - id: 1
                        serial: "QC2024001"
                        name: "有机农产品认证"
                        issuer: "国家农业部质量监督中心"
                        description: "符合有机产品标准"
                        issued_at: "2024-01-15T10:30:00Z"
                        expires_at: "2025-01-15T10:30:00Z"
                        is_active: true
                        created_at: "2024-01-15T10:30:00Z"
                        updated_at: "2024-01-15T10:30:00Z"
                      - id: 2
                        serial: "QC2024002"
                        name: "绿色食品认证"
                        issuer: "中国绿色食品发展中心"
                        description: "A级绿色食品认证"
                        issued_at: "2024-01-16T14:20:00Z"
                        expires_at: "2027-01-16T14:20:00Z"
                        is_active: true
                        created_at: "2024-01-16T14:20:00Z"
                        updated_at: "2024-01-16T14:20:00Z"
                    total: 50
                    skip: 0
                    limit: 20
        '401':
          description: 未授权访问
        '500':
          description: 服务器内部错误
```

### 3. 获取证书详情
```yaml
  /certificates/{cert_id}:
    get:
      summary: 获取指定证书详情
      description: 根据证书ID获取详细信息
      operationId: getCertificate
      tags:
        - 证书管理
      security:
        - BearerAuth: []
      parameters:
        - name: cert_id
          in: path
          description: 证书ID
          required: true
          schema:
            type: integer
            format: int32
            minimum: 1
            example: 1
      responses:
        '200':
          description: 获取成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Certificate'
              examples:
                cert_detail:
                  summary: 证书详情
                  value:
                    id: 1
                    serial: "QC2024001"
                    name: "有机农产品认证"
                    issuer: "国家农业部质量监督中心"
                    description: "符合GB/T 19630-2019有机产品认证标准，经过严格的质量检验和认证流程"
                    issued_at: "2024-01-15T10:30:00Z"
                    expires_at: "2025-01-15T10:30:00Z"
                    is_active: true
                    created_at: "2024-01-15T10:30:00Z"
                    updated_at: "2024-01-15T10:30:00Z"
        '404':
          description: 证书不存在
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
              examples:
                cert_not_found:
                  summary: 证书不存在
                  value:
                    error:
                      code: "QC_CERT_002"
                      message: "证书不存在"
                      details:
                        cert_id: 999
        '401':
          description: 未授权访问
        '500':
          description: 服务器内部错误
```

### 4. 删除证书
```yaml
    delete:
      summary: 删除指定证书
      description: 根据证书ID删除证书（软删除）
      operationId: deleteCertificate
      tags:
        - 证书管理
      security:
        - BearerAuth: []
      parameters:
        - name: cert_id
          in: path
          description: 证书ID
          required: true
          schema:
            type: integer
            format: int32
            minimum: 1
            example: 1
      responses:
        '204':
          description: 删除成功
        '404':
          description: 证书不存在
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
              examples:
                cert_not_found:
                  summary: 证书不存在
                  value:
                    error:
                      code: "QC_CERT_002"
                      message: "证书不存在"
                      details:
                        cert_id: 999
        '409':
          description: 删除冲突（证书正在使用中）
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
              examples:
                cert_in_use:
                  summary: 证书使用中
                  value:
                    error:
                      code: "QC_CERT_005"
                      message: "证书正在使用中，无法删除"
                      details:
                        cert_id: 1
                        related_products: ["产品A", "产品B"]
        '401':
          description: 未授权访问
        '500':
          description: 服务器内部错误
```

## 错误码定义

| 错误码 | HTTP状态码 | 错误描述 | 解决方案 |
|--------|------------|----------|----------|
| QC_CERT_001 | 400 | 证书序列号已存在 | 使用不同的序列号 |
| QC_CERT_002 | 404 | 证书不存在 | 检查证书ID是否正确 |
| QC_CERT_003 | 400 | 证书已过期 | 更新证书有效期 |
| QC_CERT_004 | 422 | 数据验证失败 | 检查请求数据格式 |
| QC_CERT_005 | 409 | 证书删除失败 | 先解除证书关联关系 |
| QC_AUTH_001 | 401 | 认证失败 | 检查JWT令牌 |
| QC_AUTH_002 | 403 | 权限不足 | 联系管理员获取权限 |
| QC_RATE_001 | 429 | 请求频率超限 | 降低请求频率 |
| QC_SERVER_001 | 500 | 服务器内部错误 | 联系技术支持 |

## 请求/响应示例

### 创建证书完整示例
**请求**:
```bash
curl -X POST "https://api.company.com/quality-control/certificates" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "serial": "QC2024001",
    "name": "有机农产品认证",
    "issuer": "国家农业部质量监督中心",
    "description": "符合GB/T 19630-2019有机产品认证标准",
    "issued_at": "2024-01-15T10:30:00Z",
    "expires_at": "2025-01-15T10:30:00Z",
    "is_active": true
  }'
```

**响应**:
```json
{
  "id": 1,
  "serial": "QC2024001",
  "name": "有机农产品认证",
  "issuer": "国家农业部质量监督中心",
  "description": "符合GB/T 19630-2019有机产品认证标准",
  "issued_at": "2024-01-15T10:30:00Z",
  "expires_at": "2025-01-15T10:30:00Z",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## 性能规范

### 响应时间要求
- **单个证书查询**: < 200ms (P95)
- **证书列表查询**: < 500ms (P95)  
- **证书创建**: < 1000ms (P95)
- **证书删除**: < 500ms (P95)

### 并发性能
- **最大并发数**: 1000 QPS
- **单用户限流**: 100次/分钟
- **批量操作**: 单次最多100条记录

### 可用性要求
- **系统可用性**: 99.9%
- **故障恢复时间**: < 5分钟
- **数据一致性**: 强一致性保证

## 版本变更记录

| 版本 | 日期 | 变更内容 | 影响范围 |
|------|------|----------|----------|
| v1.0.0 | 2024-01-20 | 初始版本，定义证书管理基础API | 新功能 |
| v1.0.1 | 2024-01-25 | 增加错误码定义和示例 | 文档完善 |
| v1.0.2 | 2024-02-01 | 完善性能规范和验证规则 | 规范完善 |
```

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | /api/v1/quality-control/health | 健康检查 | 待实现 |

详细API规范请参考 [standards/openapi.yaml](../../standards/openapi.yaml)
