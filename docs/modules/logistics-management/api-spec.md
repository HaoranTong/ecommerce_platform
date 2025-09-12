# 物流管理模块API规范

📝 **状态**: 草稿  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## API设计原则

基于[API设计标准](../../standards/api-standards.md)，遵循RESTful设计风格。

### 基础路径
- **Base URL**: `/api/v1/logistics`
- **认证方式**: Bearer JWT Token
- **内容类型**: application/json

## 配送方式管理API

### 1. 获取配送方式
#### GET /api/v1/logistics/delivery-methods
获取可用的配送方式

**查询参数**:
- `address`: 收货地址
- `product_type`: 商品类型

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "method_id": 1,
      "name": "标准配送",
      "delivery_time": "3-5个工作日",
      "cost": 10.00,
      "available": true
    },
    {
      "method_id": 2,
      "name": "冷链配送",
      "delivery_time": "1-2个工作日",
      "cost": 25.00,
      "available": true
    }
  ]
}
```

### 2. 计算配送费用
#### POST /api/v1/logistics/calculate-shipping
计算配送费用

**请求参数**:
```json
{
  "origin": "北京市朝阳区",
  "destination": "上海市浦东新区",
  "weight": 2.5,
  "volume": 0.01,
  "delivery_method": "standard"
}
```

## 物流跟踪API

### 1. 创建物流订单
#### POST /api/v1/logistics/shipments
创建物流配送订单

**请求参数**:
```json
{
  "order_id": 12345,
  "carrier": "sf_express",
  "delivery_method": "standard",
  "recipient": {
    "name": "张三",
    "phone": "13800138000",
    "address": "上海市浦东新区XX路XX号"
  },
  "products": [
    {
      "product_id": 1,
      "quantity": 2,
      "weight": 1.5
    }
  ]
}
```

### 2. 查询物流状态
#### GET /api/v1/logistics/shipments/{shipment_id}/tracking
查询物流配送状态

**响应示例**:
```json
{
  "success": true,
  "data": {
    "shipment_id": "SF123456789",
    "status": "in_transit",
    "current_location": "上海转运中心",
    "estimated_delivery": "2025-09-15T18:00:00Z",
    "tracking_history": [
      {
        "timestamp": "2025-09-13T10:00:00Z",
        "location": "北京分拣中心",
        "status": "picked_up",
        "description": "快件已揽收"
      }
    ]
  }
}
```

## 冷链配送API

### 1. 创建冷链订单
#### POST /api/v1/logistics/cold-chain
创建冷链配送订单

**请求参数**:
```json
{
  "order_id": 12345,
  "temperature_range": {
    "min": 2,
    "max": 8
  },
  "special_requirements": "易碎品",
  "delivery_time_preference": "morning"
}
```

### 2. 温度监控
#### GET /api/v1/logistics/cold-chain/{shipment_id}/temperature
查询冷链配送温度记录

**响应示例**:
```json
{
  "success": true,
  "data": {
    "shipment_id": "CC123456",
    "current_temperature": 4.5,
    "temperature_records": [
      {
        "timestamp": "2025-09-13T10:00:00Z",
        "temperature": 4.2,
        "location": "配送车辆"
      }
    ],
    "alerts": []
  }
}
```

## 自提服务API

### 1. 查询自提点
#### GET /api/v1/logistics/pickup-points
查询附近的自提点

**查询参数**:
- `latitude`: 纬度
- `longitude`: 经度
- `radius`: 搜索半径（公里）

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "point_id": 1,
      "name": "XX便利店",
      "address": "上海市浦东新区XX路XX号",
      "distance": 0.5,
      "operating_hours": "08:00-22:00",
      "available": true
    }
  ]
}
```

### 2. 预约自提
#### POST /api/v1/logistics/pickup-appointment
预约自提服务

**请求参数**:
```json
{
  "order_id": 12345,
  "pickup_point_id": 1,
  "preferred_date": "2025-09-15",
  "preferred_time": "14:00"
}
```

## 物流成本分析API

### 1. 成本统计
#### GET /api/v1/logistics/cost-analysis
获取物流成本统计

**查询参数**:
- `start_date`: 开始日期
- `end_date`: 结束日期
- `region`: 配送区域

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_cost": 15000.00,
    "total_shipments": 1200,
    "average_cost_per_shipment": 12.50,
    "cost_by_method": {
      "standard": 8000.00,
      "express": 5000.00,
      "cold_chain": 2000.00
    }
  }
}
```

## 状态码说明

- 200: 成功
- 400: 请求参数错误
- 401: 未授权
- 404: 配送信息不存在
- 409: 配送冲突（如地址不在配送范围）
- 500: 服务器内部错误