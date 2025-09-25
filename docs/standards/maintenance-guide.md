<!--version info: v1.0.0, created: 2025-09-23, level: L3, dependencies: standards-master-index.md-->

# 标准文档维护手册 (Standards Maintenance Guide)

## 概述

本手册定义标准文档体系的维护流程、更新机制和质量保证体系，确保L0-L1-L2架构的长期一致性和权威性。

## 依赖标准

本手册依赖以下标准文档和工具：
- `standards-master-index.md` - L0导航层总索引
- `validate_standards.ps1` - Phase 3.1自动化验证工具（核心验证）
- `maintain_standards.ps1` - Phase 3.3综合维护工具（维护操作）

## 维护机制总览

### 🔄 维护周期

| 维护类型 | 频率 | 触发条件 | 负责人 | 验证工具 |
|----------|------|----------|--------|----------|
| **日常验证** | 每次提交 | Git push/PR | 开发者 | validate_standards.ps1 |
| **结构审查** | 每周 | 定期检查 | 架构师 | CI/CD流水线 |
| **内容更新** | 按需 | 业务变更/技术升级 | 模块负责人 | 人工审查 |
| **架构重构** | 季度 | 重大变更 | 架构委员会 | ADR决策记录 |

### 📋 维护原则

1. **标准先行** - 所有变更必须先更新标准文档
2. **自动验证** - 依赖validate_standards.ps1进行质量门禁
3. **版本控制** - 每次变更必须更新版本信息头
4. **综合维护** - 使用maintain_standards.ps1进行系统性维护操作
5. **备份优先** - 重要变更前必须创建备份快照
4. **影响分析** - 评估对依赖文档的影响
5. **回归测试** - 变更后必须进行完整验证

## 维护流程详细说明

### 🔧 日常维护流程

#### 1. 标准文档修改流程

**触发条件**: 需要修改任何标准文档内容

**执行步骤**:
```powershell
# Step 1: 修改前验证
scripts/validate_standards.ps1 -Action full

# Step 2: 进行修改 (使用适当的工具/编辑器)

# Step 3: 更新版本信息头
# <!--version info: v1.x.x, created: YYYY-MM-DD, level: Lx, dependencies: ...-->

# Step 4: 修改后验证
scripts/validate_standards.ps1 -Action full

# Step 5: 提交变更 (仅在验证通过后)
git add docs/standards/
git commit -m "feat(standards): 更新XXX标准 - 原因说明"
```

#### 2. 新增标准文档流程

**触发条件**: 需要新增L2领域标准文档

**执行步骤**:
```powershell
# Step 1: 确定层级和依赖关系
# L2文档必须依赖L1核心标准

# Step 2: 使用标准模板创建文档
# 模板: docs/templates/l2-standard-template.md

# Step 3: 更新L0导航索引
# 在standards-master-index.md中添加新文档链接

# Step 4: 完整验证
scripts/validate_standards.ps1 -Action full

# Step 5: 更新相关README文档
# docs/README.md, 主README.md等
```

#### 3. 紧急修复流程 (DEV-009协议)

**触发条件**: 发现严重文档损坏或冲突

**执行步骤**:
```powershell
# Step 1: 启动DEV-009协议
scripts/ai_checkpoint.ps1 -CardType "DEV-009" -FilePath "文档路径"

# Step 2: 按DEV-009卡片执行
# 1) 备份现有文档
# 2) 强力删除+清理缓存  
# 3) 创建空文件
# 4) 逐行重建 (禁止复制粘贴)

# Step 3: 重建后验证
scripts/validate_standards.ps1 -Action full

# Step 4: 记录修复过程
# 在相关ADR或维护日志中记录
```

### 🏗️ 架构级维护

#### 1. L0-L1-L2架构完整性维护

**检查项目**:
- L0导航完整性 - 所有L1/L2文档都有入口链接
- L1权威性 - 不存在同级或下级文档定义相同规则
- L2依赖正确性 - 每个L2文档正确引用L1标准
- 循环依赖检测 - L2间不能相互引用

**维护命令**:
```powershell
# 依赖关系专项检查
scripts/validate_standards.ps1 -Action dependencies

# 重复内容专项检查  
scripts/validate_standards.ps1 -Action duplicate -Detailed
```

#### 2. 版本信息一致性维护

**标准格式**:
```html
<!--version info: v主版本.次版本.补丁版本, created: YYYY-MM-DD, level: L0/L1/L2, dependencies: 文件列表-->
```

**版本号规则**:
- **主版本**: 架构级变更 (L0-L1-L2结构调整)
- **次版本**: 内容重大更新 (新增章节、重构内容)  
- **补丁版本**: 细节修正 (错误修复、格式调整)

