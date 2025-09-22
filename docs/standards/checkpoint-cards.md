# AI检查点卡片系统 (完整版)

基于MASTER.md工作流程的精准导航检查验证程序。全面覆盖文档驱动开发的每个环节。

## 📋 需求分析类检查卡片 (REQ)

### REQ-001: 业务需求理解验证
**触发条件**: 开始新功能开发、项目启动
**检查重点**: 深度理解业务背景、用户价值、商业目标
**精准导航**:
1. **业务背景** → `docs/requirements/business.md` 第12-45行项目概述+业务目标
2. **用户角色** → `docs/requirements/business.md` 第85-120行目标用户分析
3. **商业模式** → `docs/requirements/business.md` 第140-180行业务模式设计
4. **成功指标** → `docs/requirements/business.md` 第200-230行核心KPI定义

**验证清单**:
□ 已理解项目的商业价值和战略定位
□ 已明确目标用户群体和使用场景  
□ 已掌握业务模式和盈利逻辑
□ 已确认项目成功的衡量标准

### REQ-002: 功能需求分析验证
**触发条件**: 设计具体功能、模块规划
**检查重点**: 功能完整性、需求优先级、验收标准
**精准导航**:
1. **功能规范** → `docs/requirements/functional.md` 第1-80行功能总体规划
2. **模块需求** → `docs/design/modules/{module}/requirements.md` 第10-60行详细功能描述
3. **用户故事** → `docs/design/modules/{module}/requirements.md` 第35-45行用户故事格式
4. **验收标准** → `docs/design/modules/{module}/requirements.md` 第60-85行验收条件

**验证清单**:
□ 已完整梳理功能需求清单
□ 已确认需求优先级和迭代计划
□ 已定义清晰的验收标准
□ 已识别功能间的依赖关系

### REQ-003: 非功能需求确认
**触发条件**: 架构设计前、性能要求确认
**检查重点**: 性能指标、安全要求、合规标准
**精准导航**:
1. **性能要求** → `docs/requirements/non-functional.md` 第30-65行性能指标
2. **安全要求** → `docs/requirements/non-functional.md` 第80-120行安全规范
3. **扩展性** → `docs/requirements/non-functional.md` 第140-170行扩展要求
4. **合规要求** → `docs/requirements/non-functional.md` 第190-220行法规要求

**验证清单**:
□ 已明确性能指标和响应时间要求
□ 已确认安全等级和防护措施
□ 已规划系统扩展性和可维护性
□ 已了解相关法规和合规要求

## 🏗️ 架构设计类检查卡片 (ARCH)

### ARCH-001: 系统架构设计验证
**触发条件**: 开始架构设计、技术选型
**检查重点**: 架构原则、技术栈选择、系统边界
**精准导航**:
1. **架构原则** → `docs/architecture/overview.md` 第12-40行设计原则
2. **技术栈** → `docs/architecture/overview.md` 第60-95行技术选型
3. **系统架构** → `docs/architecture/overview.md` 第110-150行整体架构
4. **扩展规划** → `docs/architecture/overview.md` 第170-200行演进路线

**验证清单**:
□ 已遵循系统架构设计原则
□ 已完成技术栈选型并说明理由
□ 已设计清晰的系统边界和接口
□ 已考虑系统演进和扩展路径

### ARCH-002: 模块架构设计验证
**触发条件**: 模块划分、依赖关系设计
**检查重点**: 模块边界、依赖关系、集成策略
**精准导航**:
1. **模块分类** → `docs/architecture/module-architecture.md` 第12-50行模块分类体系
2. **分层设计** → `docs/architecture/module-architecture.md` 第80-120行分层架构
3. **依赖管理** → `docs/architecture/module-architecture.md` 第150-180行依赖关系
4. **集成策略** → `docs/architecture/module-architecture.md` 第200-240行集成方案

**验证清单**:
□ 已按照分类体系划分模块
□ 已设计清晰的分层架构
□ 已定义模块间依赖关系
□ 已制定模块集成策略

