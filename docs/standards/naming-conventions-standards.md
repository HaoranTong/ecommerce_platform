<!--version info: v2.0.0, created: 2025-09-23, level: L1, dependencies: project-structure-standards.md-->

# 命名规范总纲 (Naming Conventions Master Guide)
版本信息：v2.2.0 (DEV-009强制重建版本)
更新日期：2025-09-23  
维护人：系统架构师
权威级别：L1核心标准
依赖关系：project-structure-standards.md
被依赖：所有L2领域标准
关联决策：ADR-002 标准文档架构重构
变更说明：按DEV-009协议强制重建，彻底解决重复内容问题，统一文档格式
-->

⬆️ **目录结构标准**: 参见 [project-structure-standards.md](project-structure-standards.md)  
⬆️ **模块命名映射**: 参见 [project-structure-standards.md](project-structure-standards.md#业务模块标准结构)

---

## 标准概述

本标准规范电商平台的统一命名规则，确保在文档、数据库、API、代码中的命名一致性。

### 标准权威性声明
- **双层命名体系**: 本标准为唯一权威定义
- **转换规则**: 本标准为唯一权威定义
- **目录结构命名**: 遵循 `project-structure-standards.md` 权威定义

---

## 双层命名体系

### 业务层级 (kebab-case)
- 文档路径: /shopping-cart/overview.md
- API路径: /api/v1/shopping-cart/items  
- Git分支: feature/shopping-cart-optimization

### 技术层级 (snake_case)
- 数据库表: shopping_cart_items
- Python模块: shopping_cart_service.py
- 函数名: get_shopping_cart_items()

### 标准文档层级 (kebab-case + standards后缀)
- **强制规则**: 所有标准文档文件名必须包含"standards"关键字
- L0导航层: standards-master-index.md
- L1核心层: project-structure-standards.md, naming-conventions-standards.md
- L2领域层: api-standards.md, database-standards.md, code-standards.md 等
- **验证机制**: 自动化脚本通过"standards"关键字识别标准文档

---

## 相关标准文档
- [项目结构标准](project-structure-standards.md) - 目录和模块结构定义
- [数据库设计规范](database-standards.md) - 数据库命名细则
- [API设计标准](api-standards.md) - API接口命名细则
- [代码标准规范](code-standards.md) - 代码命名细则

### 标准导航
返回 [标准文档主索引](standards-master-index.md)

---
**文档结束** | 如需更新此标准，请遵循 [标准变更流程](workflow-standards.md#标准变更管理)