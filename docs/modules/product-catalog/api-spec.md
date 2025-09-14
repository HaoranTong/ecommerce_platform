# Product Catalog API Specification

## Overview
产品目录模块API规范文档，定义了商品分类和商品管理的REST API接口。

## Base URL
```
/api/v1/products
```

## Authentication
所有API接口需要用户认证，使用JWT Bearer Token。

## API Endpoints

### Category Management

#### 1. Create Category
```
POST /api/v1/products/categories
```

**Request Body:**
```json
{
    "name": "分类名称",
    "description": "分类描述", 
    "parent_id": 1,
    "sort_order": 1,
    "is_active": true
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "分类名称",
        "description": "分类描述",
        "parent_id": 1,
        "sort_order": 1,
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
}
```

#### 2. Get Categories List
```
GET /api/v1/products/categories
```

**Query Parameters:**
- `parent_id` (optional): 父分类ID
- `is_active` (optional): 是否启用
- `page` (optional): 页码，默认1
- `size` (optional): 每页数量，默认20

**Response:**
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "id": 1,
                "name": "分类名称",
                "description": "分类描述",
                "parent_id": null,
                "sort_order": 1,
                "is_active": true,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ],
        "total": 1,
        "page": 1,
        "size": 20,
        "pages": 1
    }
}
```

#### 3. Get Category by ID
```
GET /api/v1/products/categories/{id}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "分类名称",
        "description": "分类描述",
        "parent_id": null,
        "sort_order": 1,
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
}
```

#### 4. Update Category
```
PUT /api/v1/products/categories/{id}
```

**Request Body:**
```json
{
    "name": "新分类名称",
    "description": "新分类描述",
    "parent_id": 1,
    "sort_order": 2,
    "is_active": false
}
```

#### 5. Delete Category
```
DELETE /api/v1/products/categories/{id}
```

**Response:**
```json
{
    "success": true,
    "message": "Category deleted successfully"
}
```

### Product Management

#### 1. Create Product
```
POST /api/v1/products
```

**Request Body:**
```json
{
    "name": "商品名称",
    "sku": "PROD-001",
    "description": "商品描述",
    "category_id": 1,
    "price": 99.99,
    "cost": 50.00,
    "stock_quantity": 100,
    "weight": 0.5,
    "dimensions": {
        "length": 10.0,
        "width": 5.0,
        "height": 2.0
    },
    "attributes": {
        "color": "红色",
        "size": "L",
        "material": "棉质"
    },
    "status": "active"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "商品名称",
        "sku": "PROD-001",
        "description": "商品描述",
        "category_id": 1,
        "price": 99.99,
        "cost": 50.00,
        "stock_quantity": 100,
        "weight": 0.5,
        "dimensions": {
            "length": 10.0,
            "width": 5.0,
            "height": 2.0
        },
        "attributes": {
            "color": "红色",
            "size": "L",
            "material": "棉质"
        },
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
}
```

#### 2. Get Products List
```
GET /api/v1/products
```

**Query Parameters:**
- `category_id` (optional): 分类ID
- `status` (optional): 商品状态
- `search` (optional): 搜索关键词（名称、SKU、描述）
- `min_price` (optional): 最低价格
- `max_price` (optional): 最高价格
- `page` (optional): 页码，默认1
- `size` (optional): 每页数量，默认20
- `sort` (optional): 排序字段（name, price, created_at）
- `order` (optional): 排序方向（asc, desc）

**Response:**
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "id": 1,
                "name": "商品名称",
                "sku": "PROD-001",
                "description": "商品描述",
                "category_id": 1,
                "price": 99.99,
                "cost": 50.00,
                "stock_quantity": 100,
                "weight": 0.5,
                "dimensions": {
                    "length": 10.0,
                    "width": 5.0,
                    "height": 2.0
                },
                "attributes": {
                    "color": "红色",
                    "size": "L",
                    "material": "棉质"
                },
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ],
        "total": 1,
        "page": 1,
        "size": 20,
        "pages": 1
    }
}
```

#### 3. Get Product by ID
```
GET /api/v1/products/{id}
```

#### 4. Update Product
```
PUT /api/v1/products/{id}
```

#### 5. Delete Product
```
DELETE /api/v1/products/{id}
```

#### 6. Update Product Stock
```
PATCH /api/v1/products/{id}/stock
```

**Request Body:**
```json
{
    "quantity": 50,
    "operation": "add"  // "add", "subtract", "set"
}
```

#### 7. Bulk Update Products
```
PATCH /api/v1/products/bulk
```

**Request Body:**
```json
{
    "product_ids": [1, 2, 3],
    "updates": {
        "status": "inactive"
    }
}
```

## Error Responses

### 400 Bad Request
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "请求参数验证失败",
        "details": [
            {
                "field": "name",
                "message": "商品名称不能为空"
            }
        ]
    }
}
```

### 401 Unauthorized
```json
{
    "success": false,
    "error": {
        "code": "UNAUTHORIZED",
        "message": "未授权访问"
    }
}
```

### 404 Not Found
```json
{
    "success": false,
    "error": {
        "code": "NOT_FOUND",
        "message": "资源不存在"
    }
}
```

### 409 Conflict
```json
{
    "success": false,
    "error": {
        "code": "DUPLICATE_SKU",
        "message": "SKU已存在"
    }
}
```

### 500 Internal Server Error
```json
{
    "success": false,
    "error": {
        "code": "INTERNAL_ERROR",
        "message": "服务器内部错误"
    }
}
```

## Rate Limiting
- 每个用户每分钟最多100次请求
- 批量操作每分钟最多10次请求

## Data Validation Rules

### Category
- `name`: 必填，1-100字符
- `description`: 可选，最多500字符
- `parent_id`: 可选，必须是有效的分类ID
- `sort_order`: 可选，整数，默认0

### Product
- `name`: 必填，1-200字符
- `sku`: 必填，唯一，1-100字符
- `description`: 可选，最多2000字符
- `price`: 必填，大于0的数值
- `cost`: 可选，大于等于0的数值
- `stock_quantity`: 必填，大于等于0的整数
- `weight`: 可选，大于0的数值
- `status`: 必填，枚举值：active, inactive, discontinued

## Security Considerations
1. 所有接口需要认证
2. 输入数据需要验证和净化
3. SQL注入防护
4. XSS攻击防护
5. API访问频率限制

## Performance Guidelines
1. 分页查询避免过大的size参数
2. 使用合适的索引优化查询性能
3. 批量操作限制数量上限
4. 实施缓存策略减少数据库压力