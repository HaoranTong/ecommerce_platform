# 客服系统模块API规范

📝 **状态**: 草稿  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## API设计原则

基于[API设计标准](../../standards/api-standards.md)，遵循RESTful设计风格。

### 基础路径
- **Base URL**: `/api/v1/customer-service`
- **认证方式**: Bearer JWT Token
- **内容类型**: application/json

## 在线客服API

### 1. 创建客服会话
#### POST /api/v1/customer-service/sessions
创建客服会话

**请求参数**:
```json
{
  "user_id": 123,
  "issue_type": "order_inquiry",
  "message": "订单问题咨询"
}
```

### 2. 发送消息
#### POST /api/v1/customer-service/sessions/{session_id}/messages
发送客服消息

**请求参数**:
```json
{
  "sender_type": "customer",
  "content": "我的订单什么时候发货？",
  "message_type": "text"
}
```

## 服务工单API

### 1. 创建工单
#### POST /api/v1/customer-service/tickets
创建服务工单

**请求参数**:
```json
{
  "user_id": 123,
  "category": "product_issue",
  "title": "商品质量问题",
  "description": "收到的商品有质量问题",
  "priority": "high"
}
```

### 2. 查询工单状态
#### GET /api/v1/customer-service/tickets/{ticket_id}
查询工单详情

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 12345,
    "status": "processing",
    "title": "商品质量问题",
    "created_at": "2025-09-13T10:00:00Z",
    "updated_at": "2025-09-13T10:30:00Z"
  }
}
```

## 知识库API

### 1. 搜索FAQ
#### GET /api/v1/customer-service/faq/search
搜索常见问题

**查询参数**:
- `q`: 搜索关键词
- `category`: 问题分类

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "question": "如何修改订单地址？",
      "answer": "在订单未发货前，可以在订单详情页修改收货地址。",
      "category": "order_management"
    }
  ]
}
```

## 状态码说明

- 200: 成功
- 400: 请求参数错误
- 401: 未授权
- 404: 资源不存在
- 500: 服务器内部错误