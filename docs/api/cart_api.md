# 购物车API文档

## API概述

购物车API提供完整的购物车管理功能，支持商品添加、查看、修改、删除等操作。所有API均需要用户认证。

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证方式**: Bearer Token
- **Content-Type**: `application/json`
- **API版本**: v1

## 认证

所有购物车API都需要在请求头中包含有效的JWT Token：

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## API端点

### 1. 添加商品到购物车

**端点**: `POST /cart/add`

**描述**: 将指定商品添加到当前用户的购物车中。如果商品已存在，则增加数量。

**请求体**:
```json
{
  "product_id": 1,
  "quantity": 2
}
```

**请求参数**:
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| product_id | integer | 是 | 商品ID，必须大于0 |
| quantity | integer | 是 | 添加数量，范围1-99 |

**成功响应** (200):
```json
{
  "message": "商品已添加到购物车",
  "cart_count": 1,
  "total_quantity": 2
}
```

**错误响应**:
- `400` - 库存不足或参数无效
- `404` - 商品不存在或已下架
- `401` - 认证失败

### 2. 获取购物车详情

**端点**: `GET /cart`

**描述**: 获取当前用户购物车的详细信息，包括所有商品和汇总统计。

**成功响应** (200):
```json
{
  "user_id": 123,
  "items": [
    {
      "product_id": 1,
      "product_name": "五常大米",
      "product_sku": "RICE-001",
      "price": 99.99,
      "quantity": 2,
      "subtotal": 199.98,
      "stock_quantity": 50,
      "image_url": "https://example.com/rice.jpg"
    }
  ],
  "total_items": 1,
  "total_quantity": 2,
  "total_amount": 199.98
}
```

**响应字段说明**:
| 字段 | 类型 | 描述 |
|------|------|------|
| user_id | integer | 用户ID |
| items | array | 购物车商品列表 |
| total_items | integer | 商品种类数量 |
| total_quantity | integer | 商品总数量 |
| total_amount | decimal | 购物车总金额 |

**商品项字段**:
| 字段 | 类型 | 描述 |
|------|------|------|
| product_id | integer | 商品ID |
| product_name | string | 商品名称 |
| product_sku | string | 商品SKU |
| price | decimal | 单价 |
| quantity | integer | 数量 |
| subtotal | decimal | 小计 |
| stock_quantity | integer | 库存数量 |
| image_url | string | 商品图片URL |

### 3. 更新购物车商品数量

**端点**: `PUT /cart/items/{product_id}`

**描述**: 更新购物车中指定商品的数量。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| product_id | integer | 商品ID |

**请求体**:
```json
{
  "quantity": 3
}
```

**请求参数**:
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| quantity | integer | 是 | 新数量，0表示删除，范围0-99 |

**成功响应** (200):
```json
{
  "message": "购物车商品数量已更新",
  "cart_count": 1,
  "total_quantity": 3
}
```

### 4. 从购物车移除商品

**端点**: `DELETE /cart/items/{product_id}`

**描述**: 从购物车中完全移除指定商品。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| product_id | integer | 商品ID |

**成功响应** (200):
```json
{
  "message": "商品已从购物车移除",
  "cart_count": 0,
  "total_quantity": 0
}
```

**错误响应**:
- `404` - 商品不在购物车中

### 5. 清空购物车

**端点**: `DELETE /cart/clear`

**描述**: 清空当前用户的整个购物车。

**成功响应** (200):
```json
{
  "message": "购物车已清空",
  "cart_count": 0,
  "total_quantity": 0
}
```

### 6. 获取购物车统计

**端点**: `GET /cart/count`

**描述**: 获取购物车的基本统计信息，用于显示购物车角标等。

**成功响应** (200):
```json
{
  "cart_count": 2,
  "total_quantity": 5
}
```

**响应字段**:
| 字段 | 类型 | 描述 |
|------|------|------|
| cart_count | integer | 购物车中商品种类数量 |
| total_quantity | integer | 购物车中商品总数量 |

## 错误处理

### 通用错误格式
```json
{
  "detail": "错误描述信息"
}
```

### 错误码说明

| 状态码 | 描述 | 常见原因 |
|--------|------|----------|
| 400 | 请求参数错误 | 数量超出范围、库存不足 |
| 401 | 认证失败 | Token无效或过期 |
| 404 | 资源不存在 | 商品不存在、商品不在购物车中 |
| 500 | 服务器错误 | Redis连接失败、数据库错误 |

### 具体错误示例

**库存不足**:
```json
{
  "detail": "库存不足，当前库存：10"
}
```

**商品不存在**:
```json
{
  "detail": "商品不存在或已下架"
}
```

**认证失败**:
```json
{
  "detail": "Not authenticated"
}
```

## 业务规则

### 数量限制
- 单次添加数量：1-99
- 购物车中单商品最大数量：99
- 总数量受库存限制

### 库存验证
- 添加商品时检查库存充足性
- 考虑购物车中已有数量
- 库存不足时返回详细错误信息

### 数据一致性
- 购物车数据存储在Redis中
- 商品信息实时从数据库获取
- 自动清理已下架商品

## 使用示例

### JavaScript/Fetch示例

```javascript
// 添加商品到购物车
async function addToCart(productId, quantity, token) {
  const response = await fetch('http://localhost:8000/api/cart/add', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      product_id: productId,
      quantity: quantity
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
}

// 获取购物车详情
async function getCart(token) {
  const response = await fetch('http://localhost:8000/api/cart', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
}
```

### PowerShell示例

```powershell
# 设置认证头
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# 添加商品到购物车
$addData = @{
    product_id = 1
    quantity = 2
}
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/cart/add" `
    -Method Post -Body ($addData | ConvertTo-Json) -Headers $headers

# 获取购物车详情
$cart = Invoke-RestMethod -Uri "http://localhost:8000/api/cart" `
    -Method Get -Headers $headers
```

### Python/Requests示例

```python
import requests

# 认证头
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# 添加商品到购物车
add_data = {
    'product_id': 1,
    'quantity': 2
}
response = requests.post(
    'http://localhost:8000/api/cart/add',
    json=add_data,
    headers=headers
)

# 获取购物车详情
cart = requests.get(
    'http://localhost:8000/api/cart',
    headers=headers
).json()
```

## 测试工具

### 使用PowerShell测试脚本
```powershell
# 执行完整购物车测试
.\test_cart_system.ps1

# 或使用开发工具
.\dev_tools.ps1 test-cart
```

### 使用OpenAPI文档
访问 `http://localhost:8000/docs` 获取交互式API文档。

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2025-09-09 | 初始版本，包含基础购物车功能 |

## 相关文档

- [购物车系统技术文档](shopping_cart_system.md)
- [开发工具使用指南](../development_tools_guide.md)
- [认证API文档](auth_api.md)
