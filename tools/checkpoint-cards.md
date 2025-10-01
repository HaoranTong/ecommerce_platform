# AI检查点卡片系统

> **作用**：为AI工作流程提供精准导航和文档索引，确保按正确标准执行各类检查点。

## � 启动类 (AI)

### AI-START: 任务理解与计划制定验证
**触发条件**: 接收到新的用户任务时
**检查重点**: 准确理解任务需求、分析任务范围、制定合理的执行计划
**精准导航**:
1. **任务分析标准** → `MASTER.md` 第15-25行
2. **检查点匹配规则** → `MASTER.md` 第26-35行
3. **TODO清单格式** → `MASTER.md` 第36-45行
4. **工作流程规范** → `docs/standards/workflow-standards.md` 第10-50行

**阅读确认**:
问题1: 任务分析的What/Why/Where/How四要素分别指什么？
问题2: TODO清单中每个项目必须包含什么标记？

**执行脚本**: `tools/ai_checkpoint.ps1 -CardType AI-START`

## �📋 需求分析类 (REQ)

### REQ-001: 业务需求理解验证
**触发条件**: 开始新功能开发、项目启动
**检查重点**: 深度理解业务背景、用户价值、商业目标
**精准导航**:
1. **业务背景标准** → `docs/requirements/business.md` 第12-45行
2. **用户角色分析** → `docs/requirements/business.md` 第85-120行
3. **商业模式设计** → `docs/requirements/business.md` 第140-180行
4. **成功指标定义** → `docs/requirements/business.md` 第200-230行

**阅读确认**:
问题1: 根据业务背景标准，用户价值定义的三个核心要素是什么？
问题2: 商业模式设计中的收入模型验证标准包含哪些具体指标？

**执行脚本**: `tools/validate_business_requirements.ps1`
**辅助脚本**: `tools/ai_checkpoint.ps1 -CardType DOC-007`

## 📊 状态管理类 (STATUS)

### STATUS-001: 状态读取验证
**触发条件**: AI任务开始时、恢复工作时
**检查重点**: 准确理解当前工作状态、进度和上下文
**精准导航**:
1. **当前工作状态** → `docs/status/current-work-status.md` 第1-50行
2. **模块状态跟踪** → `docs/status/module-status.md` 第1-100行
3. **问题跟踪记录** → `docs/status/issues-tracking.md` 第1-50行

**阅读确认**:
问题1: 当前正在进行的主要工作任务是什么？
问题2: 有哪些待解决的已知问题？

**执行脚本**: `tools/check_work_status.ps1`

### STATUS-002: 状态更新验证
**触发条件**: 完成任务阶段、遇到重要问题、工作状态变化时
**检查重点**: 及时更新工作状态、记录进度和问题
**精准导航**:
1. **状态更新格式** → `docs/status/current-work-status.md` 第10-30行
2. **进度记录标准** → `docs/status/current-work-status.md` 第35-50行
3. **问题记录格式** → `docs/status/issues-tracking.md` 第15-35行

**阅读确认**:
问题1: 状态更新的标准格式包含哪些必填字段？
问题2: 问题记录需要包含哪些核心信息？

**执行脚本**: `tools/update_work_status.ps1`

### STATUS-003: 工作归档验证
**触发条件**: 完成重要功能、模块开发完成、里程碑达成时
**检查重点**: 完整归档工作成果、更新文档、清理临时文件
**精准导航**:
1. **归档标准格式** → `docs/status/README.md` 第20-40行
2. **成果整理清单** → `docs/status/README.md` 第45-65行
3. **文档更新要求** → `docs/status/README.md` 第70-90行

**阅读确认**:
问题1: 工作归档需要完成哪些标准步骤？
问题2: 归档时需要更新哪些核心文档？

**执行脚本**: `tools/archive_work.ps1`

### STATUS-004: 状态恢复验证
**触发条件**: 中断后恢复工作、切换任务后回归、系统重启后继续
**检查重点**: 准确恢复工作上下文、识别中断点、确认环境状态
**精准导航**:
1. **恢复检查清单** → `docs/status/README.md` 第95-115行
2. **环境验证标准** → `docs/status/README.md` 第120-140行
3. **上下文重建步骤** → `docs/status/README.md` 第145-165行

**阅读确认**:
问题1: 状态恢复时需要验证哪些关键环境配置？
问题2: 如何准确重建工作上下文？

**执行脚本**: `tools/restore_work_context.ps1`