### ARCH-003: 数据架构设计验证
**触发条件**: 数据模型设计、存储架构规划
**检查重点**: 数据模型、存储策略、数据流设计
**精准导航**:
1. **数据模型** → `docs/architecture/data-models.md` 第1-50行领域模型设计
2. **存储架构** → `docs/architecture/data-models.md` 第70-110行存储策略
3. **数据关系** → `docs/architecture/data-models.md` 第130-170行关系设计
4. **数据流** → `docs/design/modules/{module}/design.md` 第120-160行数据流设计

**验证清单**:
□ 已设计符合领域的数据模型
□ 已选择合适的存储技术和策略
□ 已定义清晰的数据关系
□ 已规划完整的数据流转

### ARCH-004: 需求架构调整前置验证
**触发条件**: 修改业务需求、调整系统架构、变更技术标准
**检查重点**: ADR文档审查、变更影响分析、一致性保证
**精准导航**:
1. **决策记录** → `ARCHITECTURE_DECISION_RECORD.md` 第1-100行历史决策审查
2. **需求文档** → `docs/requirements/` 目录完整性检查
3. **架构文档** → `docs/architecture/` 目录一致性验证
4. **变更记录** → `MASTER.md` 第200-250行变更历史跟踪

**验证清单**:
□ 已审查ADR文档中相关历史决策
□ 已分析变更对现有架构的影响
□ 已确认变更不与已记录决策冲突
□ 已更新或新增ADR条目记录此次变更
□ 已同步更新相关需求和架构文档
□ **强制**: 禁止未经ADR审查的架构调整

## 🚀 开发实施类检查卡片 (DEV)

### DEV-001: 模块文档完整性验证
**触发条件**: 开始编码前、模块实施前
**检查重点**: 确保完整的模块文档存在且符合标准
**精准导航**:
1. **文档结构** → `docs/templates/module-template.md` 第1-100行标准模块结构
2. **需求文档** → `docs/design/modules/{module}/requirements.md` 完整性验证
3. **设计文档** → `docs/design/modules/{module}/design.md` 第35-150行技术设计
4. **API规范** → `docs/design/modules/{module}/api-spec.md` 第1-80行接口定义

**验证清单**:
□ 已创建完整的7文档结构 (overview/requirements/design/api-spec/implementation/api-implementation/README)
□ 已完成需求文档的业务规则和验收标准
□ 已完成技术设计的架构图和组件说明
□ 已定义完整的API接口规范
□ **强制**: 必须有完整文档才能开始编码

### DEV-002: 环境与工具准备验证
**触发条件**: 开始开发工作、环境配置
**检查重点**: 开发环境、工具配置、脚本准备
**精准导航**:
1. **环境配置** → `docs/development/environment-setup.md` 开发环境配置指南
2. **工作流程** → `docs/standards/workflow-standards.md` 第51-85行环境准备
3. **脚本工具** → `docs/development/README.md` 第20-50行工具使用指南
4. **强制检查** → `docs/standards/code-development-checklist.md` 第96-130行执行流程

**验证清单**:
□ 已配置Python虚拟环境和依赖
□ 已执行必要的检查脚本
□ 已准备开发和测试工具
□ 已确认代码规范检查工具正常

### DEV-002: 数据模型设计验证
**触发条件**: 操作models.py、设计数据库表
**检查重点**: 数据类型一致性、关系完整性、命名规范
**精准导航**:
1. **字段类型** → `docs/standards/database-standards.md` 第45-70行数据类型规范
2. **外键约束** → `docs/architecture/data-models.md` 第25-50行关系设计
3. **索引优化** → `docs/standards/database-standards.md` 第80-95行性能优化
4. **命名规范** → `docs/standards/naming-conventions.md` 第30-45行数据库命名

**验证清单**:
□ 所有*_id字段定义为Column(Integer, ...)类型
□ 外键关系ForeignKey("table.id")格式正确
□ 表名为snake_case复数形式
□ 字段命名符合snake_case规范
□ 禁止在测试中使用字符串作为ID值

**辅助脚本**: `scripts/ai_checkpoint.ps1 -CardType DEV-002 -ModuleName {module}`

