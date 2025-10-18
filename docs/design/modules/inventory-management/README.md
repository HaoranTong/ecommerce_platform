---
title: "库存管理模块快速指南"
version: "v1.1.0"
status: "active"
created: "2025-09-15"
updated: "2025-10-18"
owner: "开发团队"
dependencies:
  - "docs/design/modules/inventory-management/design.md"
  - "docs/design/modules/inventory-management/requirements.md"
labels:
  - "inventory-management"
  - "quick-guide"
---

# 库存管理模块 (Inventory Management Module)

<!--
文件名：README.md
文件路径：docs/design/modules/inventory-management/README.md
文档类型：模块快速指南
模块名称：库存管理模块 (Inventory Management Module)
文档版本：v1.0.0
创建时间：2025-09-15
最后修改：2025-09-15
维护人员：产品经理/开发工程师
文档状态：正式版本

文档用途：
- 提供库存管理模块的快速入门指南
- 包含环境配置、安装部署和基本使用方法
- 为开发者提供快速上手的参考资料

相关文档：
- 详细需求：requirements.md
- 系统设计：design.md
- 技术实现：implementation.md
- API说明：api-implementation.md
-->

## 依赖标准

本文档遵循以下标准规范：

| 标准文档 | 版本 | 应用范围 |
|---------|------|---------|
| [API设计标准](../../standards/api-standards.md) | v1.0 | RESTful API设计、路由命名 |
| [数据库设计标准](../../standards/database-standards.md) | v1.0 | 表结构设计、字段命名、索引设计 |
| [架构设计标准](../../standards/architecture-standards.md) | v1.0 | 四层架构、Repository模式、依赖注入 |
| [应用架构](../../architecture/application-architecture.md) | v1.0 | 模块化单体、模块边界、依赖管理 |

**架构版本**: V2.0 - 四层架构 (Router → Service → Repository → Model)
## 模块概述

库存管理模块是电商平台的核心基础模块，负责商品库存的全生命周期管理，包括库存查询、预留、扣减、释放以及库存监控等功能。该模块确保平台商品库存数据的准确性和一致性，支持高并发场景下的库存操作。

## 核心功能

### 🔍 库存查询
- 实时库存查询
- 批量库存查询
- 库存历史记录查询
- 库存变更日志

### 📦 库存管理
- 库存入库/出库
- 库存预留/释放
- 库存扣减/回退
- 库存调整/盘点

### 📊 库存监控
- 库存预警机制
- 低库存通知
- 库存统计报表
- 实时库存监控

### 🔐 安全控制
- 操作权限控制
- 审计日志记录
- 数据完整性保护
- 并发安全控制

## 技术架构

### 技术栈
- **Web框架**: FastAPI 0.104.1
- **ORM**: SQLAlchemy 2.0.23
- **数据验证**: Pydantic 2.5.0
- **数据库**: MySQL 8.0 (主) + Redis 7.0 (缓存)
- **Python版本**: 3.10+
- **部署方式**: Docker Compose

### 四层架构设计 ⭐

```text
┌──────────────────────────────────────────────────┐
│  Router Layer (router.py)                        │
│  • API端点定义                                    │
│  • 请求响应处理                                   │
│  • 数据验证(Pydantic)                             │
└──────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────┐
│  Service Layer (service.py)                      │
│  • 业务流程编排                                   │
│  • 业务规则验证                                   │
│  • 事务管理                                       │
└──────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────┐
│  Repository Layer (repository.py) ⭐NEW          │
│  • 数据访问封装                                   │
│  • 查询构建                                       │
│  • 缓存策略                                       │
└──────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────┐
│  Model Layer (models.py)                         │
│  • ORM模型定义                                    │
│  • 数据库约束                                     │
│  • 实体关系映射                                   │
└──────────────────────────────────────────────────┘
```text

### 模块文件结构

```python
app/modules/inventory_management/
├── __init__.py          # 模块初始化
├── models.py            # 数据模型 (SQLAlchemy ORM)
├── repository.py        # 数据操作层 ⭐NEW
├── service.py           # 业务逻辑层
├── schemas.py           # 数据传输对象 (Pydantic)
├── router.py            # API路由层
├── dependencies.py      # 依赖注入
└── README.md            # 模块说明
```text

## 快速开始

### 环境要求
- Python 3.11+
- PostgreSQL 14+
- Redis 7.0+
- Docker 20.10+ (可选)

### 安装依赖
```bash
# 安装Python依赖
pip install -r requirements.txt

# 启动数据库服务 (使用Docker)
docker-compose up -d postgres redis
```text

