<!--
文档说明：
- 内容：Redis缓存模块API接口规范，定义缓存管理、会话存储的接口
- 使用方法：缓存操作和监控时的标准参考，缓存性能分析的接口契约
- 更新方法：缓存策略变更时同步更新，保持与实现代码一致
- 引用关系：基于redis-cache/overview.md，被缓存相关模块引用
- 更新频率：缓存架构变更时
-->

# Redis缓存模块API规范

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## API设计原则

基于[API设计标准](../../standards/api-standards.md)，遵循RESTful设计风格。

### 基础路径
- **Base URL**: `/api/v1/cache`
- **认证方式**: Bearer JWT Token（管理员权限）
- **内容类型**: application/json

## 缓存状态监控API

### 1. Redis连接状态
#### GET /api/v1/cache/status
获取Redis连接和缓存状态

**请求头**: 
```
Authorization: Bearer {admin_token}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "redis_info": {
      "version": "7.0.11",
      "uptime": 86400,
      "connected_clients": 12,
      "memory_usage": "256MB",
      "memory_peak": "512MB"
    },
    "cache_stats": {
      "hit_rate": 85.5,
      "total_keys": 1250,
      "expired_keys": 45
    }
  }
}
```

### 2. 缓存性能指标
#### GET /api/v1/cache/metrics
获取缓存性能指标

**请求参数**:
- `time_range`: 时间范围 (1h, 24h, 7d)

**响应示例**:
```json
{
  "success": true,
  "data": {
    "time_range": "1h",
    "performance": {
      "commands_processed": 5420,
      "hit_rate": 85.5,
      "miss_rate": 14.5,
      "avg_response_time": 0.5,
      "peak_memory": "512MB"
    },
    "key_distribution": {
      "user_sessions": 450,
      "shopping_carts": 320,
      "product_cache": 280,
      "other": 200
    }
  }
}
```

## 缓存管理API

### 3. 清除缓存
#### DELETE /api/v1/cache/keys
清除指定的缓存键

**请求体**:
```json
{
  "pattern": "user:*",
  "confirm": true
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "缓存清除成功",
  "data": {
    "deleted_keys": 45,
    "pattern": "user:*"
  }
}
```

### 4. 缓存预热
#### POST /api/v1/cache/warmup
执行缓存预热

**请求体**:
```json
{
  "modules": ["products", "categories"],
  "force": false
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "缓存预热完成",
  "data": {
    "warmed_keys": 150,
    "duration": "5.2s",
    "modules": ["products", "categories"]
  }
}
```

## 错误码定义

| 错误码 | HTTP状态码 | 描述 | 解决方案 |
|-------|-----------|------|----------|
| CACHE_001 | 503 | Redis连接失败 | 检查Redis服务状态 |
| CACHE_002 | 500 | 缓存操作超时 | 检查网络和Redis性能 |
| CACHE_003 | 400 | 无效的缓存键模式 | 检查键名格式 |
| CACHE_004 | 403 | 权限不足 | 使用管理员权限访问 |