**维护命令**:
```powershell
# 格式一致性专项检查
scripts/validate_standards.ps1 -Action format
```

### 🔄 CI/CD集成

#### 1. GitHub Actions配置

创建 `.github/workflows/standards-validation.yml`:

```yaml
name: 标准文档验证

on:
  push:
    paths: ['docs/standards/**']
  pull_request:
    paths: ['docs/standards/**']

jobs:
  validate_standards:
    runs-on: ubuntu-latest
    
    steps:
    - name: 检出代码
      uses: actions/checkout@v3
      
    - name: 设置PowerShell环境
      uses: actions/setup-pwsh@v1
      
    - name: 完整标准验证
      run: |
        pwsh scripts/validate_standards.ps1 -Action full
      
    - name: 验证失败时上传报告
      if: failure()
      uses: actions/upload-artifact@v3
      with:
        name: standards-validation-report
        path: logs/standards-validation-*.log
```

#### 2. 质量门禁规则

```powershell
# 提交前钩子 (pre-commit hook)
# .git/hooks/pre-commit

#!/usr/bin/env pwsh
Write-Host "🔍 执行标准文档验证..." -ForegroundColor Yellow

$validationResult = & "scripts/validate_standards.ps1" -Action full
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 标准文档验证失败，提交被阻止" -ForegroundColor Red
    Write-Host "请运行: scripts/validate_standards.ps1 -Action full" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ 标准文档验证通过" -ForegroundColor Green
exit 0
```

### 📊 质量监控

#### 1. 定期质量报告

**月度报告内容**:
- 标准文档修改频率统计
- 验证工具发现的问题趋势
- 架构完整性评分
- 用户反馈和改进建议

**生成命令**:
```powershell
# 生成质量报告
scripts/generate_standards_report.ps1 -Period "monthly" -Output "docs/reports/"
```

#### 2. 问题跟踪

**问题分类**:
- **P0 - 严重**: 架构破坏、循环依赖、权威性冲突
- **P1 - 重要**: 内容缺失、格式不一致、依赖关系错误  
- **P2 - 一般**: 深层标题、代码块格式、文档优化

**处理流程**:
1. 自动检测 → validate_standards.ps1
2. 问题分类 → 根据影响程度分级
3. 修复计划 → 纳入开发迭代或紧急修复
4. 验证关闭 → 修复后重新验证

### 🔧 维护工具

#### 1. 标准文档模板

**L2标准文档模板** (`docs/templates/l2-standard-template.md`):
```markdown
<!--version info: v1.0.0, created: YYYY-MM-DD, level: L2, dependencies: naming-conventions-standards.md,project-structure-standards.md-->

# 【领域名称】标准规范 (【英文名称】 Standards)

## 概述

本文档定义【具体领域】的具体标准，属于L2领域标准。

## 依赖标准

本标准依赖以下L1核心标准：
- `naming-conventions-standards.md` - 【具体引用的命名规范】
- `project-structure-standards.md` - 【具体引用的结构标准】

## 具体标准

### 【主要标准章节1】

### 【主要标准章节2】

### 维护

本标准需要在以下情况更新：
1. 【更新触发条件1】
2. 【更新触发条件2】

相关文件：
- `【相关实现文件1】`
- `【相关实现文件2】`
```

#### 2. 自动化维护脚本

**a) validate_standards.ps1 - 核心验证工具**
```powershell
# 完整验证
scripts/validate_standards.ps1 -Action full

# 分项验证
scripts/validate_standards.ps1 -Action format      # 格式验证
scripts/validate_standards.ps1 -Action content    # 内容验证
scripts/validate_standards.ps1 -Action dependencies # 依赖验证
scripts/validate_standards.ps1 -Action duplicate    # 重复内容检查

# 单文档验证
scripts/validate_standards.ps1 -Action full -DocPath "docs/standards/naming-conventions-standards.md"
```

**b) maintain_standards.ps1 - 综合维护工具**
```powershell
# 健康检查（推荐：每日使用）
scripts/maintain_standards.ps1 -Action check

# 版本管理
scripts/maintain_standards.ps1 -Action update -Target version     # 批量更新版本头
scripts/maintain_standards.ps1 -Action update -Target content    # 内容时效性检查
scripts/maintain_standards.ps1 -Action update -Target all        # 全面更新

# 报告生成  
scripts/maintain_standards.ps1 -Action report -Target summary    # 摘要报告
scripts/maintain_standards.ps1 -Action report -Target detailed   # 详细报告
scripts/maintain_standards.ps1 -Action report -Target metrics    # 质量指标报告

# 备份管理
scripts/maintain_standards.ps1 -Action backup -Target "milestone-v1.0"  # 创建备份
scripts/maintain_standards.ps1 -Action restore -Target "milestone-v1.0" # 恢复备份
scripts/maintain_standards.ps1 -Action restore                          # 查看可用备份
```

