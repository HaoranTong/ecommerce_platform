# AI开发控制文档 (MASTER)

🤖 **AI严格禁止在未完成启动流程的情况下开始任何工作**

⚠️ **用户立即停止权限**：如AI未按以下模板回复或开始工作前未读取状态文档，用户可立即输入"STOP"强制AI重新开始

---
**✅ MASTER文档确认回复模板（完成全文阅读并理解强制规范并且清楚强制检查点后，在按照此模版回复准确内容）：**
- 已完整阅读MASTER.md全文 ✓
- 已完整读取current-work-status.md ✓
- 当前任务类型：[具体任务描述]  
- 触发检查点：[CHECK:XXX-XXX] 
- 承诺：所有TODO将包含对应检查点标记
- 承诺：完成后将更新状态文档
---

## 🎯 强制执行机制

### ⚡ 违规自动检测规则（AI必须自检）：
- **启动检测**: 每次对话开始，AI必须自问"我是否已读取状态文档？"
- **回复检测**: 每次回复前，AI必须自问"我是否已提供MASTER确认回复？"
- **TODO检测**: 创建TODO时，AI必须自问"每个TODO是否包含对应CHECK点？"
- **完成检测**: 任务完成时，AI必须自问"我是否已更新状态文档？"

### 对话启动强制流程（不可跳过）：
1. **AI必须首先阅读工作状态文档** `docs/status/current-work-status.md`
2. **AI必须提供确认回复** （基于状态文档内容使用上述模板）
3. **识别任务类型** 并说明将触发哪些检查点  
4. **在制定TODO时强制嵌入检查点** 
5. **完成后更新状态文档** 并转移已完成工作到历史档案
6. **如违规，用户指出后AI必须立即停止当前操作并重新开始**

### TODO检查点嵌入规则：
- 开发任务后 → 添加 [CHECK:DEV-xxx]
- 测试任务后 → 添加 [CHECK:TEST-xxx]  
- 文档任务后 → 添加 [CHECK:DOC-xxx]
- 架构任务后 → 添加 [CHECK:ARCH-xxx]

## � AI强制自检清单（每次对话必须执行）

### 对话开始时自检：
- [ ] 我是否已读取 `docs/status/current-work-status.md`？
- [ ] 我是否已提供完整的MASTER确认回复模板？
- [ ] 我是否已识别任务类型和触发的检查点？

### 工作过程中自检：
- [ ] 我创建的每个TODO是否都包含对应的[CHECK:XXX-XXX]标记？
- [ ] 我是否遵循了所有核心强制规则？
- [ ] 我是否正在执行正确的检查点验证流程？

### 任务完成时自检：
- [ ] 我是否已更新 `current-work-status.md`？
- [ ] 我是否已将完成工作转移到 `work-history-archive.md`？
- [ ] 我是否已执行任务完成强制闭环？

**如任何一项为"否"，必须立即停止当前操作，执行对应的纠正措施**

## �🚨 核心强制规则 (完整覆盖版)

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

## 📋 检查点路由表 (完整版-27卡片)

### AI启动类 (AI-START)
- **接收开发任务** → [CHECK:AI-START] AI开发任务启动检查点

### 需求分析类 (REQ)
- **项目启动** → [CHECK:REQ-001] 业务需求理解验证
- **功能规划** → [CHECK:REQ-002] 功能需求分析验证
- **架构设计前** → [CHECK:REQ-003] 非功能需求确认

### 架构设计类 (ARCH)  
- **系统架构设计** → [CHECK:ARCH-001] 系统架构设计验证
- **模块架构规划** → [CHECK:ARCH-002] 模块架构设计验证
- **数据架构设计** → [CHECK:ARCH-003] 数据架构设计验证
- **需求架构调整** → [CHECK:ARCH-004] 需求架构调整前置验证

### 开发实施类 (DEV)
- **编码前准备** → [CHECK:DEV-001] 模块文档完整性验证
- **环境配置** → [CHECK:DEV-002] 环境与工具准备验证
- **操作models.py** → [CHECK:DEV-003] 数据模型实现验证
- **创建*_routes.py** → [CHECK:DEV-004] API路由实现验证
- **实现service.py** → [CHECK:DEV-005] 业务逻辑实现验证
- **安全功能开发** → [CHECK:DEV-006] 安全控制实现验证
- **异常处理实现** → [CHECK:DEV-007] 错误处理实现验证
- **代码提交前** → [CHECK:DEV-008] 代码质量验证
- **文件严重混乱** → [CHECK:DEV-009] 严重混乱文件强制重建验证

### 测试验证类 (TEST)
- **开始测试会话** → [CHECK:TEST-001] 测试环境配置验证
- **编写单元测试** → [CHECK:TEST-002] 单元测试验证
- **测试连接MySQL错误** → [强制CHECK:TEST-002] fixture配置冲突排查
- **Mock统一化** → [CHECK:TEST-003] Mock模式统一验证
- **跨模块测试** → [CHECK:TEST-004] 集成测试验证
- **接口测试** → [CHECK:TEST-005] API测试验证
- **性能压力测试** → [CHECK:TEST-006] 性能测试验证
- **安全测试** → [CHECK:TEST-007] 安全测试验证
- **测试阶段完成** → [CHECK:TEST-008] 测试阶段完成验证