## 🚨 应急处理类 (EMERGENCY)

### EMERGENCY-001: 文件重建验证
**触发条件**: 关键文件丢失、损坏或严重错误时
**检查重点**: 快速诊断问题、选择重建策略、确保数据完整性
**精准导航**:
1. **文件重建策略** → `docs/operations/emergency-procedures.md` 第10-40行
2. **备份恢复流程** → `docs/operations/emergency-procedures.md` 第45-75行
3. **完整性验证标准** → `docs/operations/emergency-procedures.md` 第80-110行
4. **应急脚本使用** → `scripts/README.md` 第30-60行

**阅读确认**:
问题1: 关键文件丢失时的标准处理流程是什么？
问题2: 如何验证重建文件的完整性和正确性？

**执行脚本**: `tools/emergency_rebuild.ps1`

## 📋 需求分析类 (REQ)

### REQ-002: 功能需求分析验证
**触发条件**: 设计具体功能、模块规划
**检查重点**: 功能完整性、需求优先级、验收标准
**精准导航**:
1. **功能规范标准** → `docs/requirements/functional.md` 第1-80行
2. **模块需求模板** → `docs/design/modules/{module}/requirements.md` 第10-60行
3. **用户故事格式** → `docs/design/modules/{module}/requirements.md` 第35-45行
4. **验收标准模板** → `docs/design/modules/{module}/requirements.md` 第60-85行

**执行脚本**: `tools/validate_functional_requirements.ps1`

### REQ-003: 非功能需求确认
**触发条件**: 架构设计前、性能要求确认
**检查重点**: 性能指标、安全要求、合规标准
**精准导航**:
1. **性能指标标准** → `docs/requirements/non-functional.md` 第30-65行
2. **安全要求标准** → `docs/requirements/non-functional.md` 第80-120行
3. **扩展性标准** → `docs/requirements/non-functional.md` 第140-170行
4. **合规要求标准** → `docs/requirements/non-functional.md` 第190-220行

**执行脚本**: `tools/validate_non_functional_requirements.ps1`

## 🏗️ 架构设计类 (ARCH)

### ARCH-001: 系统架构设计验证
**触发条件**: 开始架构设计、技术选型
**检查重点**: 架构原则、技术栈选择、系统边界
**精准导航**:
1. **架构原则标准** → `docs/architecture/overview.md` 第12-40行
2. **技术栈标准** → `docs/architecture/overview.md` 第60-95行
3. **系统架构标准** → `docs/architecture/overview.md` 第110-150行
4. **扩展规划标准** → `docs/architecture/overview.md` 第170-200行

**执行脚本**: `tools/validate_system_architecture.ps1`

### ARCH-002: 模块架构设计验证
**触发条件**: 模块划分、依赖关系设计
**检查重点**: 模块边界、依赖关系、集成策略
**精准导航**:
1. **模块分类标准** → `docs/architecture/module-architecture.md` 第12-50行
2. **分层设计标准** → `docs/architecture/module-architecture.md` 第80-120行
3. **依赖管理标准** → `docs/architecture/module-architecture.md` 第150-180行
4. **集成策略标准** → `docs/architecture/module-architecture.md` 第200-240行

**执行脚本**: `tools/validate_module_architecture.ps1`

### ARCH-003: 数据架构设计验证
**触发条件**: 数据模型设计、存储架构规划
**检查重点**: 数据模型、存储策略、数据流设计
**精准导航**:
1. **数据模型标准** → `docs/architecture/data-models.md` 第1-50行
2. **存储架构标准** → `docs/architecture/data-models.md` 第70-110行
3. **数据关系标准** → `docs/architecture/data-models.md` 第130-170行
4. **数据流标准** → `docs/design/modules/{module}/design.md` 第120-160行

**执行脚本**: `tools/validate_data_architecture.ps1`

### ARCH-004: 需求架构调整前置验证
**触发条件**: 修改业务需求、调整系统架构、变更技术标准
**检查重点**: ADR文档审查、变更影响分析、一致性保证
**精准导航**:
1. **决策记录标准** → `ARCHITECTURE_DECISION_RECORD.md` 第1-100行
2. **需求文档索引** → `docs/requirements/` 目录
3. **架构文档索引** → `docs/architecture/` 目录
4. **变更记录标准** → `MASTER.md` 第200-250行

**执行脚本**: `tools/validate_architecture_changes.ps1 -WithADR`

