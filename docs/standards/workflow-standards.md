<!--
文档说明：
- 内容：标准化开发工作流程，从需求到部署的完整流程  
- 使用方法：每次开发新功能时严格按照此流程执行
- 引用关系：被MASTER.md引用，是开发工作的核心指导
- 优化状态：第一期优化完成 - 工具引用已标记待修正，结构已优化
- 文档长度：233行（符合AI优化标准）
- 检查点集成：已添加完整的[CHECK:XXX-XXX]标记
-->

# 开发工作流程

## 开发阶段划分

### Phase 1: 需求准备阶段 [CHECK:REQ-001] [CHECK:REQ-002] [CHECK:REQ-003]
**目标**: 确保需求清晰明确，技术方案可行

#### 1.1 需求分析 [CHECK:REQ-001]
- [ ] 阅读 [业务需求](../requirements/business.md) 理解项目背景
- [ ] 查看 [功能需求](../requirements/functional.md) 了解具体功能要求  
- [ ] 确认 [非功能需求](../requirements/non-functional.md) 的技术约束
- [ ] 识别功能依赖关系和集成点

#### 1.2 技术方案设计 [CHECK:ARCH-001] [CHECK:ARCH-002] 
- [ ] 遵循 [架构总览](../architecture/overview.md) 的技术栈选择
- [ ] 按照 [API设计标准](api-standards.md) 设计接口
- [ ] 遵循 [数据库设计规范](database-standards.md) 设计数据结构  
- [ ] 考虑 [安全架构](../architecture/security.md) 要求
- [ ] 规划 [第三方集成](../architecture/integration.md) 需求

#### 1.3 模块文档创建 【待修正-工具验证】
<!--
TOOL-REFERENCE-PENDING: 需要验证scripts/create_module_docs.ps1和scripts/check_docs.ps1的实际状态
原内容：使用自动化工具创建完整文档结构
修正计划：确认工具存在性和正确用法后重新编写此部分
-->
**临时方案**: 手动创建模块文档结构，后续工具验证后更新自动化流程

**必须创建的7个强制文档:**
- [ ] `README.md` - 模块导航和快速入口
- [ ] `overview.md` - 技术架构和概述  
- [ ] `requirements.md` - 详细功能需求
- [ ] `design.md` - 技术设计方案
- [ ] `api-spec.md` - API接口规范
- [ ] `api-implementation.md` - API接口实施细节记录
- [ ] `implementation.md` - 开发记录文档

### Phase 2: 开发实施阶段 [CHECK:DEV-001] [CHECK:DEV-002] [CHECK:DEV-003] [CHECK:DEV-004] [CHECK:DEV-005]
**目标**: 高质量代码实现，完整测试覆盖

#### 2.1 环境准备 【待修正-工具验证】
<!--
TOOL-REFERENCE-PENDING: 需要验证dev_env.ps1和dev_tools.ps1的实际状态和用法
原内容：配置开发环境和数据库检查脚本
修正计划：确认脚本存在性和正确用法后重新编写此部分
-->
**临时方案**: 
1. 手动配置开发环境变量
2. 手动检查数据库连接状态  
3. 创建功能分支：`git checkout -b feature/{module-name}`
4. 更新依赖：`pip install -r requirements.txt`

#### 2.2 代码开发标准 [CHECK:DEV-002] [CHECK:DEV-003] [CHECK:DEV-004] [CHECK:DEV-005]
- [ ] **数据模型** - 在 `app/modules/{module}/models.py` 中定义 SQLAlchemy 模型 [CHECK:DEV-002]
- [ ] **API路由** - 在 `app/modules/{module}/router.py` 中实现路由 [CHECK:DEV-004]
- [ ] **数据验证** - 在 `app/modules/{module}/schemas.py` 中定义 Pydantic 模式 [CHECK:DEV-003]
- [ ] **业务逻辑** - 在 `app/services/` 中实现服务层 [CHECK:DEV-005]
- [ ] **错误处理** - 统一异常处理和错误响应 [CHECK:DEV-007]

#### 2.3 代码质量要求 [CHECK:DEV-006] [CHECK:DEV-007] [CHECK:DEV-008]
**必须包含**:
- 完整字段定义和验证规则  
- 统一异常处理和错误响应
- 业务逻辑完整实现
- 代码注释和文档字符串
- 安全验证和权限检查

> 详细代码示例参考：`docs/examples/code-standards-examples.md` 【待创建】

