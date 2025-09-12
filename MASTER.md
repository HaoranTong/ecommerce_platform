⚠️ 文档修改保护机制
任何对本文档的修改都必须：
1. 先提出修改需求和理由
2. 与用户讨论确认方案  
3. 获得明确同意后才能执行
4. 修改后立即报告变更内容

# AI开发控制文档 (MASTER)

此文档专为AI开发人员设计，用于确保开发过程严格遵循规范。

## 🚨 前10条强制规则 (90%违规预防)

1. **禁止不读文档就操作** - 任何操作前必须read_file相关规范
2. **禁止随意命名** - 命名前必须检查docs/standards/naming-conventions.md
3. **禁止重复创建文档** - 创建前必须grep_search 关键词 docs/
4. **禁止不一致的API设计** - 必须检查docs/standards/api-standards.md
5. **禁止代码与文档不同步** - 修改代码必须同时更新文档
6. **禁止违反文档结构规范** - 必须检查docs/standards/document-standards.md
7. **禁止跳过检查点** - 触发条件时必须执行验证流程
8. **禁止不确认数据库字段** - 必须检查docs/standards/database-standards.md
9. **禁止不了解现有架构** - 必须读取模块overview.md全文
10. **禁止不记录检查过程** - 必须记录验证结果和引用条款
11. **禁止不使用自动检查脚本** - 必须执行scripts目录中的检查脚本

## 📋 检查点触发条件

### 主检查点 (必触发)
- 接收新任务 → 任务相关文档阅读检查点 + 执行 .\scripts\check_docs.ps1
- 开始编码 → 设计规范确认检查点 + 执行 .\scripts\check_naming_compliance.ps1
- 提交代码 → 代码文档同步检查点 + 执行 .\scripts\check_naming_compliance.ps1

### 辅助检查点 (条件触发)
- create_file docs/* → 文档结构规范检查点 + 执行 .\scripts\check_docs.ps1
- create_file *.py → 代码开发强制检查点 + 执行 .\scripts\check_naming_compliance.ps1 -CheckType code
- create_file *_routes.py → API设计标准检查点 + 执行 .\scripts\check_naming_compliance.ps1 -CheckType api
- create_file test_*.py → 测试规范检查点
- 操作models.py → 数据库设计规范检查点 + 执行 .\scripts\check_naming_compliance.ps1 -CheckType database
- 任何命名操作 → 命名规范检查点 + 执行 .\scripts\check_naming_compliance.ps1
- 创建类/函数/变量 → 代码开发检查清单 + 执行 .\scripts\check_naming_compliance.ps1 -CheckType code
- 设计数据库表/字段 → 数据库命名检查点 + 执行 .\scripts\check_naming_compliance.ps1 -CheckType database

## 🔍 检查点执行格式
🔍 检查点触发：[操作类型]
📋 必须验证：read_file [文档路径] [起始行] [结束行]
✅ 验证确认：[具体规则内容]
🚫 执行操作：[具体操作描述]

## 📁 标准规范文档引用
- docs/standards/naming-conventions.md - 所有命名规则
- docs/standards/api-standards.md - API设计规范  
- docs/standards/document-standards.md - 文档结构规范
- docs/standards/database-standards.md - 数据库设计规范
- docs/standards/code-standards.md - 代码组织规范
- docs/standards/testing-standards.md - 测试规范
- docs/standards/workflow-standards.md - 工作流程规范
- docs/standards/code-development-checklist.md - 代码开发检查清单

## ⚡ 条件分支执行
IF 创建新模块 THEN 检查 docs/templates/module-template.md
IF create_file *.py THEN 执行 docs/standards/code-development-checklist.md + .\scripts\check_naming_compliance.ps1 -CheckType code
IF create_file *_routes.py THEN 检查 docs/standards/api-standards.md + .\scripts\check_naming_compliance.ps1 -CheckType api
IF 操作models.py THEN 确认 docs/standards/database-standards.md + .\scripts\check_naming_compliance.ps1 -CheckType database
IF create_file test_*.py THEN 检查 docs/standards/testing-standards.md
IF 创建文档 THEN 检查 docs/standards/document-standards.md + .\scripts\check_docs.ps1
IF 命名实体 THEN 确认 docs/standards/naming-conventions.md + .\scripts\check_naming_compliance.ps1
IF 编写测试 THEN 检查 docs/standards/testing-standards.md
IF 修改流程 THEN 检查 docs/standards/workflow-standards.md
IF 开始工作会话 THEN 执行 .\scripts\check_naming_compliance.ps1 + .\scripts\check_docs.ps1

## 📄 README同步触发
IF create_file app/modules/* THEN 更新对应模块README.md
IF 修改main.py THEN 检查根目录README.md快速开始部分
IF create_file docs/* THEN 更新对应目录README.md
IF 修改启动脚本 THEN 更新根目录README.md
IF 添加新API THEN 更新相关模块README.md
IF 创建新目录 THEN 创建该目录README.md并更新父目录README.md
IF 删除目录 THEN 更新父目录README.md移除该目录说明
IF 重命名目录 THEN 更新所有相关README.md中的目录引用

## 🚫 违规后果
1. 立即停止当前操作
2. 报告违规的具体规则
3. 执行对应的检查点流程
4. 重新开始操作

## 📝 检查点执行记录
每次执行检查点后必须记录：
- 触发的检查点类型
- 引用的文档和具体条款
- 验证结果和确认内容
- 执行的具体操作

## 📚 文档编制原则

### 本文档编制原则
1. 长度控制：严格控制在100行以内
2. AI优化：专为AI设计，命令式表述
3. 引用外置：具体规范外置到standards目录
4. 强制检查：建立强制检查点机制
5. 条件分支：使用IF-THEN格式

### 文档修改约束
- 任何修改都必须先讨论确认
- 禁止增加修饰性内容
- 禁止内嵌具体规范
- 修改后必须验证符合编制原则
- 必须保持简洁性和可执行性

### 避免臃肿机制
- 新增内容前评估是否可外置
- 定期检查长度，超100行必须精简
- 优先更新外部规范文档
- 保持核心控制逻辑纯净性
