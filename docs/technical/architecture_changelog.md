# 架构变更日志

## 概述

本文档记录电商平台架构的重要变更，遵循文档驱动开发原则，确保所有架构决策可追溯。

## v1.1.0 - 电商核心架构稳定化 (2025-09-08)

### 🎯 目标
完成电商平台核心架构的稳定化，建立可扩展的技术基础。

### 📋 变更摘要

#### 数据模型扩展
- **新增模型**: Category, Order, OrderItem 
- **扩展模型**: User (新增 wx_openid 支持微信登录), Product (完善电商字段)
- **保留模型**: Certificate (向后兼容)
- **关系建立**: 完整的电商业务关系链 User ←→ Order ←→ OrderItem ←→ Product ←→ Category

#### 技术框架升级
- **Pydantic v2 兼容**: 
  - `regex` → `pattern` (Field 验证参数)
  - `orm_mode` → `from_attributes` (Model 配置)
  - 移除 `decimal_places` 约束参数
- **SQLAlchemy 2.x**: 使用现代 SQLAlchemy 语法和最佳实践
- **Alembic 迁移**: 建立干净的迁移链，移除历史垃圾文件

#### API 合约标准化
- **OpenAPI 3.0**: 完整的电商 API 规范定义
- **版本升级**: v1.0.0 → v1.1.0
- **端点覆盖**: 用户管理、商品目录、分类管理、订单处理、支付集成

#### 事件驱动架构
- **事件 Schema**: JSON Schema 定义 User.Created.v1, Product.Created.v1
- **扩展准备**: 为订单状态变更、库存变更等事件预留架构

### 🔧 技术细节

#### 数据库结构变更
```sql
-- 新增表
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INT REFERENCES categories(id),
    -- ...其他字段
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id INT REFERENCES users(id),
    -- ...其他字段
);

CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    product_id INT REFERENCES products(id),
    -- ...其他字段
);

-- 扩展现有表
ALTER TABLE users ADD COLUMN wx_openid VARCHAR(50) UNIQUE;
ALTER TABLE products ADD COLUMN category_id INT REFERENCES categories(id);
-- ...其他字段扩展
```

#### 迁移文件管理
- **清理**: 删除所有历史迁移和垃圾文件
- **重建**: 创建 `0001_initial.py` 作为唯一迁移入口
- **验证**: 确保迁移链完整且可重复执行

#### 应用启动验证
- **虚拟环境**: 确保在正确的 Python 虚拟环境中运行
- **依赖检查**: 验证所有 Python 包正确安装
- **服务连接**: 验证 MySQL 和 Redis 容器连接正常
- **API 响应**: 确认 FastAPI 应用正常启动和响应

### 📚 文档更新

#### 新增文档
- `docs/technical/data_models.md`: 完整的数据模型架构文档
- `docs/technical/architecture_changelog.md`: 本变更日志文档

#### 更新文档
- `docs/status/status.md`: 更新项目状态和完成进度
- `docs/technical/index.md`: 更新技术文档索引和版本信息
- `docs/openapi.yaml`: 升级到 v1.1.0，完善 API 规范描述

#### 事件 Schema 更新
- `docs/event-schemas/User.Created.v1.json`: 用户创建事件定义
- `docs/event-schemas/Product.Created.v1.json`: 商品创建事件定义

### ✅ 验证结果

#### 功能验证
- ✅ FastAPI 应用成功启动在 http://127.0.0.1:8000
- ✅ 数据库连接正常，所有表创建成功
- ✅ Alembic 迁移状态正确 (0001_initial)

## v1.1.1 - 自动化脚本修复与分支架构优化 (2025-09-08)

### 🎯 目标
修复 PowerShell 自动化脚本的语法错误和死循环问题，建立独立的日志分支架构。

### 📋 变更摘要

#### 脚本错误修复
- **语法错误**: 修复 `scripts/log_status.ps1` 中的 PowerShell 语法错误
  - 删除多余的 `+` 符号 (lines 68, 80)
  - 修复 `||` 运算符为 PowerShell 兼容的 `$LASTEXITCODE` 检查
- **退出码修复**: 优化 `scripts/smoke_test.ps1` 的退出码处理
  - 添加 `$script:TestSuccess` 变量跟踪测试状态
  - 确保成功时返回 `exit 0`，失败时返回 `exit 1`

#### 分支架构重构
- **独立日志分支**: 创建 `status/logs` 分支专门用于自动化日志
- **文件分离**:
  - `docs/status/automation_logs.md` - 仅存在于 `status/logs` 分支
  - `docs/status/status.md` - 存在于所有分支，用于人工状态记录
- **避免死循环**: 自动化脚本不再修改主开发分支的文件

