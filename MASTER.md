# AI开发控制文档 (MASTER)

## � 文档说明

本文档定义AI执行任何单一任务的标准操作流程，与`docs/standards/software-development-lifecycle-standards.md`互为补充：
- **MASTER文档6步流程**：适用于AI执行任何单一任务的标准操作
- **软件开发生命周期标准**：用于整体项目流程管控和阶段划分
- **检查点卡片系统**：为AI提供精准的上下文信息和执行指导

## �🔐 用户指令格式

### 标准任务启动格式：
> **"按MASTER文档执行，完成AI工作流程规定的所有步骤：[具体任务]"**

## 🚀 AI工作流程

### 步骤1: 读取当前工作状态
📖 读取 `docs/status/current-work-status.md` 了解当前工作状态

### 步骤2: 执行AI-START检查点验证
🎯 必须执行 [CHECK:AI-START] 验证：
- 仔细阅读AI-START卡片的完整内容
- 回答所有阅读确认问题
- 分析任务的What/Why/Where/How四要素

### 步骤3: 深度分析用户指令  
🔍 基于AI-START验证结果，深度分析任务需求

### 步骤4: 匹配相关检查点
📋 **强制遍历机制**：必须按以下步骤完整执行检查点匹配
1. **读取完整检查点列表** - 逐一阅读本文档"详细检查点列表"中的每个检查点
2. **逐个评估触发条件** - 对每个检查点，明确回答"是否与当前任务相关"及理由
3. **输出匹配过程** - 记录每个检查点的评估结果（匹配/不匹配/理由）
4. **特别注意TEST-001** - ⚠️ 任何测试相关任务都必须首先检查TEST-001卡片，了解测试工作流和自动生成工具

🚨 **关键要求**: 
- 必须完整遍历所有检查点，不得跳过任何一个
- 必须仔细阅读每个检查点的"触发条件"字段
- 必须输出完整的匹配评估过程

**输出格式要求**：
```
## 📋 检查点匹配评估

### 启动类
- [CHECK:AI-START] ✅ 匹配 - 理由：任何任务都需要执行

### 测试验证类  
- [CHECK:TEST-001] ✅ 匹配 - 理由：测试任务必须了解测试工作流
- [CHECK:TEST-002] ✅ 匹配 - 理由：需要配置测试环境
- [CHECK:TEST-003] ✅ 匹配 - 理由：需要检查测试环境可用性
- [CHECK:TEST-004] ✅ 匹配 - 理由：需要配置测试工具
- [CHECK:TEST-005] ✅ 匹配 - 理由：单元测试需要Mock外部依赖
- [CHECK:TEST-007] ✅ 匹配 - 理由：任务涉及模块功能验证
- [CHECK:TEST-012] ✅ 匹配 - 理由：需要了解测试失败处理流程
- [CHECK:TEST-014] ✅ 匹配 - 理由：需要验证测试结果
- [CHECK:TEST-008] ❌ 不匹配 - 理由：单元测试不涉及多模块交互
...

## 最终匹配的检查点：[TEST-001, TEST-002, TEST-003, TEST-004, TEST-005, TEST-007, TEST-012, TEST-014]
```

### 步骤5: 按触发条件排序检查点
🔍 严格按照检查点卡片中的"触发条件"安排执行顺序：
- 优先执行标记为"开始前"、"准备阶段"的检查点
- 其次执行"配置"、"环境"相关检查点  
- 再执行"实施"、"执行"相关检查点
- 最后执行"完成"、"验证"相关检查点

### 步骤6: 创建TODO清单
📝 每个TODO项必须包含：
- [CHECK:XXX-XXX] 检查点标记
- 该检查点"阅读确认"问题的回答
- 严格按触发条件顺序排列

**TODO清单格式要求**：
```
## 📋 TODO清单

### 1. [CHECK:TEST-001] 测试工作流程说明
**文档阅读确认**：
- Q: 根据测试工作流程说明，使用自动生成工具的命令是什么？
- A: [AI必须基于文档内容回答]

**执行步骤**：
- 阅读测试标准和工作流程
- 了解自动生成工具使用方法
- 确认测试策略和覆盖率要求

### 2. [CHECK:TEST-002] 测试环境配置
**文档阅读确认**：
- Q: 单元测试覆盖率标准是多少？
- A: [AI必须基于文档内容回答]

**执行步骤**：
- ...
```

### 步骤7: 等待用户确认TODO清单
⏸️ **强制确认机制**：
- AI生成TODO清单后必须停止执行
- 用户检查每个检查点的"文档阅读确认"回答是否正确
- 发现理解错误时，输入"重新生成TODO"
- 确认无误后，输入"确认执行TODO"

