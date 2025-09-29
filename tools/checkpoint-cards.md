# AI检查点卡片系统

> **作用**：为AI工作流程提供精准导航和文档索引，确保按正确标准执行各类检查点。

## 📋 需求分析类 (REQ)

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

### DEV-011: 数据迁移验证
**触发条件**: 数据库结构变更、数据迁移脚本编写
**检查重点**: 迁移脚本安全性、数据完整性、回滚方案
**精准导航**:
1. **迁移脚本标准** → `docs/standards/database-standards.md` 第300-350行
2. **数据备份策略** → `docs/standards/database-standards.md` 第350-380行
3. **回滚方案设计** → `docs/standards/database-standards.md` 第380-400行
4. **迁移测试要求** → `docs/standards/testing-standards.md` 第200-230行

**执行脚本**: `tools/validate_migration.ps1 -Module {module}`

### DEV-012: 配置管理验证
**触发条件**: 环境配置变更、配置文件修改
**检查重点**: 配置安全性、环境一致性、版本管理
**精准导航**:
1. **配置管理标准** → `docs/standards/deployment-standards.md` 第50-80行
2. **环境变量规范** → `docs/standards/deployment-standards.md` 第80-100行
3. **密钥管理标准** → `docs/standards/security-architecture.md` 第200-230行
4. **配置版本控制** → `docs/standards/workflow-standards.md` 第80-100行

**执行脚本**: `tools/validate_config.ps1 -Environment {env}`

### DEV-013: 依赖管理验证
**触发条件**: 新增依赖、版本升级、依赖变更
**检查重点**: 依赖安全性、版本兼容性、许可证合规
**精准导航**:
1. **依赖安全检查** → `docs/standards/security-architecture.md` 第230-260行
2. **版本管理策略** → `docs/standards/workflow-standards.md` 第50-80行
3. **许可证合规要求** → `docs/requirements/non-functional.md` 第250-280行
4. **依赖文档标准** → `docs/standards/code-standards.md` 第150-180行

**执行脚本**: `tools/check_dependencies.ps1 -Module {module}`

### DEV-014: 性能基准验证
**触发条件**: 性能关键代码开发、优化实施
**检查重点**: 性能基准达标、资源使用合理、监控埋点
**精准导航**:
1. **性能基准定义** → `docs/standards/performance-standards.md` 第30-60行
2. **监控埋点标准** → `docs/standards/performance-standards.md` 第90-120行
3. **资源使用限制** → `docs/standards/performance-standards.md` 第120-150行
4. **性能测试要求** → `docs/standards/testing-standards.md` 第240-280行

**执行脚本**: `tools/performance_benchmark.ps1 -Module {module}`

## 🧪 测试类 (TEST)

### TEST-001: 测试环境配置
**触发条件**: 开始测试会话、配置CI/CD
**检查重点**: 环境隔离、数据库配置、依赖管理
**精准导航**:
1. **环境分离标准** → `docs/standards/testing-standards.md` 第40-60行
2. **数据库配置指南** → `docs/standards/database-standards.md` 第25-45行
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
2. **安全实现验证** → `docs/design/system/security-design.md` 第60-120行
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

**阅读确认**:
问题1: 根据测试标准，单元测试覆盖率的最低要求是多少？
问题2: 代码质量检查中，函数复杂度不能超过多少？

**执行脚本**:
1. `tools/clean_temp_files.ps1`
2. `tools/check_file_locations.ps1`
3. `tools/update_module_status.ps1 -Module {module}`
4. `tools/pre_commit_check.ps1`

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
| 需求分析类 | REQ-001 ~ REQ-003 | 3个 |
| 架构设计类 | ARCH-001 ~ ARCH-004 | 4个 |
| 开发实施类 | DEV-001 ~ DEV-014 | 14个 |
| 测试验证类 | TEST-001 ~ TEST-008 | 8个 |
| 文档同步类 | DOC-001 ~ DOC-007 | 7个 |

**总计**: 36个检查点卡片