## � 开发实施类 (DEV)

### DEV-001: 模块文档完整性验证
**触发条件**: 开始编码前、模块实施前
**检查重点**: 确保完整的模块文档存在且符合标准
**精准导航**:
1. **文档结构标准** → `docs/templates/module-template.md` 第1-100行
2. **需求文档模块** → `docs/design/modules/{module}/requirements.md`
3. **设计文档模板** → `docs/design/modules/{module}/design.md` 第35-150行
4. **API规范模板** → `docs/design/modules/{module}/api-spec.md` 第1-80行

**阅读确认**:
问题1: 根据模块模板标准，每个模块文档必须包含哪些固定的章节结构？
问题2: API规范模板中的错误处理部分需要定义哪些必需的响应格式？

**执行脚本**: `tools/validate_module_documentation.ps1`

### DEV-002: 环境与工具准备验证
**触发条件**: 开始开发工作、环境配置
**检查重点**: 开发环境、工具配置、脚本准备
**精准导航**:
1. **环境配置标准** → `docs/development/environment-setup.md`
2. **工作流程标准** → `docs/standards/workflow-standards.md` 第51-85行
3. **脚本工具索引** → `tools/README.md` 第20-50行
4. **代码标准索引** → `docs/standards/code-standards.md` 第1-50行

**执行脚本**: 
1. `tools/setup_development_environment.ps1`
2. `tools/validate_development_tools.ps1`

### DEV-003: 数据模型设计验证
**触发条件**: 操作models.py、设计数据库表
**检查重点**: 数据类型一致性、关系完整性、命名规范
**精准导航**:
1. **字段类型标准** → `docs/standards/database-standards.md` 第45-70行
2. **模型文件** → `app/modules/{module}/models.py`
3. **数据架构标准** → `docs/architecture/data-architecture.md` 第25-50行
4. **索引优化标准** → `docs/standards/database-standards.md` 第80-95行
5. **命名规范标准** → `docs/standards/database-standards.md` 第200-250行

**阅读确认**:
问题1: 根据数据库设计标准，主键字段的命名规范和数据类型要求是什么？
问题2: 索引优化标准中，复合索引的字段顺序规则和性能优化原则是什么？

**执行脚本**: `tools/validate_data_model.ps1 -Module {module}`

### DEV-004: API设计与路由规范
**触发条件**: 创建*_routes.py、设计API接口
**检查重点**: RESTful设计、安全控制、响应格式
**精准导航**:
1. **路由设计标准** → `docs/standards/api-standards.md` 第15-40行
2. **路由文件** → `app/modules/{module}/router.py`
3. **认证授权实现** → `docs/design/system/security-design.md` 第10-60行
4. **响应格式标准** → `docs/standards/api-standards.md` 第60-75行
5. **错误处理标准** → `docs/standards/api-standards.md` 第90-110行

**执行脚本**: `tools/validate_api_design.ps1 -Module {module}`

### DEV-005: 业务逻辑实现验证
**触发条件**: 实现service.py、业务逻辑开发
**检查重点**: 业务规则正确性、服务层架构、事务管理
**精准导航**:
1. **业务规则标准** → `docs/design/modules/{module}/requirements.md` 第35-60行
2. **服务层设计标准** → `docs/design/modules/{module}/design.md` 第80-120行
3. **事务管理标准** → `docs/standards/code-standards.md` 第55-70行
4. **业务异常标准** → `docs/standards/code-standards.md` 第70-85行

**执行脚本**: `tools/validate_business_logic.ps1 -Module {module}`

### DEV-006: 安全控制实现验证
**触发条件**: 开发安全相关功能、权限控制实现
**检查重点**: 认证授权、数据保护、输入验证
**精准导航**:
1. **安全架构标准** → `docs/architecture/security-architecture.md` 第60-100行
2. **API安全标准** → `docs/standards/api-standards.md` 第441-490行
3. **数据保护标准** → `docs/architecture/security-architecture.md` 第140-180行
4. **权限模型标准** → `docs/architecture/security-architecture.md` 第100-140行

**执行脚本**: `tools/validate_security_implementation.ps1 -Module {module}`

### DEV-007: 错误处理实现验证
**触发条件**: 异常处理实现、错误响应设计
**检查重点**: 异常覆盖、错误响应、日志记录
**精准导航**:
1. **错误处理标准** → `docs/standards/api-standards.md` 第200-240行
2. **异常策略标准** → `docs/standards/code-standards.md` 第70-85行
3. **日志规范标准** → `docs/standards/code-standards.md` 第85-100行
4. **状态码标准** → `docs/standards/api-standards.md` 第130-170行