### 步骤8: 执行工作
🔧 按TODO清单执行，每个检查点执行前必须：
1. 重新确认已理解该卡片的文档指引
2. 执行指定的验证脚本
3. 遇到问题时先查阅相关文档

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
2. **检查点强制执行** → 每个TODO项必须包含对应的检查点标记和文档阅读确认
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
- **数据架构** → [CHECK:ARCH-003] ⚠️ [必读卡片](tools/checkpoint-cards.md#arch-003)
- **架构调整** → [CHECK:ARCH-004] ⚠️ [必读卡片](tools/checkpoint-cards.md#arch-004)

### 💻 开发实施类
- **编码准备** → [CHECK:DEV-001] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-001)
  **触发条件**: 开始任何代码编写或修改任务前
- **环境配置** → [CHECK:DEV-002] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-002)
  **触发条件**: 编码准备阶段，需要配置开发环境时
- **数据模型** → [CHECK:DEV-003] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-003)
  **触发条件**: 涉及数据库表结构或模型类开发时
- **API路由** → [CHECK:DEV-004] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-004)
  **触发条件**: 开发或修改REST API接口时
- **业务逻辑** → [CHECK:DEV-005] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-005)
  **触发条件**: 实现核心业务功能或服务层代码时
- **安全功能** → [CHECK:DEV-006] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-006)
  **触发条件**: 涉及用户认证、权限控制或敏感数据处理时
- **异常处理** → [CHECK:DEV-007] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-007)
  **触发条件**: 实现业务逻辑时，需要处理错误和异常情况
- **代码质量** → [CHECK:DEV-008] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-008)
  **触发条件**: 代码编写完成后，进行质量检查时
- **强制检查** → [CHECK:DEV-009] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-009)
  **触发条件**: 代码提交前的最终质量验证
- **代码审查** → [CHECK:DEV-010] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-010)
  **触发条件**: 代码完成后，提交合并请求前
- **数据迁移** → [CHECK:DEV-011] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-011)
  **触发条件**: 涉及数据库结构变更或数据迁移时
- **配置管理** → [CHECK:DEV-012] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-012)
  **触发条件**: 涉及环境配置文件或应用配置修改时
- **依赖管理** → [CHECK:DEV-013] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-013)
  **触发条件**: 需要添加、升级或移除项目依赖时
- **性能基准** → [CHECK:DEV-014] ⚠️ [必读卡片](tools/checkpoint-cards.md#dev-014)
  **触发条件**: 涉及性能敏感的代码实现时

### 🧪 测试验证类
- **测试工作流程说明** → [CHECK:TEST-001] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-001)
  **触发条件**: ⚠️【关键】任何测试任务开始前必须阅读，了解测试标准和自动生成工具使用方法
- **测试环境配置** → [CHECK:TEST-002] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-002)
  **触发条件**: 初次配置测试环境时（一次性设置）
- **测试环境检查** → [CHECK:TEST-003] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-003)
  **触发条件**: 每次测试执行前验证环境可用性
- **测试工具配置** → [CHECK:TEST-004] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-004)
  **触发条件**: 需要配置pytest、coverage等测试工具时
- **Mock数据统一** → [CHECK:TEST-005] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-005)
  **触发条件**: 单元测试需要模拟外部依赖时
- **数据工厂准备** → [CHECK:TEST-006] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-006)
  **触发条件**: 测试需要生成或管理测试数据时
- **单元测试执行** → [CHECK:TEST-007] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-007)
  **触发条件**: 当任务涉及模块功能验证或代码质量检查时
- **集成测试执行** → [CHECK:TEST-008] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-008)
  **触发条件**: 涉及多模块交互功能验证时
- **接口测试执行** → [CHECK:TEST-009] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-009)
  **触发条件**: 涉及API接口开发或修改时
- **性能测试执行** → [CHECK:TEST-010] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-010)
  **触发条件**: 涉及性能敏感功能或大数据处理时
- **安全测试执行** → [CHECK:TEST-011] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-011)
  **触发条件**: 涉及认证、授权或敏感数据处理时
- **测试失败处理** → [CHECK:TEST-012] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-012)
  **触发条件**: 执行任何测试类型时都必须了解失败处理流程
- **Generated代码管理** → [CHECK:TEST-013] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-013)
  **触发条件**: 涉及自动生成的测试代码管理时
- **测试完成验证** → [CHECK:TEST-014] ⚠️ [必读卡片](tools/checkpoint-cards.md#test-014)
  **触发条件**: 所有测试执行完成，需要验证测试结果和覆盖率时

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
- **测试执行脚本**: `tools/run_module_tests.ps1 -Module [模块名]`
- **集成测试**: `tools/integration_test.ps1`
- **代码规范检查**: `tools/check_code_standards.ps1` 
- **文档同步**: `tools/sync_readme.ps1`
- **测试模板生成**: `python tools/generate_test_template.py [module]`
- **测试结构验证**: `python tools/validate_test_structure.py`
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