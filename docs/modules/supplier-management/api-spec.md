# 供应商管理模块API规范

📝 **状态**: 草稿  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## API设计原则

基于[API设计标准](../../standards/api-standards.md)，遵循RESTful设计风格。

### 基础路径
- **Base URL**: `/api/v1/suppliers`
- **认证方式**: Bearer JWT Token
- **内容类型**: application/json

## 供应商入驻API

### 1. 提交入驻申请
#### POST /api/v1/suppliers/applications
提交供应商入驻申请

**请求参数**:
```json
{
  "company_name": "XX农业公司",
  "contact_person": "张三",
  "phone": "13800138000",
  "email": "contact@company.com",
  "business_license": "license_url",
  "product_categories": ["fruits", "vegetables"]
}
```

### 2. 查询申请状态
#### GET /api/v1/suppliers/applications/{application_id}
查询入驻申请状态

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 123,
    "status": "pending_review",
    "company_name": "XX农业公司",
    "submitted_at": "2025-09-13T10:00:00Z"
  }
}
```

## 绩效考核API

### 1. 获取供应商评级
#### GET /api/v1/suppliers/{supplier_id}/rating
获取供应商综合评级

**响应示例**:
```json
{
  "success": true,
  "data": {
    "supplier_id": 123,
    "overall_rating": 4.5,
    "quality_rating": 4.6,
    "delivery_rating": 4.4,
    "service_rating": 4.5
  }
}
```

### 2. 提交质量评估
#### POST /api/v1/suppliers/{supplier_id}/quality-assessment
提交质量评估报告

**请求参数**:
```json
{
  "product_batch": "BATCH001",
  "quality_score": 4.5,
  "assessment_notes": "产品质量符合标准"
}
```

## 数据服务API

### 1. 获取销售数据
#### GET /api/v1/suppliers/{supplier_id}/sales-data
获取供应商销售数据

**查询参数**:
- `start_date`: 开始日期
- `end_date`: 结束日期
- `granularity`: 数据粒度 (daily/weekly/monthly)

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_sales": 125000.00,
    "total_orders": 458,
    "average_order_value": 273.00,
    "top_products": [
      {
        "product_id": 1,
        "name": "有机苹果",
        "sales": 25000.00
      }
    ]
  }
}
```

## 资金服务API

### 1. 查询结算记录
#### GET /api/v1/suppliers/{supplier_id}/settlements
查询资金结算记录

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "settlement_id": 1,
      "amount": 95000.00,
      "settlement_date": "2025-09-10",
      "status": "completed"
    }
  ]
}
```

## 状态码说明

- 200: 成功
- 400: 请求参数错误
- 401: 未授权
- 403: 权限不足
- 404: 供应商不存在
- 500: 服务器内部错误