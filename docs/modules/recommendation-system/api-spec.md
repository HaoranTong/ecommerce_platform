<!--
文档说明：
- 内容：推荐系统模块API接口规范，定义推荐算法和个性化推荐的接口
- 使用方法：推荐功能开发时的标准参考，推荐服务的接口契约
- 更新方法：推荐算法变更时同步更新，保持与推荐逻辑一致
- 引用关系：基于recommendation-system/overview.md，被商品展示模块引用
- 更新频率：推荐算法优化时
-->

# 推荐系统模块API规范

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## API设计原则

基于[API设计标准](../../standards/api-standards.md)，遵循RESTful设计风格。

### 基础路径
- **Base URL**: `/api/v1/recommendations`
- **认证方式**: Bearer JWT Token（部分接口）
- **内容类型**: application/json

## 个性化推荐API

### 1. 用户个性化推荐
#### GET /api/v1/recommendations/user/{user_id}
为指定用户获取个性化商品推荐

**请求参数**:
- `user_id`: 用户ID (path parameter)
- `limit`: 推荐数量 (query parameter, 默认10)
- `category_id`: 限定分类 (query parameter, 可选)

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user_id": 123,
    "recommendations": [
      {
        "product_id": 456,
        "product_name": "五常大米 5kg装",
        "price": 89.90,
        "image_url": "https://cdn.example.com/rice1.jpg",
        "score": 0.95,
        "reason": "基于您的购买历史"
      }
    ],
    "algorithm": "collaborative_filtering",
    "generated_at": "2025-09-13T10:00:00Z"
  }
}
```

### 2. 商品相似推荐
#### GET /api/v1/recommendations/similar/{product_id}
基于商品相似性的推荐

**请求参数**:
- `product_id`: 商品ID (path parameter)
- `limit`: 推荐数量 (query parameter, 默认10)

**响应示例**:
```json
{
  "success": true,
  "data": {
    "product_id": 456,
    "similar_products": [
      {
        "product_id": 789,
        "product_name": "东北大米 5kg装",
        "price": 79.90,
        "similarity_score": 0.88,
        "similarity_factors": ["品类相同", "价格接近", "用户重叠"]
      }
    ]
  }
}
```

### 3. 热门商品推荐
#### GET /api/v1/recommendations/trending
获取热门商品推荐

**请求参数**:
- `category_id`: 分类ID (query parameter, 可选)
- `limit`: 推荐数量 (query parameter, 默认10)
- `time_range`: 时间范围 (query parameter, 默认"7d")

**响应示例**:
```json
{
  "success": true,
  "data": {
    "trending_products": [
      {
        "product_id": 123,
        "product_name": "有机蔬菜礼盒",
        "price": 128.00,
        "trend_score": 0.92,
        "sales_growth": "150%",
        "view_count": 5280
      }
    ],
    "time_range": "7d",
    "updated_at": "2025-09-13T10:00:00Z"
  }
}
```

## 实时推荐API

### 4. 基于浏览行为的推荐
#### POST /api/v1/recommendations/browse
基于用户当前浏览行为的实时推荐

**请求参数**:
```json
{
  "user_id": 123,
  "current_product_id": 456,
  "browse_history": [789, 234, 567],
  "session_duration": 300
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "real_time_recommendations": [
      {
        "product_id": 890,
        "product_name": "农家蜂蜜 500g",
        "price": 68.00,
        "recommendation_type": "browse_based",
        "confidence": 0.87
      }
    ]
  }
}
```

### 5. 购物车智能推荐
#### POST /api/v1/recommendations/cart
基于购物车内容的推荐

**请求参数**:
```json
{
  "user_id": 123,
  "cart_items": [
    {"product_id": 456, "quantity": 2},
    {"product_id": 789, "quantity": 1}
  ]
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "cart_recommendations": [
      {
        "product_id": 234,
        "product_name": "精装茶叶礼盒",
        "price": 158.00,
        "recommendation_type": "complement",
        "reason": "与购物车商品搭配"
      }
    ]
  }
}
```

## 推荐管理API

### 6. 更新用户偏好
#### POST /api/v1/recommendations/preferences/{user_id}
更新用户偏好数据

**请求参数**:
```json
{
  "categories": [1, 3, 5],
  "price_range": {"min": 50, "max": 200},
  "brand_preferences": ["品牌A", "品牌B"],
  "dietary_restrictions": ["有机", "无添加"]
}
```

### 7. 推荐反馈
#### POST /api/v1/recommendations/feedback
用户对推荐结果的反馈

**请求参数**:
```json
{
  "user_id": 123,
  "product_id": 456,
  "action": "click|view|add_to_cart|purchase|ignore",
  "recommendation_id": "rec_789",
  "timestamp": "2025-09-13T10:00:00Z"
}
```

## 推荐算法配置API

### 8. 算法权重配置
#### GET /api/v1/recommendations/config
获取推荐算法配置

**响应示例**:
```json
{
  "success": true,
  "data": {
    "algorithms": {
      "collaborative_filtering": {"weight": 0.4, "enabled": true},
      "content_based": {"weight": 0.3, "enabled": true},
      "trending": {"weight": 0.2, "enabled": true},
      "real_time": {"weight": 0.1, "enabled": true}
    }
  }
}
```

## 性能要求

- **响应时间**: < 200ms (实时推荐)
- **推荐准确率**: > 15% (点击率)
- **推荐覆盖率**: > 80% (商品覆盖)
- **并发支持**: 1000+ 并发请求

## 错误码定义

| 错误码 | HTTP状态码 | 描述 | 解决方案 |
|-------|-----------|------|----------|
| REC_001 | 404 | 用户推荐数据不存在 | 使用默认推荐算法 |
| REC_002 | 400 | 推荐参数无效 | 检查请求参数格式 |
| REC_003 | 500 | 推荐算法执行失败 | 降级到简单推荐 |
| REC_004 | 429 | 推荐请求频率过高 | 实施频率限制 |