### DEV-003: API设计与路由规范
**触发条件**: 创建*_routes.py、设计API接口
**检查重点**: RESTful设计、安全控制、响应格式
**精准导航**:
1. **路由设计** → `docs/standards/api-standards.md` 第15-40行RESTful规范
2. **认证授权** → `docs/architecture/security.md` 第50-80行API安全
3. **响应格式** → `docs/standards/api-standards.md` 第60-75行统一响应
4. **错误处理** → `docs/standards/api-standards.md` 第90-110行异常设计

**验证清单**:
□ 路由路径符合RESTful规范 (复数资源名)
□ HTTP方法使用正确 (GET/POST/PUT/DELETE)
□ 状态码设计符合标准 (2xx/4xx/5xx)
□ 响应格式统一 (成功/失败格式一致)
□ 已实现认证授权机制

### DEV-004: 组件实现与集成
**触发条件**: 实现service.py、组件开发
**检查重点**: 业务逻辑正确性、依赖注入、错误处理
**精准导航**:
1. **业务规则** → `docs/design/modules/{module}/requirements.md` 第35-60行详细功能描述
2. **组件设计** → `docs/design/modules/{module}/design.md` 第80-120行组件架构
3. **依赖管理** → `docs/standards/code-standards.md` 第40-55行依赖注入
4. **异常处理** → `docs/standards/code-standards.md` 第70-85行错误处理

**验证清单**:
□ 业务逻辑符合需求文档描述
□ 依赖注入配置正确
□ 异常处理覆盖完整
□ 组件接口设计清晰
□ 集成测试通过

### DEV-005: 代码质量与规范
**触发条件**: 代码提交前、Code Review
**检查重点**: 命名规范、代码结构、文档同步
**精准导航**:
1. **命名规范** → `docs/standards/naming-conventions.md` 第20-60行各类命名
2. **代码组织** → `docs/standards/code-standards.md` 第15-35行结构规范
3. **注释文档** → `docs/standards/code-standards.md` 第55-70行文档规范
4. **版本控制** → `docs/development/README.md` 第80-95行Git规范

**验证清单**:
□ 变量函数命名符合snake_case
□ 类名符合PascalCase
□ 常量使用UPPER_CASE
□ 代码结构层次清晰
□ 注释和文档同步更新

## 🧪 测试类检查卡片 (TEST)

### TEST-001: 测试环境配置
**触发条件**: 开始测试会话、配置CI/CD
**检查重点**: 环境隔离、数据库配置、依赖管理
**精准导航**:
1. **环境分离** → `docs/standards/testing-standards.md` 第40-60行环境配置
2. **数据库配置** → `docs/development/testing-setup.md` 第25-45行MySQL设置
3. **依赖注入** → `tests/conftest.py` 第15-35行测试配置
4. **环境变量** → `docs/standards/testing-standards.md` 第70-85行配置管理

**验证清单**:
□ 单元测试使用SQLite内存数据库
□ 集成测试使用MySQL容器端口3308
□ E2E测试使用独立测试环境
□ 测试数据自动清理，不影响其他测试
□ 环境变量配置正确

**辅助脚本**: `scripts/check_test_env.ps1`

### TEST-002: 测试数据一致性
**触发条件**: 编写单元测试、使用模型数据
**检查重点**: 数据类型匹配、关联关系正确
**精准导航**:
1. **数据类型** → `app/modules/{module}/models.py` 第166-200行模型定义
2. **测试模式** → `tests/unit/test_models/test_{module}_models.py` 第25-60行正确示例
3. **关联创建** → `docs/standards/testing-standards.md` 第95-115行测试数据
4. **断言验证** → `docs/standards/testing-standards.md` 第130-145行断言规范

**验证清单**:
□ 所有*_id字段使用Integer类型，禁用字符串
□ 先创建关联对象，再使用其.id属性
□ Decimal字段使用正确数值，不用字符串
□ datetime字段使用对象，不用字符串
□ 外键关系测试正确
□ **pytest fixture配置正确** - 单元测试不能连接MySQL