**执行脚本**: `tools/validate_error_handling.ps1 -Module {module}`

**异常处理**:
- 确保所有关键函数(`init`,`dependencies`,`models`,`router`,`schemas`,`service`)至少包含一个try-catch块
- 日志记录异常细节，使用统一日志格式

### DEV-008: 代码质量验证
**触发条件**: 代码提交前、Code Review
**检查重点**: 代码规范、注释完整性、性能优化
**精准导航**:
1. **代码规范标准** → `docs/standards/code-standards.md` 第40-70行
2. **注释标准** → `docs/standards/code-standards.md` 第80-120行
3. **性能要求标准** → `docs/standards/performance-standards.md` 第30-60行
4. **命名规范标准** → `docs/standards/naming-conventions-standards.md` 第150-180行

**执行脚本**:
1. `tools/check_code_standards.ps1 -FilePath {file_path}`
2. `tools/ai_checkpoint.ps1 -CardType DEV-008 -ModuleName {module}`

### DEV-009: 代码开发前强制检查验证
**触发条件**: 开始编写代码前、创建代码文件前
**检查重点**: 文档完整性、命名规范、设计合规
**精准导航**:
1. **文件命名标准** → `docs/standards/naming-conventions-standards.md` 第35-60行
2. **目录结构标准** → `docs/standards/code-standards.md` 第10-35行
3. **API设计标准** → `docs/standards/api-standards.md` 第45-80行
4. **数据模型标准** → `docs/standards/database-standards.md` 第10-65行

**执行脚本**:
1. `tools/dev_checkpoint.ps1 -Phase PRE_DEV -Module {module}`
2. `tools/check_naming_compliance.ps1 -FilePath {file_path}`

**附加检查**:
- **注释密度要求**: ≥ 15%（函数和类应有文档注释）

**辅助脚本**: `tools/ai_checkpoint.ps1 -CardType DEV-009 -ModuleName {module} -FilePath {file_path}`

### DEV-010: 代码审查验证
**触发条件**: 代码提交前、Pull Request创建
**检查重点**: 代码规范、逻辑正确性、安全性检查
**精准导航**:
1. **代码审查标准** → `docs/standards/code-standards.md` 第100-130行
2. **安全检查清单** → `docs/standards/code-standards.md` 第130-150行
3. **性能审查要点** → `docs/standards/performance-standards.md` 第60-90行
4. **测试覆盖率要求** → `docs/standards/testing-standards.md` 第40-60行

**执行脚本**: `tools/code_review_checklist.ps1 -Module {module}`

### DEV-011: 数据迁移验证
**触发条件**: 数据库结构变更、编写迁移脚本前
**检查重点**: 迁移脚本安全性、数据完整性、回滚方案
**精准导航**:
1. **迁移脚本标准** → `docs/standards/database-standards.md` 第300-350行
2. **数据备份策略** → `docs/standards/database-standards.md` 第350-380行
3. **回滚方案设计** → `docs/standards/database-standards.md` 第380-400行
4. **迁移测试要求** → `docs/standards/testing-standards.md` 第200-230行
**执行脚本**: `tools/validate_migration.ps1 -Module {module}`

### DEV-012: 配置管理验证
**触发条件**: 更改环境或配置文件时
**检查重点**: 配置安全性、一致性、版本管理
**精准导航**:
1. **配置管理标准** → `docs/standards/deployment-standards.md` 第50-80行
2. **环境变量规范** → `docs/standards/deployment-standards.md` 第80-100行
3. **密钥管理标准** → `docs/standards/security-architecture.md` 第200-230行
4. **配置版本控制** → `docs/standards/workflow-standards.md` 第80-100行
**执行脚本**: `tools/validate_config.ps1 -Environment {module}`

### DEV-013: 依赖管理验证
**触发条件**: 添加或升级依赖时
**检查重点**: 依赖安全性、兼容性、许可证合规
**精准导航**:
1. **依赖安全检查** → `docs/standards/security-architecture.md` 第230-260行
2. **版本管理策略** → `docs/standards/workflow-standards.md` 第50-80行
3. **许可证合规要求** → `docs/requirements/non-functional.md` 第250-280行
4. **依赖文档标准** → `docs/standards/code-standards.md` 第150-180行
**执行脚本**: `tools/check_dependencies.ps1 -Module {module}`

