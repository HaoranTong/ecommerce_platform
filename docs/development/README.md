# 开发阶段文档

> 🔧 **开发实施专用文档集** - 涵盖开发环境配置、测试环境设置、工具使用、问题解决的完整开发支撑体系

## 📋 文档导航

### 🛠️ 环境配置
- **[dev-env-setup.md](dev-env-setup.md)** - 开发环境完整配置指南
  - Python虚拟环境设置
  - IDE和工具配置
  - 开发依赖安装
  - Docker开发环境配置

### 🧪 测试环境
- **[test-env-setup.md](test-env-setup.md)** - 测试环境配置指南
  - 测试环境变量配置
  - Docker测试环境设置
  - 测试工具安装和使用
  - 测试数据库配置

- **[test-factory-guide.md](test-factory-guide.md)** - 测试数据工厂详细使用手册
  - 工厂模式设计
  - 数据生成策略
  - 测试场景构建
  - 性能优化指南

- **[test-dir-management.md](test-dir-management.md)** - 测试目录管理策略
  - 测试文件组织
  - 测试数据管理
  - 生成文件处理
  - 清理策略

### 🚨 问题解决
- **[dev-troubleshooting.md](dev-troubleshooting.md)** - 开发测试过程问题解决方案
  - 环境配置问题
  - 依赖管理问题
  - 测试执行问题
  - 性能优化方案
  - 最佳实践总结

## 🎯 使用场景

### 新手入门
1. 首先阅读 `dev-env-setup.md` 配置开发环境
2. 参考 `test-env-setup.md` 设置测试环境
3. 遇到问题查看 `dev-troubleshooting.md`

### 日常开发
- 开发环境问题 → `dev-env-setup.md`
- 测试环境配置 → `test-env-setup.md`
- 测试数据准备 → `test-factory-guide.md`
- 测试目录管理 → `test-dir-management.md`
- 问题排查 → `dev-troubleshooting.md`

### 团队协作
- 环境标准化 → `dev-env-setup.md` + `test-env-setup.md`
- 测试规范化 → `test-factory-guide.md` + `test-dir-management.md`
- 问题知识库 → `dev-troubleshooting.md`

##  文档职责边界

### ✅ development目录职责
- **开发环境配置**: 本地开发环境的设置和管理
- **测试环境配置**: 开发阶段的测试环境配置和使用
- **开发过程问题解决**: 编码、调试、测试过程中的问题解决方案和经验总结
- **测试工具使用**: 开发阶段相关的测试工具配置和数据管理

### ❌ 不包含的职责
- **生产运维配置**: 属于 `../operations/` 目录职责
- **架构设计决策**: 属于 `../architecture/` 目录职责
- **详细设计文档**: 属于 `../design/` 目录职责
- **开发规范标准**: 属于 `../standards/` 目录职责
- **工具脚本故障排查**: 属于 `../tools/troubleshooting.md` 职责

---

## 🔗 相关资源

### 工具脚本
- **工具集导航**: `../tools/README.md`
- **环境管理**: `../tools/setup_test_env.ps1`, `../tools/check_test_env.ps1`
- **测试执行**: `../tools/run_module_tests.ps1`, `../tools/smoke_test.ps1`

### 标准规范
- **开发规范**: `../standards/code-standards.md`
- **测试规范**: `../standards/testing-standards.md`
- **工具规范**: `../standards/scripts-standards.md`

### 架构设计
- **技术架构**: `../architecture/overview.md`
- **模块架构**: `../architecture/module-architecture.md`
- **数据架构**: `../architecture/data-models.md`

---

> 💡 **提示**: 本目录专注于开发实施阶段的实用指导和问题解决，与生产运维(operations)、架构设计(architecture)、详细设计(design)、工具故障排查(tools)形成清晰的职责边界