**c) 维护脚本组合使用**
```powershell
# 日常维护（每天）
scripts/maintain_standards.ps1 -Action check

# 周度维护（每周一）  
scripts/maintain_standards.ps1 -Action report -Target summary
scripts/maintain_standards.ps1 -Action update -Target version

# 季度维护（每季度）
scripts/maintain_standards.ps1 -Action backup -Target "quarterly-$(Get-Date -Format 'yyyyQq')"
scripts/maintain_standards.ps1 -Action report -Target detailed

# 发版前维护
scripts/validate_standards.ps1 -Action full
scripts/maintain_standards.ps1 -Action backup -Target "release-v$(Get-Date -Format 'yyyyMMdd')"
        # 扫描并更新所有过时的版本信息
    }
    "report" { 
        # 生成维护状态报告
        # 统计文档修改频率、问题类型分布
    }
    "backup" { 
        # 创建标准文档快照备份
        # 压缩存档到 backups/standards/
    }
}
```

### 📝 变更控制

#### 1. 变更类型分级

| 变更级别 | 描述 | 审批流程 | 验证要求 | 回滚计划 |
|----------|------|----------|----------|----------|
| **架构级** | L0-L1-L2结构调整 | 架构委员会 + ADR | 完整回归 | 支持快速回滚 |
| **标准级** | L1/L2内容重大更新 | 技术负责人 | 影响分析 + 验证 | 版本回退 |
| **细节级** | 格式调整、错误修复 | 开发者 | 自动验证通过 | Git撤销 |

#### 2. 影响分析模板

```markdown
# 标准文档变更影响分析

## 变更概述
- **变更文档**: 
- **变更类型**: [架构级/标准级/细节级]
- **变更原因**: 

## 影响评估
- **直接影响**: 哪些文档需要同步更新
- **间接影响**: 哪些实现代码可能需要调整  
- **用户影响**: 开发者工作流程是否变化

## 验证计划
- [ ] validate_standards.ps1 -Action full
- [ ] 相关模块测试验证
- [ ] 文档链接完整性检查

## 回滚方案
- **回滚触发条件**: 
- **回滚步骤**: 
- **回滚验证**: 
```

### 🎯 成功指标

#### 1. 质量指标

- **验证通过率**: ≥ 95% (目标100%)
- **重复内容率**: = 0%
- **依赖关系完整性**: = 100%
- **格式一致性**: ≥ 95%

#### 2. 维护效率指标  

- **问题发现时间**: ≤ 1天 (自动检测)
- **问题修复时间**: ≤ 3天 (P0), ≤ 1周 (P1), ≤ 1月 (P2)
- **文档更新及时性**: ≤ 1天 (代码变更后)

#### 3. 用户满意度指标

- **查找效率**: 通过L0导航≤30秒找到目标标准
- **准确性**: 标准文档与实际实现一致性≥98%
- **可用性**: 开发者反馈标准文档有用性≥90%

## 维护责任分工

### 角色定义

| 角色 | 责任范围 | 维护任务 |
|------|----------|----------|
| **架构师** | L0-L1-L2整体架构 | 架构完整性、重大变更审批 |
| **技术负责人** | L1核心标准 | 权威性维护、冲突解决 |
| **模块负责人** | 相关L2领域标准 | 专业内容更新、实现一致性 |
| **开发者** | 日常使用和反馈 | 问题发现、细节修正 |

### 联系方式

- **架构问题**: 通过ADR流程或架构评审会议
- **标准冲突**: 技术负责人邮件或即时通讯
- **工具问题**: GitHub Issues或内部问题跟踪系统
- **紧急问题**: 通过DEV-009协议快速响应

## 附录

### A. 常见维护场景

1. **新增业务模块** → 评估是否需要新L2标准
2. **技术栈升级** → 更新相关L2技术标准  
3. **架构重构** → 可能需要L1标准调整
4. **工具链变更** → 更新脚本和验证工具

### B. 故障排除指南

1. **验证脚本失败** → 检查PowerShell版本和权限
2. **依赖关系错误** → 检查L2文档的L1引用
3. **格式不一致** → 检查版本信息头格式
4. **重复内容警告** → 检查是否有实质性重复

### C. 相关资源

- [validate_standards.ps1使用手册](../tools/scripts-usage-manual.md#validate_standards.ps1---标准文档验证-)
- [ADR-002架构重构决策](../architecture/ADR-002-standards-architecture-refactoring.md)
- [标准文档导航总索引](standards-master-index.md)
- [开发工具脚本总览](../../scripts/README.md)