### 状态管理类 (STATUS)
- **对话开始时** → [CHECK:STATUS-001] 工作状态文档阅读验证
- **任务变更时** → [CHECK:STATUS-002] 当前状态更新验证  
- **工作完成时** → [CHECK:STATUS-003] 历史档案转移验证
- **规范违反时** → [CHECK:STATUS-004] 状态恢复验证

### 文档同步类 (DOC)
- **代码完成后** → [CHECK:DOC-001] 代码文档同步验证
- **API变更后** → [CHECK:DOC-002] API文档更新验证
- **架构调整后** → [CHECK:DOC-003] 架构文档维护验证
- **部署变更后** → [CHECK:DOC-004] 部署文档完善验证
- **文件操作后** → [CHECK:DOC-005] 文档目录同步验证
- **工具创建后** → [CHECK:DOC-006] 工具文档完整性验证

## 🎯 检查卡片详情
详细验证步骤 → `docs/tools/checkpoint-cards.md` (26张卡片)
辅助检查脚本 → `scripts/ai_checkpoint.ps1 -CardType [卡片编号]`

## 📁 标准规范文档引用 (完整版)

### 项目基础架构 (FOUNDATION级)
- **PROJECT-FOUNDATION.md** - 项目基础设定 (最高权威)
- docs/README.md - 技术文档导航中心
- MASTER.md - AI开发控制文档 (本文档)

### 需求与架构
- docs/requirements/functional.md - 功能需求规范
- docs/requirements/business.md - 业务需求规范  
- docs/architecture/overview.md - 技术架构总览
- docs/architecture/module-architecture.md - 模块架构设计
- docs/architecture/data-models.md - 数据模型设计
- docs/architecture/security.md - 安全架构设计

### 开发流程与规范 (L1-L2标准体系)
- docs/development/README.md - 开发流程指南
- docs/development/testing-setup.md - 测试环境配置（增强版）
- docs/tools/checkpoint-cards.md - 检查点卡片系统（25张卡片）
- docs/standards/README.md - L0-L1-L2标准文档导航 ⭐
- docs/standards/naming-conventions-standards.md - L1核心：命名规范
- docs/standards/workflow-standards.md - L1核心：工作流程规范
- docs/standards/api-standards.md - L2领域：API设计规范
- docs/standards/database-standards.md - L2领域：数据库设计规范
- docs/standards/code-standards.md - L2领域：代码组织规范
- docs/standards/testing-standards.md - L2领域：测试规范（五层架构）
- docs/standards/document-management-standards.md - L2领域：文档结构规范

### 状态文档管理规范 (强制)
- **核心状态文档** - 固定4个：module-status.md, current-work-status.md, issues-tracking.md, README.md
- **手动更新流程** - 任何模块开发完成后必须手动更新 current-work-status.md
- **状态同步规范** - 手动编辑各状态文档确保信息同步
- **删除保护** - 禁止删除或重命名核心状态文档
- **状态目录清理** - 定期删除多余文档，保持只有4个核心文档

## ⚡ 快速执行脚本
- 启动检查: `scripts/check_docs.ps1 + scripts/check_naming_compliance.ps1`
- 测试环境: `scripts/check_test_env.ps1` (强制执行)
- 测试生成: `python scripts/generate_test_template.py [module] --type all --auto-validate`
- 卡片验证: `scripts/ai_checkpoint.ps1 -CardType [编号]`
- 文档同步: `scripts/sync_readme.ps1` (文件操作后强制执行)
- 代码规范: `scripts/check_code_standards.ps1` (提交前强制执行)

### 工具参考文档
- scripts/README.md - 脚本使用说明（包含generate_test_template.py完整文档）
- scripts/generate_test_template.py - 五层测试架构自动生成器

## 🚫 违规后果
1. 立即停止当前操作
2. 报告违规的具体规则
3. 执行对应的检查点流程
4. 重新开始操作

## � 任务完成强制闭环
**每次完成任务后必须执行的强制流程：**
1. **合规性自检** - 检查是否违反上述10条核心规则
2. **文档同步验证** - 确认相关README已同步更新
3. **检查点完成确认** - 验证所有触发的检查点已正确执行
4. **MASTER文档回归** - 声明"已完成任务，回归MASTER文档确认合规"
5. **如有违规** - 立即暴露问题并执行纠正流程

**防止死循环机制：**
- 仅在用户明确指出违规时才执行纠正
- 自检发现问题时直接纠正，无需重启
- 正常完成任务时进行常规合规确认

## �📝 检查点执行记录
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

## 🔒 违规防范的最终保障

### 技术层面保障：
1. **硬编码检查**: AI必须在每次回复开头显示自检清单执行状态
2. **状态锁定**: 未完成启动流程时，AI禁止执行任何工具操作
3. **强制模板**: 每次对话必须先输出完整的确认回复模板

### 流程层面保障：
1. **用户STOP权限**: 发现违规可立即输入"STOP"中断AI操作
2. **重启机制**: 违规后必须从头执行完整启动流程
3. **审计追踪**: 所有检查点执行情况必须在状态文档中留痕

### 认知层面保障：
1. **优先级锁定**: 启动流程检查的优先级永远高于用户具体任务
2. **责任明确**: AI对违规承担完全责任，不得以"理解偏差"推脱
3. **习惯养成**: 通过重复执行建立强制性工作习惯