### DEV-014: 性能基准验证
**触发条件**: 性能优化或关键代码开发后
**检查重点**: 性能基准达标、资源使用、监控埋点
**精准导航**:
1. **性能基准定义** → `docs/standards/performance-standards.md` 第30-60行
2. **监控埋点标准** → `docs/standards/performance-standards.md` 第90-120行
3. **资源使用限制** → `docs/standards/performance-standards.md` 第120-150行
4. **性能测试要求** → `docs/standards/testing-standards.md` 第240-280行
**执行脚本**: `tools/performance_benchmark.ps1 -Module {module}`

## 🧪 测试验证类 (TEST)

### TEST-001: 测试工作流程说明
**触发条件**: ⚠️【关键】任何测试任务开始前必须阅读，了解测试标准和自动生成工具使用方法
**检查重点**: 测试工作流程理解、自动生成工具使用、测试策略和覆盖率标准确认
**精准导航**:
1. **标准测试执行流程** → `docs/standards/testing-standards.md` 第1035-1250行 ⭐
2. **智能测试生成工具** → `docs/standards/testing-standards.md` 第1157-1180行 
3. **测试覆盖率标准** → `docs/standards/testing-standards.md` 第1776-1780行
4. **5层测试架构** → `docs/standards/testing-standards.md` 第40-90行

**阅读确认**:
问题1: 根据测试工作流程说明，使用自动生成工具的命令是什么？
问题2: 单元测试覆盖率的最低标准是多少？

**执行脚本**: `tools/ai_checkpoint.ps1 -CardType TEST-001`

### TEST-002: 测试环境配置
**触发条件**: 初次配置测试环境时（一次性设置）
**检查重点**: 环境隔离、数据库配置、依赖管理、初始化配置
**精准导航**:
1. **测试环境配置指南** → `docs/development/test-env-setup.md` 第1-100行 ⭐
2. **环境分离标准** → `docs/standards/testing-standards.md` 第40-60行
3. **数据库配置指南** → `docs/standards/database-standards.md` 第25-45行
4. **依赖注入配置** → `tests/conftest.py` 第15-35行

**阅读确认**:
问题1: 测试环境的数据库配置与开发环境的主要区别是什么？
问题2: 测试环境配置中，依赖注入配置的关键文件是什么？

**执行脚本**: `tools/setup_test_env.ps1 -TestMode lite`

### TEST-003: 测试环境检查
**触发条件**: 每次测试执行前验证环境可用性
**检查重点**: 环境状态验证、工具可用性检查、配置完整性验证
**精准导航**:
1. **环境检查标准** → `docs/standards/testing-standards.md` 第992-1030行
2. **环境验证脚本** → `tools/check_test_env.ps1` 使用说明
3. **故障排除指南** → `docs/development/test-env-setup.md` 第80-100行
4. **常见问题解决** → `docs/status/issues-tracking.md` ISS-024

**阅读确认**:
问题1: 测试环境检查包含哪些核心验证项？
问题2: 如果环境检查失败，应该执行什么脚本进行修复？

**执行脚本**: `tools/check_test_env.ps1 -TestMode lite`

### TEST-004: 测试工具配置
**触发条件**: 需要配置pytest、coverage等测试工具时
**检查重点**: pytest配置、coverage设置、测试发现配置、报告生成配置
**精准导航**:
1. **pytest配置标准** → `docs/standards/testing-standards.md` 第381-420行
2. **coverage配置指南** → `docs/standards/testing-standards.md` 第411-430行
3. **测试工具使用标准** → `docs/standards/testing-standards.md` 第150-185行
4. **工具配置验证** → `tools/validate_test_config.py` 使用说明

**阅读确认**:
问题1: pytest的测试发现模式配置的关键参数是什么？
问题2: coverage报告的输出格式标准是什么？

**执行脚本**: `python tools/validate_test_config.py`

### TEST-005: Mock数据统一
**触发条件**: 单元测试需要模拟外部依赖时
**检查重点**: Mock策略选择、数据一致性、依赖隔离、测试数据标准化
**精准导航**:
1. **Mock策略标准** → `docs/standards/testing-standards.md` 第200-220行
2. **双工厂架构指南** → `docs/standards/testing-standards.md` 第500-600行
3. **Factory Boy工厂使用** → `docs/standards/testing-standards.md` 第520-550行
4. **数据类型标准** → `docs/standards/testing-standards.md` 第95-115行