**常见错误**: 
- ❌ `sku_id="TEST-SKU-001"` → ✅ `sku_id=sku.id`
- ❌ `autouse fixture直接依赖集成测试fixture` → ✅ `使用延迟fixture获取`

**fixture配置错误排查** [NEW 2024-09-21]:
如果单元测试连接MySQL而非SQLite，检查`tests/conftest.py`中：
1. **autouse fixture依赖**: 检查是否有autouse fixture直接依赖integration_test_engine
2. **Mock配置错误**: 检查Mock是否patch了不存在的属性
3. **问题追踪查询**: → `docs/status/issues-tracking.md` ISS-024 完整解决方案

**辅助脚本**: `scripts/ai_checkpoint.ps1 -CardType TEST-002`

### TEST-003: 集成测试设计
**触发条件**: API测试、跨模块测试
**检查重点**: 接口契约、数据流验证、边界场景
**精准导航**:
1. **API契约** → `docs/design/modules/{module}/api-spec.md` 第20-50行接口定义
2. **数据流** → `docs/design/modules/{module}/design.md` 第120-150行数据流设计
3. **测试策略** → `docs/standards/testing-standards.md` 第160-185行集成测试
4. **Mock设计** → `docs/standards/testing-standards.md` 第200-220行Mock策略

**验证清单**:
□ API接口契约测试覆盖完整
□ 跨模块数据流验证正确
□ 边界条件和异常场景覆盖
□ Mock对象使用合理
□ 测试数据隔离

### TEST-004: 性能与安全测试
**触发条件**: 压力测试、安全验证
**检查重点**: 性能指标、安全漏洞、压力边界
**精准导航**:
1. **性能指标** → `docs/requirements/non-functional.md` 第30-50行性能要求
2. **安全测试** → `docs/architecture/security.md` 第100-130行安全验证
3. **压力测试** → `docs/standards/testing-standards.md` 第240-260行性能测试
4. **监控指标** → `docs/operations/monitoring.md` 第40-65行监控规范

**验证清单**:
□ 响应时间符合性能要求
□ 并发处理能力验证
□ 安全漏洞扫描通过
□ SQL注入防护验证
□ 权限控制测试通过

### TEST-007: 测试阶段完成验证
**触发条件**: 模块测试完成、代码保护提交前
**检查重点**: 测试覆盖率、代码质量、文件清理、提交准备
**精准导航**:
1. **测试覆盖率** → `docs/standards/testing-standards.md` 第15-40行覆盖率要求
2. **代码质量** → `docs/standards/code-standards.md` 第15-35行质量标准
3. **文件管理** → `docs/standards/workflow-standards.md` 第100-130行提交规范
4. **状态文档** → `docs/status/module-status.md` 状态同步验证

**验证清单**:
□ 单元测试通过率达到100%
□ 集成测试通过率达到预设目标(≥85%)
□ 所有测试文件语法正确，无编译错误
□ 清理__pycache__目录和临时文件
□ 检查文件保存位置是否正确
□ 更新模块状态文档
□ 验证测试脚本的文件路径和导入正确
□ 确认测试数据隔离和清理机制
□ 代码提交前执行完整性检查

**强制执行脚本**:
- `scripts/clean_temp_files.ps1` - 清理临时文件
- `scripts/check_file_locations.ps1` - 检查文件位置
- `scripts/update_module_status.ps1` - 更新状态文档
- `scripts/pre_commit_check.ps1` - 提交前检查

## 📚 文档类检查卡片 (DOC)

### DOC-001: 架构文档完整性
**触发条件**: 架构设计、系统设计变更
**检查重点**: 架构图准确、组件说明完整、依赖关系清晰
**精准导航**:
1. **架构总览** → `docs/architecture/overview.md` 第12-100行完整架构
2. **模块架构** → `docs/architecture/module-architecture.md` 第12-50行+第100-200行
3. **数据架构** → `docs/architecture/data-models.md` 第1-80行数据设计
4. **安全架构** → `docs/architecture/security.md` 第1-50行+第80-130行