#### 2.4 文档同步要求 [CHECK:DOC-001] [CHECK:DOC-002]
**IF 开发进展变化 THEN 必须更新**:
- [ ] `docs/modules/{module}/implementation.md` - 开发进展记录
- [ ] `docs/modules/{module}/api-implementation.md` - API实现细节

**IF 遇到问题 THEN 必须记录**:
- [ ] `docs/status/issues-tracking.md` - 问题跟踪和解决方案

#### 2.5 文档完整性验证 【待修正-工具验证】
<!--
TOOL-REFERENCE-PENDING: 需要验证check_docs.ps1脚本的实际状态
原内容：每日文档完整性检查
修正计划：确认脚本存在性和正确参数后重新编写此部分
-->
**临时方案**: 手动检查模块文档是否包含所有7个必需文档并内容完整

### Phase 3: 测试验证阶段 [CHECK:TEST-001] [CHECK:TEST-002] [CHECK:TEST-003] [CHECK:TEST-004] [CHECK:TEST-005]
**目标**: 确保功能正确性和系统稳定性

#### 🚨 强制环境检查 【待修正-工具验证】
<!--
TOOL-REFERENCE-PENDING: 需要验证check_test_env.ps1和setup_test_env.ps1的实际状态
原内容：强制测试环境检查流程
修正计划：确认测试工具和脚本状态后重新编写此部分
-->
**临时方案**: 手动检查测试环境配置，确保数据库连接和测试数据准备就绪

#### 3.1 单元测试 [CHECK:TEST-002]
**必须覆盖**:
- [ ] 正常业务逻辑测试
- [ ] 边界条件和异常处理测试  
- [ ] 数据验证测试
- [ ] Mock外部依赖测试

#### 3.2 集成测试 [CHECK:TEST-004]  
**必须覆盖**:
- [ ] API接口完整测试
- [ ] 数据库操作测试
- [ ] 模块间集成测试
- [ ] 权限验证测试

> 详细测试示例参考：`docs/examples/testing-examples.md` 【待创建】

#### 3.3 标准测试执行流程 【待修正-工具验证】
<!--
TOOL-REFERENCE-PENDING: 需要验证所有测试相关脚本的实际状态
原内容：分层测试执行流程
修正计划：确认测试架构和工具后重新编写此部分
-->
**临时方案**: 
- 开发阶段：手动执行单元测试
- 功能完成：手动执行集成测试  
- 提交前：手动执行完整测试套件

#### 3.4 系统测试 【待修正-工具验证】
<!--
TOOL-REFERENCE-PENDING: 需要验证smoke_test.ps1和性能测试工具状态
原内容：系统级测试流程
修正计划：确认测试工具后重新编写此部分
-->
**临时方案**: 手动执行关键功能验证和基础性能检查

### Phase 4: 文档完善阶段 [CHECK:DOC-001] [CHECK:DOC-002] [CHECK:DOC-003]
**目标**: 完整准确的技术文档，100%符合标准

#### 4.1 API文档更新  
- [ ] 更新 `docs/modules/{module}/api-spec.md` - 接口规范要求
- [ ] 更新 `docs/modules/{module}/api-implementation.md` - 实施细节记录
- [ ] 确保遵循 `standards/openapi.yaml` 全局契约
- [ ] 添加完整的请求响应示例
- [ ] 说明错误处理和状态码

#### 4.2 模块文档完善
- [ ] 完善 `docs/modules/{module}/design.md` 技术设计
- [ ] 更新 `docs/modules/{module}/implementation.md` 实现细节  
- [ ] 完善 `docs/modules/{module}/requirements.md` 需求文档
- [ ] 更新 `docs/modules/{module}/overview.md` 技术概述
- [ ] 确保 `docs/modules/{module}/README.md` 导航完整

#### 4.3 文档标准化验证 【待修正-工具验证】
<!--
TOOL-REFERENCE-PENDING: 需要验证check_docs.ps1脚本功能
原内容：自动化文档验证流程  
修正计划：确认文档检查工具后重新编写此部分
-->
**临时方案**: 手动检查模块文档完整性，确保包含所有必需内容

**⚠️ 重要**: 不符合文档标准的代码不允许合并到主分支 [CHECK:DOC-003]

### Phase 5: 代码提交阶段 [CHECK:DEV-008] [CHECK:STATUS-002] [CHECK:STATUS-003] [CHECK:STATUS-004]
**目标**: 规范化代码提交和版本管理

