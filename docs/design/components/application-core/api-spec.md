<!--
文档说明：
- 内容：应用核心模块API接口规范，定义应用启动、健康检查、路由管理的接口
- 使用方法：服务部署和监控时的标准参考，系统集成的接口契约
- 更新方法：应用核心功能变更时同步更新，保持与实现代码一致
- 引用关系：基于application-core/overview.md，被运维部署文档引用
- 更新频率：应用架构变更时
-->

# 应用核心模块API规范

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## API设计原则

基于[API设计标准](../../standards/api-standards.md)，遵循RESTful设计风格。

### 基础路径
- **Base URL**: `/api/v1/system`
- **认证方式**: 无需认证（系统级接口）
- **内容类型**: application/json

## 系统健康检查API

### 1. 应用健康检查
#### GET /api/health
检查应用整体健康状态

**请求参数**: 无

**响应示例**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-09-13T10:00:00Z",
    "version": "1.0.0",
    "uptime": 3600,
    "checks": {
      "database": "healthy",
      "redis": "healthy",
      "external_services": "healthy"
    }
  }
}
```

### 2. 详细健康检查
#### GET /api/health/detailed
获取详细的系统健康状态

**请求参数**: 无

**响应示例**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "components": {
      "database": {
        "status": "healthy",
        "response_time": 5,
        "connection_pool": {
          "active": 2,
          "idle": 8,
          "max": 10
        }
      },
      "redis": {
        "status": "healthy",
        "response_time": 1,
        "memory_usage": "45%"
      },
      "disk_space": {
        "status": "healthy",
        "available": "85%"
      }
    }
  }
}
```

## 应用信息API

### 3. 应用信息
#### GET /api/info
获取应用基本信息

**请求参数**: 无

**响应示例**:
```json
{
  "success": true,
  "data": {
    "name": "ecommerce-platform",
    "version": "1.0.0",
    "environment": "production",
    "build_time": "2025-09-13T08:00:00Z",
    "python_version": "3.11.5",
    "fastapi_version": "0.104.1"
  }
}
```

### 4. 路由信息
#### GET /api/routes
获取所有可用路由信息（仅开发环境）

**请求参数**: 无

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_routes": 45,
    "routes": [
      {
        "path": "/api/v1/users",
        "methods": ["GET", "POST"],
        "module": "user-auth"
      },
      {
        "path": "/api/v1/products",
        "methods": ["GET", "POST"],
        "module": "product-catalog"
      }
    ]
  }
}
```

## 系统管理API

### 5. 应用重启
#### POST /api/admin/restart
重启应用（仅管理员权限）

**请求头**: 
```
Authorization: Bearer {admin_token}
```

**请求参数**: 无

**响应示例**:
```json
{
  "success": true,
  "message": "应用重启指令已发送",
  "data": {
    "restart_time": "2025-09-13T10:05:00Z"
  }
}
```

### 6. 配置重载
#### POST /api/admin/reload-config
重新加载应用配置（仅管理员权限）

**请求头**: 
```
Authorization: Bearer {admin_token}
```

**请求参数**: 无

**响应示例**:
```json
{
  "success": true,
  "message": "配置重载成功",
  "data": {
    "reload_time": "2025-09-13T10:05:00Z",
    "changed_configs": ["database.pool_size", "redis.timeout"]
  }
}
```

## 错误码定义

| 错误码 | HTTP状态码 | 描述 | 解决方案 |
|-------|-----------|------|----------|
| SYS_001 | 503 | 数据库连接失败 | 检查数据库服务状态 |
| SYS_002 | 503 | Redis连接失败 | 检查Redis服务状态 |
| SYS_003 | 500 | 应用启动失败 | 检查应用配置和依赖 |
| SYS_004 | 403 | 管理员权限不足 | 使用管理员Token |

## 使用示例

### 监控脚本示例
```bash
# 健康检查脚本
#!/bin/bash
response=$(curl -s "http://localhost:8000/api/health")
status=$(echo $response | jq -r '.data.status')

if [ "$status" = "healthy" ]; then
    echo "应用健康状态正常"
    exit 0
else
    echo "应用健康状态异常: $response"
    exit 1
fi
```

### Docker健康检查
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1
```