#### 推送优化
- **超时处理**: 添加 30 秒推送超时限制
- **错误处理**: 增强 Git 操作的错误检测和恢复机制
- **远程同步**: 优化多远程仓库（GitHub + Gitee）的推送策略

### 🔧 技术细节

#### PowerShell 语法修复
```powershell
# 修复前 (错误语法)
+ $existsRemote = git ls-remote --heads origin $statusBranch | Select-String $statusBranch -Quiet
+ git commit -m $commitMsg || Write-Output "No changes to commit"

# 修复后 (正确语法)
$existsRemote = git ls-remote --heads origin $statusBranch | Select-String $statusBranch -Quiet
git commit -m $commitMsg
if ($LASTEXITCODE -ne 0) {
    Write-Output "No changes to commit on $statusBranch"
}
```

#### 烟雾测试退出码修复
```powershell
# 添加测试状态跟踪
$script:TestSuccess = $true

# 在测试失败时设置状态
if ($response.StatusCode -ne 200) {
    $script:TestSuccess = $false
}

# 正确的退出码处理
if ($script:TestSuccess) {
    exit 0  # 成功
} else {
    exit 1  # 失败
}
```

#### 分支架构设计
```
main / dev (主开发分支)
├── docs/status/status.md (人工状态记录)
└── (不包含 automation_logs.md)

status/logs (独立日志分支)
├── docs/status/status.md (从主分支同步)
├── docs/status/automation_logs.md (自动化日志)
└── scripts/ (脚本修复版本)
```

### 🔄 自动化流程修复

#### 发布脚本 (`scripts/release_to_main.ps1`)
1. ✅ 在 dev 分支运行烟雾测试
2. ✅ 合并 dev → main (无冲突)
3. ✅ 推送到远程仓库
4. ✅ 记录合并日志到独立分支
5. ✅ 在 main 分支运行最终验证
6. ✅ 记录发布完成日志

#### 日志脚本 (`scripts/log_status.ps1`)
1. ✅ 切换到独立的 `status/logs` 分支
2. ✅ 在独立分支添加自动化日志条目
3. ✅ 提交并推送日志更新
4. ✅ 返回原分支，不影响工作状态

### ✅ 验证结果

#### 脚本功能验证
- ✅ PowerShell 语法错误全部修复
- ✅ 烟雾测试正确返回退出码 (0=成功, 1=失败)
- ✅ 发布自动化流程完整运行无错误
- ✅ 日志记录到独立分支，避免死循环

#### 分支架构验证
- ✅ `automation_logs.md` 仅存在于 `status/logs` 分支
- ✅ 主开发分支 (main/dev) 不包含自动化日志文件
- ✅ 分支切换和合并不产生意外的文件变更

#### 推送性能验证
- ✅ 添加 30 秒超时限制，避免无限等待
- ✅ GitHub 和 Gitee 双远程推送策略优化
- ✅ 错误恢复机制工作正常
- ✅ API 端点响应正常
- ✅ 烟雾测试通过

#### 性能验证
- ✅ 应用启动时间 < 5 秒
- ✅ 数据库查询响应正常
- ✅ 无内存泄漏或异常

#### 兼容性验证
- ✅ Python 3.11 兼容
- ✅ Pydantic v2 完全兼容
- ✅ SQLAlchemy 2.x 语法正确
- ✅ Docker 容器环境稳定

### 🚀 后续规划

#### 短期目标 (1-2 周)
- 实现具体业务 API 端点逻辑
- 集成微信支付和支付宝支付
- 添加基础的权限和认证系统
- 实现商品图片上传和管理

#### 中期目标 (1 个月)
- 前端框架集成 (Vue.js/React)
- 完善订单流程和库存管理
- 实现优惠券和促销系统
- 添加数据分析和报表功能

#### 长期目标 (3 个月)
- 多租户架构支持
- 高并发性能优化
- 微服务架构迁移准备
- 生产环境部署和监控

### 🔄 回滚计划

如需回滚到 v1.0.0:
1. 恢复数据库到基础的 3 表结构 (users, products, certificates)
2. 回滚 Pydantic v1 兼容性代码
3. 使用历史备份的迁移文件
4. 更新 OpenAPI 规范到 v1.0.0

### 📊 影响评估

#### 正面影响
- 🎯 建立了完整的电商业务模型基础
- 🛡️ 消除了技术债务和兼容性问题  
- 📈 为快速业务开发奠定了稳固基础
- 📚 建立了完善的文档体系

#### 风险控制
- 🔍 完整的迁移测试确保数据安全
- 🏗️ 渐进式架构变更减少风险
- 📋 详细的文档确保团队协作顺畅
- 🧪 烟雾测试保证基础功能正常

---

## 版本历史

- **v1.1.0** (2025-09-08): 电商核心架构稳定化
- **v1.0.0** (2025-09-07): 基础项目脚手架建立
