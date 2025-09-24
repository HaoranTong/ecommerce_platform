# AI开发控制文档 (MASTER)

🤖 **AI工作启动指南**：本文档帮助AI提供高质量、规范化的开发服务

✅ **成功工作模式**：遵循启动流程 → 获得完整上下文 → 提供精准解## � 详细检查点列表 (按场景分类)

⚠️ **重要提醒**: 本文档中的检查点描述仅为概述，AI必须点击卡片链接查看详细要求并严格按照卡片内容执行！

### 🚀 启动类  
⚠️ **用户STOP权限**：发现AI未按流程工作时，可输入"STOP"重启流程

## 🔐 启动验证机制

### 用户标准指令格式：
> **"按MASTER文档执行，提供完整验证：[具体任务]"**

### AI必须回复的验证模板：
```
📋 AI工作启动确认：
【文档验证证明】
- MASTER.md：已读取[具体行数]行，包含[X]个检查点分类
- 卡片文档：已读取[具体卡片编号]的详细要求，共[X]行内容
- 核心规则验证：第[X]条-[具体规则内容]
- 检查点验证：[任务类型]对应[CHECK:XXX-XXX]检查点
- 状态文档：[从current-work-status.md获取的具体描述]

【任务分析】
- What: [具体要做什么]
- Why: [为什么要做]  
- Where: [涉及哪些文件/模块]
- When: [优先级/时间要求]
- Who: [影响哪些用户/角色]
- How: [大概实现思路]

【工作承诺】
- 文档驱动：遇到问题先查文档 ✓
- TODO清单：创建带检查点的任务列表 ✓
- 完成承诺：更新状态文档 ✓
```

**⚠️ 验证失败处理：如AI提供信息错误或缺失，用户立即输入"STOP"要求重新验证**

## 🚀 AI启动工作流程 (每次对话必须执行)

### 步骤1: 读取状态文档
📖 读取 `docs/status/current-work-status.md` 了解当前工作状态

### 步骤2: 分析用户指令  
🔍 用5W1H方式分析：What(做什么)/Why(为什么)/Where(在哪里)/When(什么时候)/Who(影响谁)/How(怎么做)

### 步骤3: 提供启动确认
✅ 使用验证模板回复（见上方"启动验证机制"）：
- 必须包含文档验证证明（行数、规则、检查点）
- 必须完成5W1H任务分析  
- 必须提供工作承诺

### 步骤4: 创建TODO清单
📝 每个TODO项必须包含 [CHECK:XXX-XXX] 检查点标记

### 步骤5: 开始执行工作
🔧 遇到问题时先查阅相关文档，修改前先更新文档

## 🎯 AI自检机制 (工作过程中持续执行)

### 对话开始时 - 问自己：
✅ 我读了status文档吗？  
✅ 我做了5W1H分析吗？  
✅ 我给了启动确认吗？  
✅ 我创建TODO清单了吗？

### 工作过程中 - 问自己：
✅ 我的每个TODO都有检查点吗？  
✅ 遇到问题我先查文档了吗？  
✅ 我遵循核心规则了吗？  

### 任务完成时 - 问自己：
✅ 我更新了status文档吗？  
✅ 我转移工作到历史档案了吗？  
✅ 我执行了完成闭环吗？

## 📋 快速检查点匹配指南

| 任务类型 | 常用检查点 | 什么时候用 |
|---------|-----------|----------|
| 修复Bug | DEV-005, DEV-010, TEST-002 | 修改业务逻辑+代码审查+测试验证 |
| 新增API | DEV-001, DEV-004, DEV-010, DOC-002 | 检查文档+创建路由+代码审查+更新API文档 |
| 数据模型 | DEV-001, DEV-003, DEV-011, TEST-002 | 检查设计+实现模型+数据迁移+测试 |
| 架构调整 | ARCH-001, DEV-012, DOC-003 | 架构设计+配置管理+文档更新 |
| 测试开发 | TEST-001, TEST-002, DEV-010 | 环境配置+单元测试+代码审查 |
| 文档更新 | DOC-001, DOC-005 | 同步文档+目录整理 |
| 环境部署 | DEV-002, DEV-012, DEV-013 | 环境配置+配置管理+依赖管理 |
| 性能优化 | DEV-010, DEV-014, TEST-006 | 代码审查+性能基准+性能测试 |

## � 核心工作规则 (必须遵守的10条)

1. **文档驱动开发** → 先完善文档，再编写代码
2. **数据模型一致性** → 确保类型定义和使用匹配  
3. **架构规范遵循** → 按照系统设计规范实现
4. **接口标准统一** → API设计符合RESTful规范
5. **测试完整覆盖** → 功能实现必须有测试验证
6. **安全控制必备** → 数据操作必须有权限验证
7. **错误处理完善** → 业务逻辑必须有异常处理
8. **文档同步强制** → 代码变更必须同步更新README
9. **工具文档完整** → 新工具必须有使用说明
10. **代码规范完备** → 文件头、注释符合标准格式

## � 详细检查点列表 (按场景分类)

### 🚀 启动类
- **接收任务时** → [CHECK:AI-START] 确认理解任务并制定计划