**验证清单**:
□ 架构图与实际系统一致
□ 组件职责描述准确
□ 模块依赖关系清晰
□ 技术选型说明完整
□ 扩展性设计合理

### DOC-002: 模块文档规范性
**触发条件**: 新建模块、修改模块文档
**检查重点**: 7文档结构完整、内容准确、模板一致
**精准导航**:
1. **模块模板** → `docs/templates/module-template.md` 第1-100行标准结构
2. **需求文档** → `docs/design/modules/{module}/requirements.md` 验证完整性
3. **设计文档** → `docs/design/modules/{module}/design.md` 验证技术设计
4. **文档标准** → `docs/standards/document-standards.md` 第20-60行规范要求

**验证清单**:
□ 模块overview.md完整
□ requirements.md业务需求清晰
□ design.md技术设计详细
□ api-spec.md接口规范准确
□ 文档模板一致性

### DOC-003: API文档同步性
**触发条件**: API变更、接口文档更新
**检查重点**: 接口文档与代码同步、示例准确性
**精准导航**:
1. **API规范** → `docs/design/modules/{module}/api-spec.md` 第1-50行接口定义
2. **代码实现** → `app/modules/{module}/router.py` 验证一致性
3. **响应格式** → `docs/standards/api-standards.md` 第60-90行格式标准
4. **版本管理** → `docs/standards/api-standards.md` 第120-140行版本控制

**验证清单**:
□ 接口路径与代码一致
□ 请求响应格式准确
□ 状态码使用正确
□ API示例可执行
□ 版本信息同步

### DOC-004: 运维文档维护
**触发条件**: 部署变更、运维流程更新
**检查重点**: 部署脚本、监控配置、故障处理
**精准导航**:
1. **部署指南** → `docs/operations/deployment.md` 第1-80行部署流程
2. **监控配置** → `docs/operations/monitoring.md` 第1-100行监控设置
3. **故障处理** → `docs/operations/troubleshooting.md` 第1-120行故障指南
4. **运维标准** → `docs/standards/workflow-standards.md` 第40-80行运维规范

**验证清单**:
□ 部署步骤准确可执行
□ 监控指标配置完整
□ 故障处理流程清晰
□ 运维工具文档更新
□ 应急预案可操作

## 🔧 使用指南

### 卡片执行流程
1. **触发识别** → MASTER.md路由表确定卡片类型
2. **精准导航** → 直接定位到具体文档行号范围
3. **逐项验证** → 按验证清单逐项确认
4. **脚本辅助** → 使用自动化脚本加速检查
5. **结果记录** → 在TODO中标记检查完成

### 导航精准度
- **文档路径**: 精确到具体文件
- **行号范围**: 精确到具体章节  
- **检查重点**: 避免无用信息检索
- **验证清单**: 可操作的具体标准

### 违规处理机制
- **发现问题** → 立即停止，修复后重新检查
- **修复验证** → 使用相同卡片重新验证
- **持续改进** → 根据实际使用更新卡片内容

---

## 📋 CHECK:DOC-005 文档目录同步验证

### 🎯 检查目标
确保创建、重命名、删除文档或代码文件时，同步更新同级目录的README文档

### ✅ 验证清单

#### 文档操作同步检查
- [ ] **新建文档同步**
  - 新建文档后已更新同级README.md
  - 文档索引包含新文件说明
  - 文档分类和用途已标明
- [ ] **重命名文档同步**
  - README中的文件引用已全部更新
  - 相关文档的交叉引用已修正
  - 文档链接保持有效性
- [ ] **删除文档同步**
  - README中已移除相关条目
  - 相关文档的死链接已清理
  - 依赖关系已重新整理

#### 代码文件同步检查
- [ ] **代码模块创建**
  - 模块README包含新文件说明
  - 代码功能和接口已文档化
  - 依赖关系已明确标注
- [ ] **代码重构同步**
  - 文档反映最新代码结构
  - API文档与实际接口一致
  - 使用示例保持准确性

#### 目录结构一致性
- [ ] **目录索引完整性**
  - 所有子目录都有README.md
  - 目录用途和内容已说明
  - 导航链接结构清晰