### 数据库初始化
```bash
# 运行数据库迁移
alembic upgrade head

# 初始化基础数据
python scripts/init_inventory_data.py
```python

### 启动服务
```bash
# 开发模式启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 或使用开发脚本
./start.ps1
```text

## API使用示例

### 查询库存
```python
import httpx

# 查询单个SKU库存
response = httpx.get("http://localhost:8000/api/v1/inventory-management/SKU001")
print(response.json())

# 批量查询库存
response = httpx.post(
    "http://localhost:8000/api/v1/inventory-management/batch-query",
    json={"sku_codes": ["SKU001", "SKU002", "SKU003"]}
)
print(response.json())
```json

### 库存预留
```python
# 预留库存
response = httpx.post(
    "http://localhost:8000/api/v1/inventory-management/reserve",
    json={
        "sku_code": "SKU001",
        "quantity": 10,
        "business_type": "ORDER",
        "business_id": "ORDER_12345",
        "expires_at": "2024-01-15T10:00:00Z"
    }
)
print(response.json())
```json

### 库存扣减
```python
# 确认扣减库存
response = httpx.post(
    "http://localhost:8000/api/v1/inventory-management/deduct",
    json={
        "sku_code": "SKU001",
        "quantity": 5,
        "business_type": "ORDER",
        "business_id": "ORDER_12345"
    }
)
print(response.json())
```json

## 开发指南

### 项目结构
```text
app/modules/inventory_management/
├── __init__.py
├── router.py              # API路由
├── service.py             # 业务服务
├── repository.py          # 数据仓储
├── models.py             # 数据模型
├── schemas.py            # 请求/响应模式
├── exceptions.py         # 自定义异常
├── constants.py          # 常量定义
└── utils.py              # 工具函数
```text

### 代码规范
- 遵循 PEP 8 代码风格
- 使用 Type Hints 进行类型注解
- 编写完整的单元测试
- 添加详细的文档字符串

### 测试运行
```bash
# 运行所有测试
pytest tests/

# 运行库存模块测试
pytest tests/test_inventory_management.py -v

# 运行覆盖率测试
pytest --cov=app.modules.inventory_management tests/
```text

## 配置说明

### 环境变量
```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce
REDIS_URL=redis://localhost:6379/0

# 库存配置
INVENTORY_CACHE_TTL=300
INVENTORY_BATCH_SIZE=1000
INVENTORY_RESERVATION_TTL=1800

# 监控配置
ENABLE_METRICS=true
METRICS_PORT=8001
```text

### 性能调优
- 数据库索引优化
- Redis 缓存策略
- 连接池配置
- 批量操作优化

## 监控和运维

### 健康检查
```bash
# 检查服务状态
curl http://localhost:8000/health

# 检查数据库连接
curl http://localhost:8000/health/database

# 检查Redis连接
curl http://localhost:8000/health/redis
```text

### 关键指标
- 库存查询QPS
- 库存操作成功率
- 数据库响应时间
- 缓存命中率
- 错误率统计

### 日志监控
```bash
# 查看应用日志
tail -f logs/inventory.log

# 查看错误日志
grep "ERROR" logs/inventory.log | tail -20
```text

## 常见问题

### Q: 如何处理库存不足的情况？
A: 系统会抛出 `InsufficientInventoryError` 异常，前端需要捕获并提示用户。

### Q: 预留库存过期后会自动释放吗？
A: 是的，系统有定时任务会清理过期的预留库存。

### Q: 支持分布式环境下的库存同步吗？
A: 支持，使用Redis分布式锁确保库存操作的原子性。

### Q: 如何进行库存盘点？
A: 可以使用库存调整接口，支持批量调整和审计记录。

## 相关文档

- [需求规格说明书](./requirements.md) - 详细的功能需求和业务规则
- [系统设计文档](./design.md) - 架构设计和技术选型
- [实现指南](./implementation.md) - 具体的实现细节和代码结构  
- [API实现文档](./api-implementation.md) - 详细的API端点和使用说明
- [模块概览](./overview.md) - 模块的整体介绍
- [API规格](./api-spec.md) - API接口规范

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0.0 | 2024-01-10 | 初始版本，基础库存管理功能 |
| v1.1.0 | 2024-01-15 | 添加批量操作和性能优化 |
| v1.2.0 | 2024-01-20 | 增加监控和告警功能 |

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/inventory-enhancement`)
3. 提交更改 (`git commit -am 'Add some feature'`)
4. 推送到分支 (`git push origin feature/inventory-enhancement`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](../../../LICENSE) 文件。
