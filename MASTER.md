# AI开发控制文档 (MASTER)

## 🔐 用户指令格式

### 标准任务启动格式：
> **"按MASTER文档执行，完成AI工作流程规定的所有步骤：[具体任务]"**

## 🚀 AI工作流程

### 步骤1: 读取当前工作状态
📖 读取 `docs/status/current-work-status.md` 了解当前工作状态

### 步骤2: 分析用户指令  
🔍 分析任务：What(做什么)/Why(为什么)/Where(在哪里)/How(怎么做)

### 步骤3: 确定相关检查点
📋 根据任务内容匹配本文档"详细检查点列表"中的相关检查点

### 步骤4: 创建TODO清单
📝 每个TODO项必须包含 [CHECK:XXX-XXX] 检查点标记

### 步骤5: 等待用户确认TODO清单
⏸️ 用户确认TODO清单后开始执行

### 步骤6: 执行工作
🔧 按TODO清单执行，遇到问题时先查阅相关文档

## ⚠️ 异常处理机制

### 检查点执行失败处理
当任何检查点执行失败时，必须执行以下流程：

1. **立即暂停执行**
   - 停止当前TODO项执行
   - 不继续后续步骤

2. **失败信息输出**
   ```
   🚨 检查点执行失败：
   - 失败检查点: [CHECK:XXX-XXX] 
   - 失败原因: [具体错误描述]
   - 影响范围: [可能影响的功能/模块]
   - 建议措施: [初步建议的解决方案]
   
   ⏸️ 流程已暂停，等待人工干预...
   ```

3. **等待人工干预**
   - 用户输入"继续执行" → 跳过当前检查点，继续后续步骤
   - 用户输入"重新执行" → 重新执行当前检查点
   - 用户输入"修改方案" → 返回步骤4重新确定检查点清单
   - 用户输入"终止任务" → 完全停止当前任务

### 常见失败场景处理
- **文档不存在**: 提示缺失文档路径，建议创建或修正引用
- **卡片内容缺失**: 提示检查点卡片不完整，建议使用通用验证规则
- **权限不足**: 提示文件访问权限问题，建议检查文件状态
- **依赖缺失**: 提示缺少必要的依赖文件或工具，建议安装或配置

## 🎯 核心工作原则 (AI最容易忽略的3条)

1. **文档驱动开发** → 修改代码前必须先更新相关文档
2. **检查点强制执行** → 每个TODO项必须包含对应的检查点标记
3. **状态同步** → 完成任务后必须更新current-work-status.md

## 📋 详细检查点列表 (按场景分类)

### 🚀 启动类
- **接收任务时** → [CHECK:AI-START] ⚠️ [必读卡片](tools/checkpoint-cards.md#ai-start) 确认理解任务并制定计划

### 📋 需求分析类  
- **项目启动** → [CHECK:REQ-001] ⚠️ [必读卡片](tools/checkpoint-cards.md#req-001)
- **功能规划** → [CHECK:REQ-002] ⚠️ [必读卡片](tools/checkpoint-cards.md#req-002)
- **架构设计前** → [CHECK:REQ-003] ⚠️ [必读卡片](tools/checkpoint-cards.md#req-003)

### 🏗️ 架构设计类
- **系统架构** → [CHECK:ARCH-001] ⚠️ [必读卡片](tools/checkpoint-cards.md#arch-001)
- **模块架构** → [CHECK:ARCH-002] ⚠️ [必读卡片](tools/checkpoint-cards.md#arch-002)
- **数据架构** → [CHECK:ARCH-003] ⚠️ [必读卡片](tools/checkpoint-cards.md#arch-003) + [数据库标准](docs/standards/database-standards.md)
- **架构调整** → [CHECK:ARCH-004] ⚠️ [必读卡片](tools/checkpoint-cards.md#arch-004)

### 💻 开发实施类
- **编码准备** → [CHECK:DEV-001] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-001)
- **环境配置** → [CHECK:DEV-002] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-002)
- **数据模型** → [CHECK:DEV-003] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-003) + [数据库标准](docs/standards/database-standards.md)
- **API路由** → [CHECK:DEV-004] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-004) + [API标准](docs/standards/api-standards.md)
- **业务逻辑** → [CHECK:DEV-005] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-005)
- **安全功能** → [CHECK:DEV-006] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-006)
- **异常处理** → [CHECK:DEV-007] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-007)
- **代码质量** → [CHECK:DEV-008] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-008) + [命名标准](docs/standards/naming-conventions-standards.md)
- **强制检查** → [CHECK:DEV-009] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-009)
- **代码审查** → [CHECK:DEV-010] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-010)
- **数据迁移** → [CHECK:DEV-011] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-011) + [数据库标准](docs/standards/database-standards.md)
- **配置管理** → [CHECK:DEV-012] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-012)
- **依赖管理** → [CHECK:DEV-013] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-013)
- **性能基准** → [CHECK:DEV-014] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-014)

