# 数据分析模块API规范

📝 **状态**: 草稿  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## API设计原则

基于[API设计标准](../../standards/api-standards.md)，遵循RESTful设计风格。

### 基础路径
- **Base URL**: `/api/v1/analytics`
- **认证方式**: Bearer JWT Token
- **内容类型**: application/json

## 用户行为分析API

### 1. 用户行为统计
#### GET /api/v1/analytics/user-behavior
获取用户行为统计数据

**查询参数**:
- `user_id`: 用户ID（可选）
- `start_date`: 开始日期
- `end_date`: 结束日期
- `behavior_type`: 行为类型 (view/search/purchase)

**响应示例**:
```json
{
  "success": true,
  "data": {
    "page_views": 12500,
    "unique_visitors": 3200,
    "search_queries": 850,
    "conversion_rate": 0.125,
    "top_viewed_products": [
      {
        "product_id": 1,
        "views": 450,
        "name": "有机苹果"
      }
    ]
  }
}
```

### 2. 用户路径分析
#### GET /api/v1/analytics/user-journey
分析用户购买路径

**查询参数**:
- `user_id`: 用户ID
- `session_id`: 会话ID

## 销售数据分析API

### 1. 销售趋势
#### GET /api/v1/analytics/sales-trends
获取销售趋势数据

**查询参数**:
- `granularity`: 数据粒度 (daily/weekly/monthly)
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_revenue": 125000.00,
    "total_orders": 1250,
    "average_order_value": 100.00,
    "trends": [
      {
        "date": "2025-09-01",
        "revenue": 5200.00,
        "orders": 52
      }
    ]
  }
}
```

### 2. 热门产品分析
#### GET /api/v1/analytics/popular-products
获取热门产品统计

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "product_id": 1,
      "name": "有机苹果",
      "sales_volume": 1250,
      "revenue": 25000.00,
      "growth_rate": 0.15
    }
  ]
}
```

## 运营效果分析API

### 1. 活动效果分析
#### GET /api/v1/analytics/campaign-performance/{campaign_id}
获取营销活动效果

**响应示例**:
```json
{
  "success": true,
  "data": {
    "campaign_id": 123,
    "participants": 1500,
    "conversion_rate": 0.18,
    "revenue": 85000.00,
    "roi": 3.2,
    "cost_per_acquisition": 25.50
  }
}
```

## 客户价值分析API

### 1. RFM分析
#### GET /api/v1/analytics/rfm-analysis
获取客户RFM分析

**响应示例**:
```json
{
  "success": true,
  "data": {
    "segments": [
      {
        "segment": "champions",
        "count": 150,
        "avg_clv": 2500.00,
        "characteristics": {
          "recency": "high",
          "frequency": "high",
          "monetary": "high"
        }
      }
    ]
  }
}
```

## 智能报表API

### 1. 生成自定义报表
#### POST /api/v1/analytics/reports/generate
生成自定义分析报表

**请求参数**:
```json
{
  "report_type": "sales_summary",
  "filters": {
    "start_date": "2025-09-01",
    "end_date": "2025-09-13",
    "product_categories": ["fruits"]
  },
  "metrics": ["revenue", "orders", "conversion_rate"]
}
```

### 2. 获取报表列表
#### GET /api/v1/analytics/reports
获取已生成的报表列表

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "report_id": 1,
      "name": "九月销售汇总",
      "type": "sales_summary",
      "generated_at": "2025-09-13T10:00:00Z",
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
- 404: 数据不存在
- 500: 服务器内部错误