### 📋 需求分析类  
- **项目启动** → [CHECK:REQ-001] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#req-001)
- **功能规划** → [CHECK:REQ-002] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#req-002)
- **架构设计前** → [CHECK:REQ-003] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#req-003)

### 🏗️ 架构设计类
- **系统架构** → [CHECK:ARCH-001] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#arch-001)
- **模块架构** → [CHECK:ARCH-002] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#arch-002)
- **数据架构** → [CHECK:ARCH-003] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#arch-003)
- **架构调整** → [CHECK:ARCH-004] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#arch-004)

### 💻 开发实施类
- **编码准备** → [CHECK:DEV-001] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#dev-001)
- **环境配置** → [CHECK:DEV-002] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#dev-002)
- **数据模型** → [CHECK:DEV-003] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#dev-003)
- **API路由** → [CHECK:DEV-004] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#dev-004)
- **业务逻辑** → [CHECK:DEV-005] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#dev-005)
- **安全功能** → [CHECK:DEV-006] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#dev-006)
- **异常处理** → [CHECK:DEV-007] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#dev-007)
- **代码质量** → [CHECK:DEV-008] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#dev-008)
- **强制检查** → [CHECK:DEV-009] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#dev-009)
- **代码审查** → [CHECK:DEV-010] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#dev-010)
- **数据迁移** → [CHECK:DEV-011] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#dev-011)
- **配置管理** → [CHECK:DEV-012] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#dev-012)
- **依赖管理** → [CHECK:DEV-013] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#dev-013)
- **性能基准** → [CHECK:DEV-014] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#dev-014)

### 🧪 测试验证类
- **测试环境** → [CHECK:TEST-001] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#test-001)
- **单元测试** → [CHECK:TEST-002] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#test-002)
- **Mock统一** → [CHECK:TEST-003] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#test-003)
- **集成测试** → [CHECK:TEST-004] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#test-004)
- **接口测试** → [CHECK:TEST-005] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#test-005)
- **性能测试** → [CHECK:TEST-006] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#test-006)
- **安全测试** → [CHECK:TEST-007] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#test-007)
- **测试完成** → [CHECK:TEST-008] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#test-008)

### 📊 状态管理类
- **状态读取** → [CHECK:STATUS-001] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#status-001)
- **状态更新** → [CHECK:STATUS-002] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#status-002)
- **工作归档** → [CHECK:STATUS-003] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#status-003)
- **状态恢复** → [CHECK:STATUS-004] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#status-004)

### 📖 文档同步类
- **代码文档** → [CHECK:DOC-001] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#doc-001)
- **API文档** → [CHECK:DOC-002] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#doc-002)
- **架构文档** → [CHECK:DOC-003] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#doc-003)
- **部署文档** → [CHECK:DOC-004] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#doc-004)
- **目录同步** → [CHECK:DOC-005] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#doc-005)
- **工具文档** → [CHECK:DOC-006] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#doc-006)

### 🚨 应急处理类
- **文件重建** → [CHECK:EMERGENCY-001] ⚠️ [必读卡片](docs/tools/checkpoint-cards.md#emergency-001)

## � 重要文档快速索引

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
- **docs/architecture/security.md** - 安全架构设计

### 🔧 开发规范文档  
- **docs/standards/README.md** - L0-L1-L2标准导航 ⭐
- **docs/standards/naming-conventions-standards.md** - 命名规范
- **docs/standards/workflow-standards.md** - 工作流程规范
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
- **测试环境检查**: `scripts/check_test_env.ps1`
- **代码规范检查**: `scripts/check_code_standards.ps1` 
- **文档同步**: `scripts/sync_readme.ps1`
- **测试模板生成**: `python scripts/generate_test_template.py [module]`
- **检查点验证**: `scripts/ai_checkpoint.ps1 -CardType [编号]`

## ⚠️ 违规处理流程
1. **停止当前操作** - 立即暂停正在进行的工作
2. **识别违规规则** - 明确违反了哪条核心规则  
3. **执行对应检查点** - 按照检查点要求进行验证
4. **重新开始操作** - 从正确的步骤重新执行

## 🔄 任务完成标准流程
每次完成任务必须执行：
1. **规则合规检查** - 确认10条核心规则全部遵守
2. **文档同步验证** - 确认README等相关文档已更新
3. **检查点完成确认** - 验证触发的检查点全部执行
4. **状态文档更新** - 更新current-work-status.md
5. **工作归档转移** - 将完成工作转移到历史档案

## 📝 检查点执行日志
每次执行检查点需记录：
- 检查点类型和编号
- 引用的具体文档条款  
- 验证结果和确认内容
- 执行的具体操作步骤

---
## 🎯 AI使用提醒

**这个文档是为AI优化的工作指南，重点关注：**
- ✅ 每次对话都要执行启动流程
- ✅ 遇到问题先查相关文档  
- ✅ 创建的TODO必须包含检查点
- ✅ 完成工作后及时更新状态

**用户监督要点：**
- 🔍 检查AI是否提供了启动确认
- 🔍 验证AI的TODO是否包含检查点
- 🔍 确认AI遇到问题时先查询了文档
- ⚠️ 发现违规时可随时输入"STOP"