### 🧪 测试验证类
- **测试环境** → [CHECK:TEST-001] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-001)
- **单元测试** → [CHECK:TEST-002] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-002)
- **Mock统一** → [CHECK:TEST-003] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-003)
- **集成测试** → [CHECK:TEST-004] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-004)
- **接口测试** → [CHECK:TEST-005] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-005)
- **性能测试** → [CHECK:TEST-006] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-006)
- **安全测试** → [CHECK:TEST-007] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-007)
- **测试完成** → [CHECK:TEST-008] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-008)

### 📊 状态管理类
- **状态读取** → [CHECK:STATUS-001] ⚠️ [必读卡片](tools/checkpoint-cards.md#status-001)
- **状态更新** → [CHECK:STATUS-002] ⚠️ [必读卡片](tools/checkpoint-cards.md#status-002)
- **工作归档** → [CHECK:STATUS-003] ⚠️ [必读卡片](tools/checkpoint-cards.md#status-003)
- **状态恢复** → [CHECK:STATUS-004] ⚠️ [必读卡片](tools/checkpoint-cards.md#status-004)

### 📖 文档同步类
- **代码文档** → [CHECK:DOC-001] ⚠️ [必读卡片](tools/checkpoint-cards.md#doc-001)
- **API文档** → [CHECK:DOC-002] ⚠️ [必读卡片](tools/checkpoint-cards.md#doc-002)
- **架构文档** → [CHECK:DOC-003] ⚠️ [必读卡片](tools/checkpoint-cards.md#doc-003)
- **部署文档** → [CHECK:DOC-004] ⚠️ [必读卡片](tools/checkpoint-cards.md#doc-004)
- **目录同步** → [CHECK:DOC-005] ⚠️ [必读卡片](tools/checkpoint-cards.md#doc-005)
- **工具文档** → [CHECK:DOC-006] ⚠️ [必读卡片](tools/checkpoint-cards.md#doc-006)
- **强制文档阅读** → [CHECK:DOC-007] ⚠️ [必读卡片](tools/checkpoint-cards.md#doc-007)

### 🚨 应急处理类
- **文件重建** → [CHECK:EMERGENCY-001] ⚠️ [必读卡片](tools/checkpoint-cards.md#emergency-001)

## 📚 重要文档快速索引

### 🏗️ 基础架构文档
- **PROJECT-FOUNDATION.md** - 项目最高权威设定
- **docs/README.md** - 技术文档导航中心  
- **MASTER.md** - AI控制文档(本文档)

### 📋 需求与架构文档
- **docs/requirements/functional.md** - 功能需求规范
- **docs/requirements/business.md** - 业务需求规范
- **docs/architecture/overview.md** - 技术架构总览
- **docs/architecture/module-architecture.md** - 模块架构设计
- **docs/architecture/data-models.md** - 数据模型设计
- **docs/architecture/security-architecture.md** - 安全架构设计原则

### 🔧 开发规范文档  
- **docs/standards/README.md** - 开发标准导航 ⭐
- **docs/standards/software-development-lifecycle-standards.md** - 软件开发生命周期标准
- **docs/standards/requirements-standards.md** - 需求管理标准
- **docs/standards/architecture-standards.md** - 架构设计标准
- **docs/standards/naming-conventions-standards.md** - 命名规范
- **docs/standards/api-standards.md** - API设计规范
- **docs/standards/database-standards.md** - 数据库设计规范
- **docs/standards/code-standards.md** - 代码组织规范
- **docs/standards/testing-standards.md** - 测试规范
- **docs/standards/document-management-standards.md** - 文档结构规范

### 📊 状态管理文档 (核心4个)
- **docs/status/current-work-status.md** - 当前工作状态 ⭐
- **docs/status/module-status.md** - 模块状态跟踪
- **docs/status/issues-tracking.md** - 问题跟踪记录
- **docs/status/README.md** - 状态文档说明

## ⚡ 常用工具脚本
- **测试环境管理**: `tools/setup_test_env.ps1 -TestMode <lite|full>`
- **测试环境检查**: `tools/check_test_env.ps1 -TestMode <lite|full>`
- **代码规范检查**: `tools/check_code_standards.ps1` 
- **文档同步**: `tools/sync_readme.ps1`
- **测试模板生成**: `python tools/generate_test_template.py [module]`
- **检查点验证**: `tools/ai_checkpoint.ps1 -CardType [编号]`

---
## 🎯 AI使用提醒

**这个文档是为AI优化的工作指南，重点关注**：
- ✅ 分析任务并匹配相关检查点
- ✅ 创建的TODO必须包含检查点标记
- ✅ 遇到问题先查相关文档  
- ✅ 完成工作后及时更新状态

**用户监督要点**：
- 🔍 验证AI的TODO是否包含检查点
- 🔍 确认AI遇到问题时先查询了文档
- ⚠️ 发现违规时可随时输入"STOP"