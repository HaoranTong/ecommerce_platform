⚠️ 文档修改保护机制
任何对本文档的修改都必须：
1. 先提出修改需求和理由
2. 与用户讨论确认方案  
3. 获得明确同意后才能执行
4. 修改后立即报告变更内容

# AI开发控制文档 (MASTER)

此文档专为AI开发人员设计，用于确保开发过程严格遵循规范。

## 🤖 AI强制工作流程启动检查

### 每次对话开始必须执行以下自检：
□ 已完整读取 MASTER.md 全文
□ 已识别当前任务类型和触发的检查点
□ 已确认需要执行的检查卡片类型  
□ 已承诺在制定TODO时自动嵌入对应检查点

### TODO制定强制规则：
制定任何TODO任务时必须按以下格式嵌入检查点：
- 开发任务后 → 添加 [CHECK:DEV-xxx]
- 测试任务后 → 添加 [CHECK:TEST-xxx]
- 文档任务后 → 添加 [CHECK:DOC-xxx] 
- 模型操作后 → 添加 [CHECK:MODEL-xxx]

### 违规后果：
未执行启动检查或TODO中缺少检查点 → 立即停止工作，重新开始

## 🚨 核心强制规则 (完整覆盖版)

1. **文档驱动开发** - 必须先有完整文档才能开始编码实现
2. **数据模型一致性** - 模型定义与使用必须类型匹配，禁止类型不一致
3. **架构规范遵循** - 必须遵循系统架构和模块设计规范
4. **接口标准统一** - API设计必须符合RESTful和响应格式标准  
5. **测试完整覆盖** - 功能实现必须有对应的完整测试验证
6. **安全控制必备** - 涉及数据和权限的操作必须有安全验证
7. **错误处理完善** - 所有业务逻辑必须有完整的异常处理机制
8. **文档同步强制** - 创建/重命名/删除文档或代码时必须同步更新同级README
9. **工具文档完整** - 新增工具必须同步更新使用说明和相关文档
10. **代码规范完备** - 文件头部、函数说明、代码注释必须符合标准格式

## 📋 检查点路由表 (完整版-24卡片)

### 需求分析类 (REQ)
- **项目启动** → [CHECK:REQ-001] 业务需求理解验证
- **功能规划** → [CHECK:REQ-002] 功能需求分析验证
- **架构设计前** → [CHECK:REQ-003] 非功能需求确认

### 架构设计类 (ARCH)  
- **系统架构设计** → [CHECK:ARCH-001] 系统架构设计验证
- **模块架构规划** → [CHECK:ARCH-002] 模块架构设计验证
- **数据架构设计** → [CHECK:ARCH-003] 数据架构设计验证

### 开发实施类 (DEV)
- **编码前准备** → [CHECK:DEV-001] 模块文档完整性验证
- **环境配置** → [CHECK:DEV-002] 环境与工具准备验证
- **操作models.py** → [CHECK:DEV-003] 数据模型实现验证
- **创建*_routes.py** → [CHECK:DEV-004] API路由实现验证
- **实现service.py** → [CHECK:DEV-005] 业务逻辑实现验证
- **安全功能开发** → [CHECK:DEV-006] 安全控制实现验证
- **异常处理实现** → [CHECK:DEV-007] 错误处理实现验证
- **代码提交前** → [CHECK:DEV-008] 代码质量验证

### 测试验证类 (TEST)
- **开始测试会话** → [CHECK:TEST-001] 测试环境配置验证
- **编写单元测试** → [CHECK:TEST-002] 单元测试验证
- **跨模块测试** → [CHECK:TEST-003] 集成测试验证
- **接口测试** → [CHECK:TEST-004] API测试验证
- **性能压力测试** → [CHECK:TEST-005] 性能测试验证
- **安全测试** → [CHECK:TEST-006] 安全测试验证

### 文档同步类 (DOC)
- **代码完成后** → [CHECK:DOC-001] 代码文档同步验证
- **API变更后** → [CHECK:DOC-002] API文档更新验证
- **架构调整后** → [CHECK:DOC-003] 架构文档维护验证
- **部署变更后** → [CHECK:DOC-004] 部署文档完善验证
- **文件操作后** → [CHECK:DOC-005] 文档目录同步验证
- **工具创建后** → [CHECK:DOC-006] 工具文档完整性验证

## 🎯 检查卡片详情
详细验证步骤 → `docs/standards/checkpoint-cards.md`
辅助检查脚本 → `scripts/ai-checkpoint.ps1 -CardType [卡片编号]`

## 📁 标准规范文档引用 (完整版)

### 需求与架构
- docs/requirements/functional.md - 功能需求规范
- docs/requirements/business.md - 业务需求规范  
- docs/architecture/overview.md - 技术架构总览
- docs/architecture/module-architecture.md - 模块架构设计
- docs/architecture/data-models.md - 数据模型设计
- docs/architecture/security.md - 安全架构设计

### 开发流程与规范
- docs/development/README.md - 开发流程指南
- docs/development/testing-setup.md - 测试环境配置
- docs/standards/naming-conventions.md - 命名规范
- docs/standards/api-standards.md - API设计规范
- docs/standards/database-standards.md - 数据库设计规范
- docs/standards/code-standards.md - 代码组织规范
- docs/standards/testing-standards.md - 测试规范
- docs/standards/document-standards.md - 文档结构规范
- docs/standards/workflow-standards.md - 工作流程规范

## ⚡ 快速执行脚本
- 启动检查: `scripts/check_docs.ps1 + scripts/check_naming_compliance.ps1`
- 测试环境: `scripts/check_test_env.ps1` (强制执行)
- 卡片验证: `scripts/ai-checkpoint.ps1 -CardType [编号]`
- 文档同步: `scripts/sync_readme.ps1` (文件操作后强制执行)
- 代码规范: `scripts/check_code_standards.ps1` (提交前强制执行)



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