#### 5.1 提交前检查 【待修正-工具验证】
<!--
TOOL-REFERENCE-PENDING: 需要验证所有检查脚本的实际状态
原内容：提交前自动化检查流程
修正计划：确认所有检查工具后重新编写此部分
-->
**临时方案**:
1. 手动检查文档完整性
2. 手动运行所有测试
3. 检查代码质量（如有工具配置）
4. 确保数据库迁移正确：`alembic upgrade head`
5. 手动执行关键功能验证

**⚠️ 提交阻止规则**: 如果文档完整性检查不通过，禁止提交代码 [CHECK:DOC-003]

#### 5.2 自动化提交 【待修正-工具验证】
<!--
TOOL-REFERENCE-PENDING: 需要验证feature_finish.ps1脚本状态
原内容：自动化提交流程
修正计划：确认脚本功能后重新编写此部分
-->
**临时方案**: 使用手动提交流程，确保每个步骤手动验证

#### 5.3 手动提交流程
```powershell
# 如果不使用自动化脚本
git add .
git commit -m "feat: 实现{模块名}功能

- 完成{具体功能1}
- 完成{具体功能2}
- 添加相关测试用例
- 更新API文档

Closes #issue_number"

git push origin feature/{module-name}

# 切换到dev分支并合并
git checkout dev
git pull origin dev
git merge feature/{module-name}
git push origin dev
```

## 开发规范和约束

### 代码质量标准
1. **功能完整性** - 所有功能按需求规范实现
2. **错误处理** - 完善的异常处理和错误响应
3. **数据验证** - 严格的输入验证和数据校验
4. **性能考虑** - 合理的数据库查询和缓存使用
5. **安全性** - 遵循安全规范和最佳实践

## 强制执行规则 [CHECK:DEV-006] [CHECK:DEV-007] [CHECK:DEV-008]

### ❌ 严格禁止
- 为通过测试而简化业务逻辑
- 跳过必要的数据验证
- 硬编码配置信息  
- 忽略错误处理
- 不更新相关文档

### ✅ 强制执行
- 完整的字段验证和业务逻辑实现
- 完整的错误处理和测试覆盖
- 及时更新文档和状态记录

### 数据库操作规范 [CHECK:DEV-002] [CHECK:DEV-007]
**必须包含**:
- 数据验证和唯一性检查
- 完整事务处理（提交/回滚）
- 异常处理和错误日志
- 数据库连接管理

### API设计规范 [CHECK:DEV-004] [CHECK:DEV-006]
**必须包含**:
- 完整请求/响应模型定义
- 权限验证和安全检查
- 统一错误处理和状态码
- API文档字符串

> 详细实现示例参考：`docs/examples/api-database-examples.md` 【待创建】

## 问题处理流程 

### IF 开发问题 THEN 执行排查步骤
1. 检查日志 - 应用和数据库日志
2. 验证配置 - 环境变量和配置文件  
3. 测试连接 - 数据库和外部服务连接

### IF 测试失败 THEN 执行修复流程 [CHECK:TEST-006]
1. 分析失败原因和错误信息
2. 检查测试数据和业务逻辑 
3. 修复问题后重新运行测试

---

## 📝 第一期优化完成状态 

### ✅ 已完成优化
- **工具引用**: 全部标记为【待修正-工具验证】
- **检查点**: 已添加完整的[CHECK:XXX-XXX]标记系统
- **文档长度**: 从443行精简到233行 
- **结构优化**: 使用IF-THEN条件逻辑，命令式表述
- **内容外置**: 详细代码示例移至独立文件引用

### 🔄 待创建的外置文件
- `docs/examples/code-standards-examples.md` - 详细代码规范示例
- `docs/examples/testing-examples.md` - 完整测试用例示例  
- `docs/examples/api-database-examples.md` - API和数据库操作示例
- `docs/operations/release-procedures.md` - 详细发布操作流程

### 🚧 待第二期处理（工具验证后）
- 所有标记为【待修正-工具验证】的部分
- 脚本工具的准确引用和用法
- 自动化流程的完整配置

## 版本发布流程

### 开发版本发布 【待修正-工具验证】
<!--
TOOL-REFERENCE-PENDING: 需要验证release_to_main.ps1脚本状态
原内容：自动化发布流程
修正计划：确认发布工具后重新编写此部分
-->
**临时方案**: 手动合并到主分支并进行发布前验证

### 版本发布规范 [CHECK:STATUS-004]
**发布流程**:
1. 创建版本标签：`git tag -a v1.x.x -m "Release description"`
2. 推送标签：`git push origin v1.x.x` 
3. 验证核心功能正常
4. 更新状态文档记录发布信息

> 详细发布流程参考：`docs/operations/release-procedures.md`
