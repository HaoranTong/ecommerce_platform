<!--
文档说明：
- 内容：数据库工具模块API接口规范，定义数据库脚本和工具函数的接口
- 使用方法：数据库维护和测试时的标准参考，开发工具的接口契约
- 更新方法：工具功能变更时同步更新，保持与脚本实现一致
- 引用关系：基于database-utils/overview.md，被开发和运维流程引用
- 更新频率：工具脚本变更时
-->

# 数据库工具模块API规范

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## API设计原则

数据库工具模块提供命令行工具和函数库，用于数据库的管理和维护。

### 工具分类
- **初始化工具**: 数据库创建和初始化
- **迁移工具**: 数据库结构变更管理
- **测试工具**: 测试数据库操作辅助
- **维护工具**: 数据库性能分析和优化

## 命令行工具API

### 1. 数据库初始化
```bash
# 创建数据库
python -m app.utils.db_init create_database

# 创建所有表
python -m app.utils.db_init create_tables

# 初始化基础数据
python -m app.utils.db_init seed_data
```

### 2. 数据库迁移
```bash
# 生成迁移文件
alembic revision --autogenerate -m "migration_description"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 3. 测试数据管理
```bash
# 创建测试数据
python -m app.utils.test_data create_test_users --count=100
python -m app.utils.test_data create_test_products --count=500

# 清理测试数据
python -m app.utils.test_data cleanup_test_data
```

## 函数库API

### 数据库连接工具
```python
from app.utils.db_utils import get_db_connection, execute_query

# 获取数据库连接
conn = get_db_connection()

# 执行查询
result = execute_query("SELECT COUNT(*) FROM users")
```

### 性能分析工具
```python
from app.utils.performance import analyze_query_performance

# 分析查询性能
stats = analyze_query_performance("SELECT * FROM products WHERE category_id = 1")
```

### 数据验证工具
```python
from app.utils.validation import validate_data_integrity

# 验证数据完整性
validation_result = validate_data_integrity()
```

## 配置管理

### 环境配置
```python
# 开发环境
DATABASE_URL = "mysql://user:pass@localhost/dev_db"

# 测试环境
TEST_DATABASE_URL = "mysql://user:pass@localhost/test_db"

# 生产环境
PROD_DATABASE_URL = "mysql://user:pass@prod-server/prod_db"
```

## 性能要求

- **脚本执行时间**: 初始化 < 30s, 迁移 < 60s
- **内存使用**: 单次操作 < 100MB
- **错误处理**: 完整的错误日志和回滚机制
- **并发安全**: 支持多环境并行操作