### 📚 参考文档
- `docs/standards/document-standards.md` (60-120行)
- `docs/development/README.md` (1-50行)
- `scripts/README.md` (1-30行)

### 🔧 辅助脚本
```powershell
# 检查文档目录同步状态
scripts\sync_readme.ps1 -CheckOnly -Path [目录路径]
```

---

## 📋 CHECK:DOC-006 工具文档完整性验证

### 🎯 检查目标
确保新增工具必须同步更新使用说明和相关文档

### ✅ 验证清单

#### 工具文档创建
- [ ] **工具说明文档**
  - 工具用途和功能说明
  - 参数列表和使用方法
  - 使用示例和最佳实践
- [ ] **README更新**
  - scripts/README.md包含新工具
  - 工具分类和索引已更新
  - 工具依赖关系已说明
- [ ] **集成文档更新**
  - MASTER.md快速执行脚本已更新
  - 相关检查点卡片已引用
  - 工作流程文档已同步

#### 工具标准化检查
- [ ] **文件头部标准**
  - 包含标准PowerShell注释块
  - 工具描述、参数、示例完整
  - 版权和维护信息准确
- [ ] **函数文档完整**
  - 所有函数有标准注释
  - 参数说明清晰准确
  - 返回值和异常处理已说明
- [ ] **代码注释规范**
  - 关键逻辑有详细注释
  - 复杂算法有说明文档
  - 配置项和常量有注释

#### 工具集成验证
- [ ] **工具链一致性**
  - 与现有工具命名规范一致
  - 参数格式统一标准
  - 错误处理机制统一

### 📚 参考文档
- `docs/standards/code-standards.md` (80-120行)
- `docs/development/tool-development.md` (1-100行)
- `scripts/README.md` (30-80行)

### 🔧 辅助脚本
```powershell
# 验证工具文档完整性
scripts\check_tool_documentation.ps1 -ToolPath [工具路径]
```

---

## 📋 CHECK:DEV-009 代码规范完备性验证

### 🎯 检查目标
验证文件头部、函数说明、代码注释符合标准格式要求

### ✅ 验证清单

#### 文件头部标准检查
- [ ] **Python文件头部**
  - 包含标准文档字符串 ("""...""")
  - 模块用途和功能说明
  - 作者、创建时间、版本信息