**阅读确认**:
问题1: Factory Boy工厂和统一工厂的适用场景分别是什么？
问题2: 单元测试中Mock外部API的标准做法是什么？

**执行脚本**: `tools/ai_checkpoint.ps1 -CardType TEST-005`

### TEST-006: 数据工厂准备
**触发条件**: 测试需要生成或管理测试数据时
**检查重点**: 工厂类型选择、数据创建正确性、数据库配置匹配
**精准导航**:
1. **数据工厂选择指南** → `docs/standards/testing-standards.md` 第580-600行
2. **统一工厂使用** → `docs/standards/testing-standards.md` 第550-580行
3. **关联创建规范** → `docs/standards/testing-standards.md` 第130-145行
4. **断言验证标准** → `docs/standards/testing-standards.md` 第160-180行

**阅读确认**:
问题1: 单元测试和集成测试应该分别使用哪种数据工厂？
问题2: 数据工厂创建关联对象的标准流程是什么？

**执行脚本**: `pytest tests/unit/ -v`

### TEST-007: 单元测试执行
**触发条件**: 当任务涉及模块功能验证或代码质量检查时
**检查重点**: 模块功能验证、代码逻辑正确性、边界条件测试
**精准导航**:
1. **单元测试标准** → `docs/standards/testing-standards.md` 第95-140行
2. **测试模式参考** → `tests/unit/test_models/test_user_models.py` 第25-60行
3. **测试覆盖率标准** → `docs/standards/testing-standards.md` 第15-40行
4. **代码质量标准** → `docs/standards/code-standards.md` 第15-35行

**阅读确认**:
问题1: 单元测试的覆盖率最低要求是多少？
问题2: 单元测试中函数复杂度不能超过多少？

**执行脚本**: `tools/run_module_tests.ps1 -Module {module} -TestMode unit`

### TEST-008: 集成测试执行
**触发条件**: 涉及多模块交互功能验证时
**检查重点**: 接口契约、数据流验证、跨模块交互、边界场景
**精准导航**:
1. **集成测试标准** → `docs/standards/testing-standards.md` 第160-185行
2. **API契约标准** → `docs/design/modules/{module}/api-spec.md` 第20-50行
3. **数据流设计** → `docs/design/modules/{module}/design.md` 第120-150行
4. **跨模块测试指南** → `docs/standards/testing-standards.md` 第140-160行

**阅读确认**:
问题1: 集成测试的主要验证点是什么？
问题2: 跨模块交互测试的数据隔离策略是什么？

**执行脚本**: `tools/run_module_tests.ps1 -Module {module} -TestMode integration`

### TEST-009: 接口测试执行
**触发条件**: 涉及API接口开发或修改时
**检查重点**: 接口功能、响应格式、错误处理、端到端验证
**精准导航**:
1. **API测试标准** → `docs/standards/testing-standards.md` 第200-240行
2. **响应格式标准** → `docs/standards/api-standards.md` 第160-200行
3. **状态码标准** → `docs/standards/api-standards.md` 第130-170行
4. **错误处理标准** → `docs/standards/api-standards.md` 第200-240行

**阅读确认**:
问题1: API接口测试的标准验证项包含哪些？
问题2: 错误响应的标准格式是什么？

**执行脚本**: `tools/setup_test_env.ps1 -TestMode full && pytest tests/e2e/ -v`

### TEST-010: 性能测试执行
**触发条件**: 涉及性能敏感功能或大数据处理时
**检查重点**: 响应时间、并发能力、资源使用、性能指标
**精准导航**:
1. **性能测试标准** → `docs/standards/testing-standards.md` 第240-280行
2. **性能指标标准** → `docs/requirements/non-functional.md` 第30-50行
3. **性能架构** → `docs/architecture/performance-architecture.md` 第80-120行
4. **监控指标** → `docs/architecture/performance-architecture.md` 第140-180行

**阅读确认**:
问题1: 性能测试的核心指标有哪些？
问题2: 性能测试的通过标准是什么？

**执行脚本**: `tools/performance_test.ps1 -Module {module}`

### TEST-011: 安全测试执行
**触发条件**: 涉及认证、授权或敏感数据处理时
**检查重点**: 认证授权、数据保护、攻击防护、安全漏洞扫描
**精准导航**:
1. **安全测试标准** → `docs/standards/testing-standards.md` 第280-320行
2. **安全架构标准** → `docs/architecture/security-architecture.md` 第60-120行
3. **权限控制标准** → `docs/architecture/security-architecture.md` 第120-160行
4. **数据保护标准** → `docs/architecture/security-architecture.md` 第160-200行

