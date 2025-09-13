<!--
文档说明：
- 内容：数据库核心模块API接口规范，定义数据库连接管理、事务处理的接口
- 使用方法：数据库操作和监控时的标准参考，数据库性能分析的接口契约
- 更新方法：数据库连接策略变更时同步更新，保持与实现代码一致
- 引用关系：基于database-core/overview.md，被数据访问层模块引用
- 更新频率：数据库架构变更时
-->

# 数据库核心模块API规范

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## API设计原则

基于[API设计标准](../../standards/api-standards.md)，遵循RESTful设计风格。

### 基础路径
- **Base URL**: `/api/v1/database`
- **认证方式**: Bearer JWT Token（管理员权限）
- **内容类型**: application/json

## 数据库状态监控API

### 1. 数据库连接状态
#### GET /api/v1/database/status
获取数据库连接池状态

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
    "connection_pool": {
      "total_connections": 10,
      "active_connections": 3,
      "idle_connections": 7,
      "pool_size": 10,
      "max_overflow": 5
    },
    "performance": {
      "avg_query_time": 15.5,
      "slow_queries": 2,
      "total_queries": 1250
    }
  }
}
```

### 2. 数据库性能指标
#### GET /api/v1/database/metrics
获取数据库性能指标

**请求参数**:
- `time_range`: 时间范围 (1h, 24h, 7d)

**响应示例**:
```json
{
  "success": true,
  "data": {
    "time_range": "1h",
    "metrics": {
      "query_count": 1250,
      "avg_response_time": 15.5,
      "max_response_time": 125.0,
      "error_count": 2,
      "cache_hit_rate": 85.2
    },
    "slow_queries": [
      {
        "query": "SELECT * FROM products WHERE...",
        "duration": 125.0,
        "timestamp": "2025-09-13T10:00:00Z"
      }
    ]
  }
}
```

## 数据库管理API

### 3. 连接池管理
#### POST /api/v1/database/pool/refresh
刷新数据库连接池

**请求头**: 
```
Authorization: Bearer {admin_token}
```

**响应示例**:
```json
{
  "success": true,
  "message": "连接池刷新成功",
  "data": {
    "refresh_time": "2025-09-13T10:05:00Z",
    "old_connections": 10,
    "new_connections": 10
  }
}
```

### 4. 数据库迁移状态
#### GET /api/v1/database/migrations
获取数据库迁移状态

**响应示例**:
```json
{
  "success": true,
  "data": {
    "current_version": "v1.2.3",
    "pending_migrations": [
      {
        "version": "v1.2.4",
        "description": "添加批次溯源表",
        "created_at": "2025-09-13T09:00:00Z"
      }
    ],
    "migration_history": [
      {
        "version": "v1.2.3",
        "applied_at": "2025-09-12T15:30:00Z",
        "status": "success"
      }
    ]
  }
}
```

## 错误码定义

| 错误码 | HTTP状态码 | 描述 | 解决方案 |
|-------|-----------|------|----------|
| DB_001 | 503 | 数据库连接池耗尽 | 等待连接释放或增加池大小 |
| DB_002 | 500 | 数据库连接超时 | 检查网络和数据库状态 |
| DB_003 | 500 | SQL执行错误 | 检查SQL语法和数据完整性 |
| DB_004 | 403 | 权限不足 | 使用管理员权限访问 |