- [ ] **PowerShell文件头部**
  - 包含标准注释块 (<#...#>)
  - SYNOPSIS、DESCRIPTION、PARAMETER完整
  - 使用示例和注意事项
- [ ] **通用信息标准**
  - 文件编码声明准确
  - 依赖库和版本要求
  - 许可证和版权信息

#### 函数文档标准检查
- [ ] **Python函数文档**
  - 所有函数有docstring
  - 参数类型和说明完整
  - 返回值和异常说明清晰
- [ ] **PowerShell函数文档**
  - 包含标准帮助注释
  - 参数验证和类型声明
  - 示例和错误处理说明
- [ ] **函数命名规范**
  - 遵循语言命名约定
  - 函数名清晰表达用途
  - 参数名准确描述功能

#### 代码注释质量检查
- [ ] **关键逻辑注释**
  - 复杂算法有详细说明
  - 业务逻辑意图清晰
  - 临时解决方案有标注
- [ ] **配置和常量注释**
  - 配置项用途和影响说明
  - 魔术数字有合理解释
  - 环境依赖有明确标注
- [ ] **TODO和FIXME标准**
  - 使用标准标记格式
  - 包含负责人和时间
  - 优先级和影响范围标明

### 📚 参考文档
- `docs/standards/code-standards.md` (1-80行)
- `docs/standards/document-standards.md` (120-180行)
- `docs/development/coding-guidelines.md` (1-150行)

### 🔧 辅助脚本
```powershell
# 检查代码规范完备性
scripts\check_code_standards.ps1 -FilePath [文件路径] -Standard [检查级别]
```

---

## 📋 CHECK:REQ-003 非功能需求确认

### 🎯 检查目标
在架构设计前确认所有非功能需求（性能、安全、可维护性等）已充分考虑

### ✅ 验证清单

#### 性能需求确认
- [ ] **响应时间要求**
  - API响应时间标准 < 200ms (正常), < 500ms (复杂查询)
  - 页面加载时间 < 2秒
  - 数据库查询优化策略
- [ ] **并发处理能力**
  - 用户并发数量预期
  - 系统资源消耗限制
  - 负载均衡需求评估

#### 安全需求确认  
- [ ] **身份认证标准**
  - JWT token过期策略
  - 密码强度要求
  - 多因素认证需求
- [ ] **数据保护要求**
  - 个人信息脱敏规则
  - 数据加密传输标准
  - 审计日志记录范围

#### 可维护性需求
- [ ] **代码质量标准**
  - 测试覆盖率要求 ≥ 80%
  - 代码复杂度限制
  - 文档同步更新机制
- [ ] **运维监控需求**
  - 健康检查端点设计
  - 错误报警机制
  - 性能监控指标

### 📚 参考文档
- `docs/requirements/non-functional-requirements.md` (1-50行)
- `docs/standards/security-standards.md` (1-100行)  
- `docs/standards/performance-standards.md` (1-80行)
- `docs/operations/monitoring-standards.md` (1-60行)

### 🔧 辅助脚本
```powershell
# 检查非功能需求覆盖率
scripts\check_nfr_coverage.ps1 -Module [模块名]
```

---

## 📋 CHECK:ARCH-003 数据架构设计验证

### 🎯 检查目标  
验证数据模型设计、数据库schema、数据流转架构的完整性和一致性

### ✅ 验证清单

#### 数据模型设计
- [ ] **实体关系完整性**
  - 所有业务实体已建模
  - 实体间关系正确定义
  - 主键外键约束合理
- [ ] **数据类型规范性**  
  - 字段类型选择合适
  - 长度限制符合业务需求
  - 索引策略优化查询性能
- [ ] **数据完整性约束**
  - 业务规则转化为数据约束
  - 唯一性约束正确设置
  - 默认值和允空策略

#### 数据流转架构
- [ ] **数据访问模式**
  - Repository模式实现
  - 查询优化策略
  - 缓存层设计
- [ ] **数据一致性保证**
  - 事务边界定义
  - 并发控制机制
  - 数据同步策略
- [ ] **数据迁移规划**
  - Schema版本控制
  - 数据迁移脚本
  - 回滚策略设计

### 📚 参考文档
- `docs/architecture/data-architecture.md` (1-200行)
- `app/shared/base_models.py` (1-100行)
- `docs/standards/database-standards.md` (1-150行)
- `alembic/versions/` (所有迁移文件)

### 🔧 辅助脚本
```powershell
# 验证数据模型一致性
scripts\validate_data_models.ps1 -CheckRelations -CheckConstraints
```

---

## 📋 CHECK:TEST-005 性能测试验证

### 🎯 检查目标
验证系统在负载条件下的性能表现，确保满足非功能性需求

### ✅ 验证清单

#### 负载测试设计
- [ ] **测试场景设计**
  - 正常负载测试用例
  - 峰值负载测试用例  
  - 压力极限测试用例
- [ ] **性能指标定义**
  - 响应时间阈值设定
  - 吞吐量目标确定
  - 资源利用率限制
- [ ] **测试数据准备**
  - 大量测试数据生成
  - 真实业务场景模拟
  - 数据分布合理性

#### 性能测试执行
- [ ] **API性能测试**
  - 单个API负载测试
  - 并发API调用测试
  - 长时间运行稳定性测试
- [ ] **数据库性能测试**
  - 查询性能优化验证
  - 索引效果测试
  - 连接池配置验证
- [ ] **系统集成性能测试**
  - 端到端性能测试
  - 第三方服务调用性能
  - 缓存命中率测试

#### 性能优化验证
- [ ] **瓶颈识别**
  - 性能分析报告生成
  - 资源消耗热点定位
  - 优化建议制定
- [ ] **优化效果验证**
  - 优化前后对比测试
  - 性能回归测试
  - 持续监控机制

### 📚 参考文档
- `docs/testing/performance-testing-guide.md` (1-150行)
- `tests/performance/` (所有性能测试文件)
- `docs/standards/performance-standards.md` (50-100行)
- `docs/operations/monitoring-standards.md` (30-80行)

### 🔧 辅助脚本
```powershell
# 执行性能测试套件
scripts\run_performance_tests.ps1 -Module [模块名] -LoadLevel [负载级别]
```

---

## 📋 CHECK:TEST-006 安全测试验证  

### 🎯 检查目标
全面验证系统安全控制措施，确保无常见安全漏洞

### ✅ 验证清单

#### 身份认证安全测试
- [ ] **认证机制测试**
  - JWT token安全性验证
  - 密码强度策略测试
  - 会话管理安全测试
- [ ] **授权控制测试**
  - 角色权限边界测试
  - API访问控制验证
  - 资源授权正确性测试
- [ ] **认证绕过测试**
  - 未授权访问尝试
  - Token伪造防护测试
  - 权限提升攻击测试

#### 数据安全测试
- [ ] **输入验证测试**
  - SQL注入攻击测试
  - XSS攻击防护测试
  - 参数篡改防护测试
- [ ] **数据保护测试**
  - 敏感数据加密验证
  - 数据传输安全测试
  - 数据存储安全测试  
- [ ] **业务逻辑安全测试**
  - 业务流程绕过测试
  - 数据一致性攻击测试
  - 并发竞态条件测试

#### 系统安全测试
- [ ] **错误处理安全**
  - 敏感信息泄露测试
  - 错误消息安全性验证
  - 异常处理完整性测试
- [ ] **日志安全测试**
  - 安全事件记录验证
  - 日志注入攻击测试
  - 审计追踪完整性测试

### 📚 参考文档
- `docs/testing/security-testing-guide.md` (1-200行)
- `tests/security/` (所有安全测试文件)
- `docs/standards/security-standards.md` (100-200行)
- `app/core/security_logger.py` (1-100行)

### 🔧 辅助脚本
```powershell
# 执行安全测试套件
scripts\run_security_tests.ps1 -Module [模块名] -TestLevel [测试级别]
```

## 📋 文件操作类检查卡片 (FILE)

### DEV-009: 严重混乱文件强制重建验证
**触发条件**: 文件内容严重混乱、格式错误、大量重复内容
**检查重点**: 安全删除、完全重建、防止错误复制
**精准导航**:
1. **备份策略** → 使用Terminal创建备份文件，不依赖内存保存
2. **删除策略** → Terminal强制删除+清理缓存+删除Python预编译目录  
3. **重建策略** → Terminal创建空文件，逐行编写，禁止复制粘贴
4. **验证策略** → 每步验证，确保文件状态符合预期

**强制执行流程**:
1. **备份原文件**:
   ```powershell
   # 创建备份文件
   Copy-Item "原文件路径" "原文件路径.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
   ```

2. **强力删除**:
   ```powershell
   # 删除混乱文件
   Remove-Item "文件路径" -Force
   # 清理Python缓存
   Remove-Item "__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
   # 清理.pyc文件
   Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
   ```

3. **创建空文件**:
   ```powershell
   # 创建全新空文件
   New-Item "文件路径" -ItemType File -Force
   # 验证文件为空
   Get-Content "文件路径" | Should -BeNullOrEmpty
   ```

4. **逐行重建**:
   - ❌ 禁止: 使用create_file工具
   - ❌ 禁止: 复制粘贴原文件内容
   - ✅ 必须: 使用replace_string_in_file逐行添加
   - ✅ 必须: 每次添加验证内容正确性

**验证清单**:
□ 已创建带时间戳的备份文件
□ 已强力删除原文件和所有缓存
□ 已创建完全空白的新文件
□ 已验证新文件确实为空
□ 已逐行重建内容，无复制粘贴
□ 已验证每行内容的正确性
□ **强制**: 必须参考备份文件而非内存内容