**阅读确认**:
问题1: 安全测试的主要验证项是什么？
问题2: 敏感数据处理的安全标准是什么？

**执行脚本**: `tools/security_scan.ps1 -Module {module}`

### TEST-012: 测试失败处理
**触发条件**: 执行任何测试类型时都必须了解失败处理流程
**检查重点**: 失败分析、问题定位、修复策略、重新验证流程
**精准导航**:
1. **测试失败处理流程** → `docs/standards/testing-standards.md` 第320-360行
2. **问题诊断指南** → `docs/development/debugging-guide.md` 第20-50行
3. **常见问题解决** → `docs/status/issues-tracking.md` 相关问题
4. **测试重试策略** → `docs/standards/testing-standards.md` 第340-360行

**阅读确认**:
问题1: 测试失败时的标准处理流程是什么？
问题2: 什么情况下需要重新生成测试数据？

**执行脚本**: `tools/ai_checkpoint.ps1 -CardType TEST-012`

### TEST-013: Generated代码管理
**触发条件**: 涉及自动生成的测试代码管理时
**检查重点**: Generated目录文件状态、文件迁移处理、代码质量验证
**精准导航**:
1. **Generated目录管理** → `docs/standards/testing-standards.md` 第185-220行
2. **文件处理流程** → `docs/standards/testing-standards.md` 第195-210行
3. **测试模板定制指南** → `docs/standards/testing-standards.md` 第170-185行
4. **文件清理规则** → `docs/standards/file-management-standards.md` 第30-50行

**阅读确认**:
问题1: Generated目录的作用是什么？哪些文件应该保留？
问题2: 测试模板从Generated目录迁移的标准步骤是什么？

**执行脚本**: `Get-ChildItem tests\generated\*.py | Format-Table Name, LastWriteTime`

### TEST-014: 测试完成验证
**触发条件**: 所有测试执行完成，需要验证测试结果和覆盖率时
**检查重点**: 测试覆盖率验证、代码质量检查、文件清理、提交准备
**精准导航**:
1. **测试覆盖率标准** → `docs/standards/testing-standards.md` 第15-40行
2. **代码质量标准** → `docs/standards/code-standards.md` 第15-35行
3. **文件管理标准** → `docs/standards/document-management-standards.md` 第770-780行
4. **状态文档模板** → `docs/status/module-status.md`

**阅读确认**:
问题1: 测试完成的验收标准是什么？
问题2: 提交前需要清理哪些临时文件？

**执行脚本**: 
1. `tools/clean_temp_files.ps1`
2. `tools/update_module_status.ps1 -Module {module}`
3. `tools/pre_commit_check.ps1`

---

## � 文档同步类 (DOC)

### DOC-001: 代码文档同步验证
**触发条件**: 代码变更后、模块完成前
**检查重点**: 代码注释、README更新、API文档同步
**精准导航**:
1. **代码文档标准** → `docs/standards/code-standards.md` 第120-160行
2. **README维护标准** → `docs/standards/document-management-standards.md` 第45-80行
3. **API文档标准** → `docs/standards/api-standards.md` 第200-250行
4. **模块文档模板** → `docs/templates/module-template.md`

**阅读确认**:
问题1: 根据代码标准，每个公共函数必须包含哪些类型的注释？
问题2: README文档的维护触发条件是什么？

**执行脚本**: `tools/sync_code_docs.ps1`

### DOC-002: API文档同步验证
**触发条件**: API接口变更、路由添加/修改
**检查重点**: OpenAPI规范、接口文档准确性、示例更新
**精准导航**:
1. **API文档标准** → `docs/standards/api-standards.md` 第1-50行
2. **OpenAPI规范** → `docs/standards/api-standards.md` 第80-130行
3. **接口示例标准** → `docs/standards/api-standards.md` 第160-200行
4. **API测试规范** → `docs/standards/testing-standards.md` 第200-240行

**阅读确认**:
问题1: API文档中每个端点必须包含哪些必需的字段描述？
问题2: 接口示例的错误响应状态码标准是什么？

**执行脚本**: `tools/sync_api_docs.ps1`

