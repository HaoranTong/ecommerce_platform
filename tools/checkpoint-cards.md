<!--version info: v1.0.0, created: 2025-09-23, level: L2, dependencies: naming-conventions-standards.md,../../PROJECT-FOUNDATION.md-->

# AI检查点卡片系统 (完整版)

基于MASTER.md工作流程的精准导航检查验证程序。全面覆盖文档驱动开发的每个环节。

## 📋 需求分析类检查卡片 (REQ)

### REQ-001: 业务需求理解验证
**触发条件**: 开始新功能开发、项目启动
**检查重点**: 深度理解业务背景、用户价值、商业目标
**精准导航**:
1. **业务背景标准** → `docs/requirements/business.md` 第12-45行
2. **用户角色分析** → `docs/requirements/business.md` 第85-120行
3. **商业模式设计** → `docs/requirements/business.md` 第140-180行
4. **成功指标定义** → `docs/requirements/business.md` 第200-230行

**执行脚本**: `tools/validate_business_requirements.ps1`

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

## 🏗️ 架构设计类检查卡片 (ARCH)

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

## 🚀 开发实施类检查卡片 (DEV)

### DEV-001: 模块文档完整性验证
**触发条件**: 开始编码前、模块实施前
**检查重点**: 确保完整的模块文档存在且符合标准
**精准导航**:
1. **文档结构标准** → `docs/templates/module-template.md` 第1-100行
2. **需求文档模板** → `docs/design/modules/{module}/requirements.md`
3. **设计文档模板** → `docs/design/modules/{module}/design.md` 第35-150行
4. **API规范模板** → `docs/design/modules/{module}/api-spec.md` 第1-80行

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
2. **数据架构标准** → `docs/architecture/data-architecture.md` 第25-50行
3. **索引优化标准** → `docs/standards/database-standards.md` 第80-95行
4. **命名规范标准** → `docs/standards/database-standards.md` 第200-250行

**执行脚本**: `tools/validate_data_model.ps1 -Module {module}`

### DEV-004: API设计与路由规范
**触发条件**: 创建*_routes.py、设计API接口
**检查重点**: RESTful设计、安全控制、响应格式
**精准导航**:
1. **路由设计标准** → `docs/standards/api-standards.md` 第15-40行
2. **认证授权标准** → `docs/architecture/security.md` 第50-80行
3. **响应格式标准** → `docs/standards/api-standards.md` 第60-75行
4. **错误处理标准** → `docs/standards/api-standards.md` 第90-110行

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

**辅助脚本**: `tools/ai_checkpoint.ps1 -CardType DEV-009`

## 🧪 测试类检查卡片 (TEST)

### TEST-001: 测试环境配置
**触发条件**: 开始测试会话、配置CI/CD
**检查重点**: 环境隔离、数据库配置、依赖管理
**精准导航**:
1. **环境分离标准** → `docs/standards/testing-standards.md` 第40-60行
2. **数据库配置指南** → `docs/tools/testing-tools.md` 第25-45行
3. **依赖注入配置** → `tests/conftest.py` 第15-35行
4. **环境变量管理** → `docs/standards/testing-standards.md` 第70-85行

**执行脚本**:
1. `tools/check_test_env.ps1` - 快速环境检查
2. `tools/setup_test_env.ps1 -TestMode lite -CheckOnly` - 环境检查
3. `python tools/validate_test_config.py` - 深度诊断

**辅助脚本**: `tools/check_test_env.ps1 -TestMode lite`

### TEST-002: 测试数据一致性
**触发条件**: 编写单元测试、使用模型数据
**检查重点**: 数据类型匹配、关联关系正确
**精准导航**:
1. **数据类型标准** → `docs/standards/testing-standards.md` 第95-115行
2. **测试模式参考** → `tests/unit/test_models/test_user_models.py` 第25-60行
3. **关联创建规范** → `docs/standards/testing-standards.md` 第130-145行
4. **断言验证标准** → `docs/standards/testing-standards.md` 第160-180行

**执行脚本**: 
1. `tools/check_test_env.ps1` - 环境验证
2. `python tools/validate_test_config.py` - 配置诊断

**常见问题排查**:
- 如果单元测试连接MySQL → `docs/status/issues-tracking.md` ISS-024
- 如果fixture配置错误 → `tests/conftest.py` 第15-35行对比

**辅助脚本**: `tools/ai_checkpoint.ps1 -CardType TEST-002`

### TEST-003: 集成测试设计
**触发条件**: API测试、跨模块测试
**检查重点**: 接口契约、数据流验证、边界场景
**精准导航**:
1. **API契约标准** → `docs/design/modules/{module}/api-spec.md` 第20-50行
2. **数据流设计** → `docs/design/modules/{module}/design.md` 第120-150行
3. **集成测试标准** → `docs/standards/testing-standards.md` 第160-185行
4. **Mock策略标准** → `docs/standards/testing-standards.md` 第200-220行

**执行脚本**: 
1. `tools/setup_test_env.ps1 -TestMode full`
2. `tools/run_module_tests.ps1 -Module {module} -TestMode full`

### TEST-004: 性能与安全测试
**触发条件**: 压力测试、安全验证
**检查重点**: 性能指标、安全漏洞、压力边界
**精准导航**:
1. **性能指标标准** → `docs/requirements/non-functional.md` 第30-50行
2. **安全验证标准** → `docs/architecture/security.md` 第100-130行
3. **性能测试标准** → `docs/standards/testing-standards.md` 第240-260行
4. **监控标准** → `docs/operations/monitoring.md` 第40-65行

**执行脚本**:
1. `tools/performance_test.ps1` - 性能测试
2. `tools/security_scan.ps1` - 安全扫描

