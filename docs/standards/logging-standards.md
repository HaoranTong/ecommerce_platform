<!--version info: v1.0.0, created: 2025-09-23, level: L2, dependencies: naming-conventions-standards.md,../../PROJECT-FOUNDATION.md-->

# 日志管理标准 (Logging Standards)

## 概述
本文档定义logs/目录的日志文件管理规范，包括日志分类、命名标准、文件管理、监控机制等，属于L2领域标准。

## 依赖标准
本标准依赖以下L1核心标准：
- **[项目基础定义](../../PROJECT-FOUNDATION.md)** - 定义logs/目录结构规范
- **[命名规范](./naming-conventions-standards.md)** - 日志文件命名规则

## 具体标准
⬆️ **目录结构**: 参见 [PROJECT-FOUNDATION.md](../../PROJECT-FOUNDATION.md#根目录结构标准) - logs/目录权威定义

## L2标准动态管理义务

### 静态内容确认 (基于L1权威定义)
✅ **logs/目录基本职责已定义**: 参考 [PROJECT-FOUNDATION.md](../../PROJECT-FOUNDATION.md)
- 核心职责: 应用运行时日志文件存储
- 允许内容: 日志文件、错误报告、监控数据
- 禁止内容: 源代码、配置文件、用户数据

### 动态内容管理规范

#### 日志文件分类标准
**系统日志类型** (随应用发展动态增加):
1. **应用日志**: `app_YYYY-MM-DD.log` - 应用运行日志
2. **错误日志**: `error_YYYY-MM-DD.log` - 异常和错误记录
3. **安全日志**: `security_events_YYYY-MM-DD.log` - 安全相关事件
4. **性能日志**: `performance_YYYY-MM-DD.log` - 性能监控数据
5. **业务日志**: `{module}_YYYY-MM-DD.log` - 业务模块专项日志
6. **测试日志**: `test_{type}_YYYYMMDDHHMMSS.log` - 测试执行日志

#### 日志文件命名规范
**标准命名格式**:
```
{category}_{detail}_YYYY-MM-DD[.sequence].log
```

**命名规则**:
- `category`: 日志类型 (app, error, security, performance, {module_name}, test)
- `detail`: 详细分类 (可选)
- 日期格式: YYYY-MM-DD 或 YYYYMMDDHHMMSS (测试日志)
- 序列号: 当单日文件过大时使用 .1, .2, .3...

#### 日志轮转管理
**文件大小限制**:
- 单个日志文件最大: 100MB
- 达到限制自动轮转: filename.log → filename.log.1
- 保留历史版本: 最多7个轮转文件

**时间轮转策略**:
- 日志文件按日期轮转
- 自动归档超过30天的日志文件
- 压缩存储超过7天的日志文件

#### 日志内容标准
**日志格式要求**:
```
YYYY-MM-DD HH:MM:SS.mmm [LEVEL] [MODULE] MESSAGE
```

**日志级别标准**:
- `DEBUG`: 调试信息 (开发环境)
- `INFO`: 一般信息记录
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

### 新增日志类型管理流程
1. **需求评估**: 确认新日志类型的必要性和分类
2. **命名标准**: 按照命名规范确定文件名格式
3. **配置更新**: 更新日志配置和轮转策略
4. **监控集成**: 纳入日志监控和告警体系
5. **文档更新**: 及时更新本标准文档

### 日志监控标准
**关键监控指标**:
- 日志文件大小增长速度
- 错误日志频率和类型
- 磁盘空间使用情况
- 日志轮转执行状态

**告警阈值设置**:
- 错误日志每小时超过100条
- 单个日志文件超过80MB
- logs目录占用超过1GB
- 日志轮转失败

## 职责边界声明

**本文档职责**: logs/目录的日志文件管理、分类标准、监控规范
- **专门负责**: 日志文件命名、分类管理、轮转策略、监控告警
- **动态管理**: 随应用发展新增的日志类型规范化管理
- **不包含职责**: 日志内容生成逻辑、应用日志配置、监控系统实现

**边界划分**:
- ✅ 日志文件的存储标准和命名规范
- ✅ 日志轮转和归档策略
- ❌ 应用代码中的日志记录逻辑 (由code-standards.md管理)
- ❌ 监控系统的部署和配置 (由operations/目录文档管理)

## 相关文档
- [项目基础定义](../../PROJECT-FOUNDATION.md) - logs/目录权威定义
- [命名规范](./naming-conventions-standards.md) - 日志文件命名规则
- [运维文档](../operations/monitoring.md) - 日志监控实施指南

---
**注**: 本标准专注于logs/目录的文件管理规范，应用层面的日志记录标准请参考code-standards.md相关章节。