### DOC-003: 架构文档同步验证
**触发条件**: 架构调整、系统设计变更
**检查重点**: 架构图更新、设计文档一致性、依赖关系描述
**精准导航**:
1. **架构文档标准** → `docs/standards/document-management-standards.md` 第200-250行
2. **系统架构模板** → `docs/architecture/overview.md` 第1-50行
3. **模块架构模板** → `docs/architecture/module-architecture.md` 第30-80行
4. **依赖管理标准** → `docs/architecture/dependencies.md`

**阅读确认**:
问题1: 架构图更新的触发条件和必要性判断标准是什么？
问题2: 模块间依赖关系描述必须包含哪些关键信息？

**执行脚本**: `tools/sync_arch_docs.ps1`

### DOC-004: 部署文档同步验证
**触发条件**: 部署配置变更、环境需求调整
**检查重点**: 部署指南准确性、环境配置文档、运维手册更新
**精准导航**:
1. **部署文档标准** → `docs/standards/ops-standards.md` 第50-100行
2. **环境配置模板** → `docs/deployment/environment-setup.md`
3. **运维手册标准** → `docs/operations/deployment-guide.md` 第1-40行
4. **监控配置文档** → `docs/operations/monitoring-setup.md`

**阅读确认**:
问题1: 部署文档必须包含哪些环境变量的说明？
问题2: 运维手册中的应急处理流程标准格式是什么？

**执行脚本**: `tools/sync_deployment_docs.ps1`

### DOC-005: 目录同步验证
**触发条件**: 目录结构变更、文件重组
**检查重点**: README索引更新、目录导航准确性、链接有效性
**精准导航**:
1. **目录管理标准** → `docs/standards/document-management-standards.md` 第300-350行
2. **README索引模板** → `docs/README.md` 第1-30行
3. **导航链接标准** → `docs/standards/workflow-standards.md` 第200-230行
4. **文件组织规范** → `docs/standards/naming-conventions-standards.md` 第150-180行

**阅读确认**:
问题1: 目录README文件必须包含哪些固定的结构化元素？
问题2: 链接有效性检查的自动化工具和手动验证要求是什么？

**执行脚本**: `tools/sync_readme.ps1`

### DOC-006: 工具文档同步验证
**触发条件**: 工具脚本变更、新工具添加
**检查重点**: 工具使用说明、脚本参数文档、示例更新
**精准导航**:
1. **工具文档标准** → `docs/standards/document-management-standards.md` 第600-650行
2. **脚本文档模板** → `docs/tools/script-template.md`
3. **工具索引标准** → `tools/README.md` 第10-50行
4. **使用示例规范** → `docs/standards/code-standards.md` 第200-230行

**阅读确认**:
问题1: 工具脚本文档必须包含哪些参数说明格式？
问题2: 使用示例的验证和测试要求是什么？

**执行脚本**: `tools/sync_tool_docs.ps1`

### DOC-007: 强制文档阅读验证
**触发条件**: 任何检查点执行前的文档阅读环节
**检查重点**: 确保AI实际阅读相关文档内容而非推测回答
**精准导航**:
1. **阅读确认标准** → `docs/standards/document-management-standards.md` 第577-600行
2. **检查点卡片标准** → `docs/standards/document-management-standards.md` 第577-620行
3. **文档导航规范** → `MASTER.md` 第130-176行
4. **阅读验证机制** → `tools/checkpoint-cards.md` 第1-10行

**阅读确认**:
问题1: 阅读确认字段在检查点卡片中的具体位置是什么？
问题2: 阅读确认问题设计的核心原则是什么，如何确保无法推测回答？

**执行脚本**: `tools/enforce_doc_reading.ps1`
**辅助脚本**: `tools/ai_checkpoint.ps1 -CardType DOC-007`

---

## �📋 检查点索引

| 类别 | 编号范围 | 检查点数量 |
|------|----------|------------|
| 启动类 | AI-START | 1个 |
| 需求分析类 | REQ-001 ~ REQ-003 | 3个 |
| 架构设计类 | ARCH-001 ~ ARCH-004 | 4个 |
| 开发实施类 | DEV-001 ~ DEV-014 | 14个 |
| 测试验证类 | TEST-001 ~ TEST-014 | 14个 |
| 状态管理类 | STATUS-001 ~ STATUS-004 | 4个 |
| 文档同步类 | DOC-001 ~ DOC-007 | 7个 |
| 应急处理类 | EMERGENCY-001 | 1个 |

**总计**: 48个检查点卡片