### TEST-005: API测试验证
**触发条件**: API接口测试、端到端验证
**检查重点**: 接口功能、响应格式、错误处理
**精准导航**:
1. **API测试标准** → `docs/standards/testing-standards.md` 第200-240行
2. **响应格式标准** → `docs/standards/api-standards.md` 第160-200行
3. **状态码标准** → `docs/standards/api-standards.md` 第130-170行
4. **错误处理标准** → `docs/standards/api-standards.md` 第200-240行

**执行脚本**:
1. `tools/setup_test_env.ps1 -TestMode full`  # E2E测试建议使用full模式
2. `pytest tests/e2e/ -v`

### TEST-006: 性能测试验证
**触发条件**: 性能压力测试、负载验证
**检查重点**: 响应时间、并发能力、资源使用
**精准导航**:
1. **性能标准** → `docs/standards/performance-standards.md` 第30-60行
2. **性能架构** → `docs/architecture/performance-architecture.md` 第80-120行
3. **监控指标** → `docs/architecture/performance-architecture.md` 第140-180行
4. **性能测试标准** → `docs/standards/testing-standards.md` 第240-280行

**执行脚本**:
1. `tools/ai_checkpoint.ps1 -CardType TEST-005 -ModuleName {module}`
2. `tools/generate_test_template.py --test-type performance --module {module}`

### TEST-007: 安全测试验证
**触发条件**: 安全功能测试、漏洞扫描
**检查重点**: 认证授权、数据保护、攻击防护
**精准导航**:
1. **安全架构标准** → `docs/architecture/security-architecture.md` 第60-120行
2. **安全测试标准** → `docs/standards/testing-standards.md` 第280-320行
3. **权限控制标准** → `docs/architecture/security-architecture.md` 第120-160行
4. **数据保护标准** → `docs/architecture/security-architecture.md` 第160-200行

**执行脚本**:
1. `tools/ai_checkpoint.ps1 -CardType TEST-006 -ModuleName {module}`
2. `tools/generate_test_template.py --test-type security --module {module}`

### TEST-008: 测试阶段完成验证
**触发条件**: 模块测试完成、代码提交前
**检查重点**: 测试覆盖率、代码质量、文件清理、提交准备
**精准导航**:
1. **测试覆盖率标准** → `docs/standards/testing-standards.md` 第15-40行
2. **代码质量标准** → `docs/standards/code-standards.md` 第15-35行
3. **文件管理标准** → `docs/standards/workflow-standards.md` 第100-130行
4. **状态文档模板** → `docs/status/module-status.md`

**执行脚本**:
1. `tools/clean_temp_files.ps1`
2. `tools/check_file_locations.ps1`
3. `tools/update_module_status.ps1 -Module {module}`
4. `tools/pre_commit_check.ps1`

## 🔧 使用指南

### 卡片执行流程
1. **触发识别** → MASTER.md路由表确定卡片类型
2. **精准导航** → 直接定位到具体文档行号范围
3. **脚本执行** → 使用推荐脚本进行自动化检查
4. **结果记录** → 在TODO中标记检查完成

### 导航精准度
- **文档路径**: 精确到具体文件
- **行号范围**: 精确到具体章节  
- **检查重点**: 避免无用信息检索
- **执行脚本**: 自动化验证工具

### 边界职责说明
- **检查卡片**: 仅提供文档索引和脚本执行引导
- **标准文档**: 定义规则、流程、标准  
- **工具文档**: 提供配置步骤、操作指导

### 卡片更新原则
- **内容边界**: 严禁在卡片中定义规则和标准
- **职责清晰**: 只做导航和脚本引导，不做规则描述
- **权威唯一**: 所有标准以相应的标准文档为准

## 📋 检查卡片索引

### 需求分析类 (REQ)
- **REQ-001**: 业务需求理解验证
- **REQ-002**: 功能需求分析验证  
- **REQ-003**: 非功能需求确认

### 架构设计类 (ARCH)
- **ARCH-001**: 系统架构设计验证
- **ARCH-002**: 模块架构设计验证
- **ARCH-003**: 数据架构设计验证
- **ARCH-004**: 需求架构调整前置验证

### 开发实施类 (DEV)
- **DEV-001**: 模块文档完整性验证
- **DEV-002**: 环境与工具准备验证
- **DEV-003**: 数据模型设计验证
- **DEV-004**: API设计与路由规范
- **DEV-005**: 业务逻辑实现验证
- **DEV-006**: 安全控制实现验证
- **DEV-007**: 错误处理实现验证
- **DEV-008**: 代码质量验证
- **DEV-009**: 代码开发前强制检查验证

### 测试验证类 (TEST)
- **TEST-001**: 测试环境配置
- **TEST-002**: 测试数据一致性
- **TEST-003**: 集成测试设计
- **TEST-004**: 性能与安全测试
- **TEST-005**: API测试验证
- **TEST-006**: 性能测试验证
- **TEST-007**: 安全测试验证
- **TEST-008**: 测试阶段完成验证

### 文档管理类 (DOC)
- **DOC-001**: 架构文档完整性
- **DOC-002**: 模块文档规范性
- **DOC-003**: API文档同步性
- **DOC-004**: 运维文档维护
3. **文件管理** → `docs/standards/workflow-standards.md` 第100-130行提交规范
4. **状态文档** → `docs/status/module-status.md` 状态同步验证

**验证清单**:
□ 单元测试通过率达到100%
□ 集成测试通过率达到预设目标(≥85%)
□ 所有测试文件语法正确，无编译错误
□ 清理__pycache__目录和临时文件
