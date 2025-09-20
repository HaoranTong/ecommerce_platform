#!/usr/bin/env pwsh
<#
.SYNOPSIS
AI检查点辅助验证脚本

.DESCRIPTION
根据检查卡片类型执行对应的自动化验证，帮助AI快速准确地执行检查点要求。

.PARAMETER CardType
检查卡片类型 (DEV-001, DEV-002, DEV-003, TEST-001, TEST-002, DOC-001)

.PARAMETER ModuleName
模块名称 (如: inventory_management, user_auth等)

.PARAMETER FilePath
具体文件路径 (可选，用于精确检查)

.EXAMPLE
scripts/ai_checkpoint.ps1 -CardType DEV-001 -ModuleName inventory_management
scripts/ai_checkpoint.ps1 -CardType TEST-001 -FilePath "tests/unit/test_models/test_inventory.py"
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet(
        "REQ-001", "REQ-002", "REQ-003",
        "ARCH-001", "ARCH-002", "ARCH-003", 
        "DEV-001", "DEV-002", "DEV-003", "DEV-004", "DEV-005", "DEV-006", "DEV-007", "DEV-008", "DEV-009",
        "TEST-001", "TEST-002", "TEST-003", "TEST-004", "TEST-005", "TEST-006",
        "DOC-001", "DOC-002", "DOC-003", "DOC-004", "DOC-005", "DOC-006"
    )]
    [string]$CardType,
    
    [string]$ModuleName = "",
    [string]$FilePath = "",
    [string]$TestLevel = "basic",
    [string]$DirectoryPath = ""
)

Write-Host "🔍 执行检查卡片: $CardType" -ForegroundColor Cyan
Write-Host "=" * 50

# 检查点卡片路由函数
function Invoke-CheckpointCard {
    param($CardType, $ModuleName, $FilePath, $TestLevel)
    
    switch ($CardType) {
        # 需求分析类 (REQ)
        "REQ-001" { Test-BusinessRequirements $ModuleName }
        "REQ-002" { Test-FunctionalRequirements $ModuleName }
        "REQ-003" { Test-NonFunctionalRequirements $ModuleName }
        
        # 架构设计类 (ARCH)  
        "ARCH-001" { Test-SystemArchitecture $ModuleName }
        "ARCH-002" { Test-ModuleArchitecture $ModuleName }
        "ARCH-003" { Test-DataArchitecture $ModuleName }
        
        # 开发实施类 (DEV)
        "DEV-001" { Test-ModuleDocumentation $ModuleName }
        "DEV-002" { Test-EnvironmentSetup $ModuleName }
        "DEV-003" { Test-DataModelImplementation $ModuleName $FilePath }
        "DEV-004" { Test-APIRouteImplementation $ModuleName $FilePath }
        "DEV-005" { Test-BusinessLogicImplementation $ModuleName $FilePath }
        "DEV-006" { Test-SecurityImplementation $ModuleName $FilePath }
        "DEV-007" { Test-ErrorHandlingImplementation $ModuleName $FilePath }
        "DEV-008" { Test-CodeQuality $ModuleName $FilePath }
        "DEV-009" { Test-CodeStandards $ModuleName $FilePath }
        
        # 测试验证类 (TEST)
        "TEST-001" { Test-TestEnvironment $ModuleName }
        "TEST-002" { Test-UnitTests $ModuleName $FilePath }
        "TEST-003" { Test-IntegrationTests $ModuleName $FilePath }
        "TEST-004" { Test-APITests $ModuleName $FilePath }
        "TEST-005" { Test-PerformanceTests $ModuleName $TestLevel }
        "TEST-006" { Test-SecurityTests $ModuleName $TestLevel }
        
        # 文档同步类 (DOC)
        "DOC-001" { Test-CodeDocumentation $ModuleName $FilePath }
        "DOC-002" { Test-APIDocumentation $ModuleName }
        "DOC-003" { Test-ArchitectureDocumentation $ModuleName }
        "DOC-004" { Test-DeploymentDocumentation $ModuleName }
        "DOC-005" { Test-DocumentSync $DirectoryPath }
        "DOC-006" { Test-ToolDocumentation $FilePath }
        
        default {
            Write-Host "⚠️  检查卡片 $CardType 尚未实现" -ForegroundColor Yellow
            Write-Host "📖 请手动执行 docs/standards/checkpoint-cards.md 中的检查步骤" -ForegroundColor Cyan
        }
    }
}

# 需求分析检查函数
function Test-BusinessRequirements($ModuleName) {
    Write-Host "📋 业务需求理解验证 - $ModuleName" -ForegroundColor Yellow
    
    $RequirementsDoc = "docs/requirements/business.md"
    if (Test-Path $RequirementsDoc) {
        $Content = Get-Content $RequirementsDoc -Raw
        if ($Content -match $ModuleName) {
            Write-Host "✅ 业务需求文档包含模块 $ModuleName" -ForegroundColor Green
        } else {
            Write-Host "❌ 业务需求文档缺少模块 $ModuleName" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ 业务需求文档不存在" -ForegroundColor Red
    }
}

function Test-FunctionalRequirements($ModuleName) {
    Write-Host "📋 功能需求分析验证 - $ModuleName" -ForegroundColor Yellow
    
    $ModuleDoc = "docs/modules/$ModuleName/README.md"
    if (Test-Path $ModuleDoc) {
        Write-Host "✅ 模块文档存在: $ModuleDoc" -ForegroundColor Green
        
        $Content = Get-Content $ModuleDoc -Raw
        $RequiredSections = @("功能概述", "API接口", "数据模型", "业务流程")
        
        foreach ($Section in $RequiredSections) {
            if ($Content -match $Section) {
                Write-Host "   ✅ 包含 $Section 章节" -ForegroundColor Green
            } else {
                Write-Host "   ❌ 缺少 $Section 章节" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "❌ 模块文档不存在: $ModuleDoc" -ForegroundColor Red
    }
}

function Test-NonFunctionalRequirements($ModuleName) {
    Write-Host "📋 非功能需求确认 - $ModuleName" -ForegroundColor Yellow
    
    $NFRDoc = "docs/requirements/non-functional.md"
    if (Test-Path $NFRDoc) {
        $Content = Get-Content $NFRDoc -Raw
        $NFRItems = @("性能要求", "安全要求", "可维护性", "监控需求")
        
        foreach ($Item in $NFRItems) {
            if ($Content -match $Item) {
                Write-Host "   ✅ 已定义 $Item" -ForegroundColor Green
            } else {
                Write-Host "   ❌ 缺少 $Item 定义" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "❌ 非功能需求文档不存在: $NFRDoc" -ForegroundColor Red
    }
}

# 架构设计检查函数  
function Test-SystemArchitecture($ModuleName) {
    Write-Host "📋 系统架构设计验证 - $ModuleName" -ForegroundColor Yellow
    
    $ArchDoc = "docs/architecture/overview.md"
    if (Test-Path $ArchDoc) {
        Write-Host "✅ 系统架构文档存在" -ForegroundColor Green
    } else {
        Write-Host "❌ 系统架构文档不存在" -ForegroundColor Red
    }
}

function Test-ModuleArchitecture($ModuleName) {
    Write-Host "📋 模块架构设计验证 - $ModuleName" -ForegroundColor Yellow
    
    $ModuleArchDoc = "docs/architecture/module-architecture.md"
    if (Test-Path $ModuleArchDoc) {
        $Content = Get-Content $ModuleArchDoc -Raw
        if ($Content -match $ModuleName) {
            Write-Host "✅ 模块架构设计已定义" -ForegroundColor Green
        } else {
            Write-Host "❌ 缺少模块 $ModuleName 的架构设计" -ForegroundColor Red
        }
    }
}

function Test-DataArchitecture($ModuleName) {
    Write-Host "📋 数据架构设计验证 - $ModuleName" -ForegroundColor Yellow
    
    $DataArchDoc = "docs/architecture/data-models.md"
    $ModelsFile = "app/modules/$ModuleName/models.py"
    
    if ((Test-Path $DataArchDoc) -and (Test-Path $ModelsFile)) {
        Write-Host "✅ 数据架构文档和模型文件都存在" -ForegroundColor Green
        
        # 检查模型实体关系
        $ModelsContent = Get-Content $ModelsFile -Raw
        $Relations = $ModelsContent -split "`n" | Select-String "relationship\(|ForeignKey\("
        
        if ($Relations) {
            Write-Host "✅ 发现数据关系定义 ($($Relations.Count) 个)" -ForegroundColor Green
        } else {
            Write-Host "⚠️  未发现明确的数据关系定义" -ForegroundColor Yellow
        }
    }
}

# 开发实施检查函数
function Test-ModuleDocumentation($ModuleName) {
    Write-Host "📋 模块文档完整性验证 - $ModuleName" -ForegroundColor Yellow
    
    $RequiredDocs = @(
        "docs/modules/$ModuleName/README.md",
        "docs/modules/$ModuleName/api-spec.md"
    )
    
    foreach ($Doc in $RequiredDocs) {
        if (Test-Path $Doc) {
            Write-Host "   ✅ $Doc" -ForegroundColor Green
        } else {
            Write-Host "   ❌ 缺少: $Doc" -ForegroundColor Red
        }
    }
}

function Test-EnvironmentSetup($ModuleName) {
    Write-Host "📋 环境与工具准备验证 - $ModuleName" -ForegroundColor Yellow
    
    $EnvFiles = @("requirements.txt", "docker-compose.yml", ".env.example")
    
    foreach ($File in $EnvFiles) {
        if (Test-Path $File) {
            Write-Host "   ✅ $File" -ForegroundColor Green
        } else {
            Write-Host "   ❌ 缺少: $File" -ForegroundColor Red
        }
    }
}

function Test-DataModelImplementation($ModuleName, $FilePath) {
    Write-Host "📋 数据模型实现验证 - $ModuleName" -ForegroundColor Yellow
    
    $ModelFile = if ($FilePath) { $FilePath } else { "app/modules/$ModuleName/models.py" }
    
    if (Test-Path $ModelFile) {
        Write-Host "📄 检查文件: $ModelFile" -ForegroundColor Gray
        
        $Content = Get-Content $ModelFile -Raw
        
        # 检查基础模型继承
        if ($Content -match "Base|DeclarativeBase") {
            Write-Host "   ✅ 使用正确的基础模型" -ForegroundColor Green
        } else {
            Write-Host "   ❌ 未使用标准基础模型" -ForegroundColor Red
        }
        
        # 检查字段类型规范
        $IntegerIds = $Content -split "`n" | Select-String "Column\(Integer.*ForeignKey|.*_id\s*=\s*Column\(Integer"
        if ($IntegerIds) {
            Write-Host "   ✅ Integer ID字段: $($IntegerIds.Count) 个" -ForegroundColor Green
        }
        
        # 检查模型一致性
        $StringIdUsage = $Content -split "`n" | Select-String 'id.*=.*["''].*["'']'
        if ($StringIdUsage) {
            Write-Host "   ❌ 发现字符串ID使用，应使用Integer" -ForegroundColor Red
        } else {
            Write-Host "   ✅ 数据类型使用一致" -ForegroundColor Green
        }
        
    } else {
        Write-Host "❌ 模型文件不存在: $ModelFile" -ForegroundColor Red
    }
}

function Test-APIRouteImplementation($ModuleName, $FilePath) {
    Write-Host "📋 API路由实现验证 - $ModuleName" -ForegroundColor Yellow
    
    $RouteFile = if ($FilePath) { $FilePath } else { "app/modules/$ModuleName/routes.py" }
    
    if (Test-Path $RouteFile) {
        $Content = Get-Content $RouteFile -Raw
        
        # 检查路由注册
        if ($Content -match "APIRouter|@router") {
            Write-Host "   ✅ 使用标准路由器" -ForegroundColor Green
        } else {
            Write-Host "   ❌ 未使用标准路由器模式" -ForegroundColor Red
        }
        
        # 检查HTTP方法覆盖
        $Methods = @("GET", "POST", "PUT", "DELETE")
        foreach ($Method in $Methods) {
            if ($Content -match "@router\.$($Method.ToLower())|@$($Method.ToLower())") {
                Write-Host "   ✅ 包含 $Method 接口" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "❌ 路由文件不存在: $RouteFile" -ForegroundColor Red
    }
}

function Test-BusinessLogicImplementation($ModuleName, $FilePath) {
    Write-Host "📋 业务逻辑实现验证 - $ModuleName" -ForegroundColor Yellow
    
    $ServiceFile = if ($FilePath) { $FilePath } else { "app/modules/$ModuleName/service.py" }
    
    if (Test-Path $ServiceFile) {
        $Content = Get-Content $ServiceFile -Raw
        
        # 检查业务逻辑分层
        if ($Content -match "class.*Service|def.*_service") {
            Write-Host "   ✅ 使用服务层模式" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  建议使用服务层模式组织业务逻辑" -ForegroundColor Yellow
        }
        
        # 检查异常处理
        if ($Content -match "try:|except|raise") {
            Write-Host "   ✅ 包含异常处理" -ForegroundColor Green
        } else {
            Write-Host "   ❌ 缺少异常处理机制" -ForegroundColor Red
        }
    }
}

function Test-SecurityImplementation($ModuleName, $FilePath) {
    Write-Host "📋 安全控制实现验证 - $ModuleName" -ForegroundColor Yellow
    
    $ModuleFiles = Get-ChildItem "app/modules/$ModuleName" -Filter "*.py" -Recurse
    
    $SecurityPatterns = @(
        @{Pattern="Depends.*get_current_user"; Name="身份认证"},
        @{Pattern="HTTPException.*401|403"; Name="授权检查"},
        @{Pattern="validate|pydantic"; Name="输入验证"},
        @{Pattern="hash|bcrypt|passlib"; Name="密码加密"}
    )
    
    foreach ($File in $ModuleFiles) {
        $Content = Get-Content $File.FullName -Raw
        foreach ($Security in $SecurityPatterns) {
            if ($Content -match $Security.Pattern) {
                Write-Host "   ✅ $($File.Name): $($Security.Name)" -ForegroundColor Green
            }
        }
    }
}

function Test-ErrorHandlingImplementation($ModuleName, $FilePath) {
    Write-Host "📋 错误处理实现验证 - $ModuleName" -ForegroundColor Yellow
    
    $ModuleFiles = Get-ChildItem "app/modules/$ModuleName" -Filter "*.py" -Recurse
    
    foreach ($File in $ModuleFiles) {
        $Content = Get-Content $File.FullName -Raw
        
        # 检查异常处理覆盖
        $TryBlocks = ($Content -split "`n" | Select-String "try:").Count
        $ExceptBlocks = ($Content -split "`n" | Select-String "except").Count
        
        if ($TryBlocks -gt 0 -and $ExceptBlocks -gt 0) {
            Write-Host "   ✅ $($File.Name): 异常处理 ($TryBlocks try, $ExceptBlocks except)" -ForegroundColor Green
        } elseif ($Content.Length -gt 100) {
            Write-Host "   ⚠️  $($File.Name): 建议添加异常处理" -ForegroundColor Yellow
        }
    }
}

function Test-CodeQuality($ModuleName, $FilePath) {
    Write-Host "📋 代码质量验证 - $ModuleName" -ForegroundColor Yellow
    
    # 检查代码格式化
    Write-Host "🔍 检查代码格式化..." -ForegroundColor Cyan
    $BlackResult = & python -m black --check "app/modules/$ModuleName" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ 代码格式化正确" -ForegroundColor Green
    } else {
        Write-Host "   ❌ 代码格式需要调整" -ForegroundColor Red
        if ($BlackResult) { Write-Host "      详情: $BlackResult" -ForegroundColor Gray }
    }
    
    # 检查导入排序
    Write-Host "🔍 检查导入排序..." -ForegroundColor Cyan
    $IsortResult = & python -m isort --check-only "app/modules/$ModuleName" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ 导入排序正确" -ForegroundColor Green
    } else {
        Write-Host "   ❌ 导入排序需要调整" -ForegroundColor Red
        if ($IsortResult) { Write-Host "      详情: $IsortResult" -ForegroundColor Gray }
    }
}

# 测试验证检查函数
function Test-TestEnvironment($ModuleName) {
    Write-Host "📋 测试环境配置验证 - $ModuleName" -ForegroundColor Yellow
    
    $TestConfigs = @("conftest.py", "tests/conftest.py", "tests/conftest_standalone.py")
    
    foreach ($Config in $TestConfigs) {
        if (Test-Path $Config) {
            Write-Host "   ✅ 测试配置: $Config" -ForegroundColor Green
        }
    }
    
    # 检查测试数据库配置
    if (Test-Path "tests") {
        Write-Host "   ✅ 测试目录存在" -ForegroundColor Green
    } else {
        Write-Host "   ❌ 测试目录不存在" -ForegroundColor Red
    }
}

function Test-UnitTests($ModuleName, $FilePath) {
    Write-Host "📋 单元测试验证 - $ModuleName" -ForegroundColor Yellow
    
    $TestPattern = "tests/**/test_*$ModuleName*.py"
    $TestFiles = Get-ChildItem $TestPattern -Recurse -ErrorAction SilentlyContinue
    
    if ($TestFiles) {
        Write-Host "   ✅ 发现单元测试: $($TestFiles.Count) 个文件" -ForegroundColor Green
        foreach ($File in $TestFiles) {
            $Content = Get-Content $File.FullName -Raw
            $TestCount = ($Content -split "`n" | Select-String "def test_").Count
            Write-Host "      $($File.Name): $TestCount 个测试用例" -ForegroundColor Gray
        }
    } else {
        Write-Host "   ❌ 未发现单元测试文件" -ForegroundColor Red
    }
}

function Test-IntegrationTests($ModuleName, $FilePath) {
    Write-Host "📋 集成测试验证 - $ModuleName" -ForegroundColor Yellow
    
    $IntegrationPath = "tests/integration"
    if (Test-Path $IntegrationPath) {
        $TestFiles = Get-ChildItem "$IntegrationPath/*$ModuleName*" -ErrorAction SilentlyContinue
        if ($TestFiles) {
            Write-Host "   ✅ 发现集成测试: $($TestFiles.Count) 个" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  建议添加集成测试" -ForegroundColor Yellow
        }
    }
}

function Test-APITests($ModuleName, $FilePath) {
    Write-Host "📋 API测试验证 - $ModuleName" -ForegroundColor Yellow
    
    $APITestFiles = Get-ChildItem "tests" -Filter "*api*" -Recurse -ErrorAction SilentlyContinue
    
    if ($APITestFiles) {
        Write-Host "   ✅ 发现API测试文件" -ForegroundColor Green
        foreach ($File in $APITestFiles) {
            $Content = Get-Content $File.FullName -Raw
            if ($Content -match $ModuleName) {
                Write-Host "      ✅ $($File.Name) 包含模块测试" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "   ❌ 未发现API测试文件" -ForegroundColor Red
    }
}

function Test-PerformanceTests($ModuleName, $TestLevel) {
    Write-Host "📋 性能测试验证 - $ModuleName ($TestLevel)" -ForegroundColor Yellow
    
    $PerfPath = "tests/performance"
    if (Test-Path $PerfPath) {
        Write-Host "   ✅ 性能测试目录存在" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  建议创建性能测试: $PerfPath" -ForegroundColor Yellow
    }
}

function Test-SecurityTests($ModuleName, $TestLevel) {
    Write-Host "📋 安全测试验证 - $ModuleName ($TestLevel)" -ForegroundColor Yellow
    
    $SecPath = "tests/security"
    if (Test-Path $SecPath) {
        Write-Host "   ✅ 安全测试目录存在" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  建议创建安全测试: $SecPath" -ForegroundColor Yellow
    }
}

# 文档同步检查函数
function Test-CodeDocumentation($ModuleName, $FilePath) {
    Write-Host "📋 代码文档同步验证 - $ModuleName" -ForegroundColor Yellow
    
    $ModuleFiles = Get-ChildItem "app/modules/$ModuleName" -Filter "*.py" -Recurse
    
    foreach ($File in $ModuleFiles) {
        $Content = Get-Content $File.FullName -Raw
        
        # 检查docstring覆盖
        $Functions = ($Content -split "`n" | Select-String "def ").Count
        $Docstrings = ($Content -split "`n" | Select-String '"""').Count / 2
        
        if ($Functions -gt 0) {
            $CoveragePercent = [Math]::Round(($Docstrings / $Functions) * 100, 1)
            if ($CoveragePercent -ge 80) {
                Write-Host "   ✅ $($File.Name): 文档覆盖率 $CoveragePercent%" -ForegroundColor Green
            } else {
                Write-Host "   ❌ $($File.Name): 文档覆盖率 $CoveragePercent% (需要≥80%)" -ForegroundColor Red
            }
        }
    }
}

function Test-APIDocumentation($ModuleName) {
    Write-Host "📋 API文档更新验证 - $ModuleName" -ForegroundColor Yellow
    
    $APIDoc = "docs/modules/$ModuleName/api-spec.md"
    if (Test-Path $APIDoc) {
        Write-Host "   ✅ API文档存在: $APIDoc" -ForegroundColor Green
    } else {
        Write-Host "   ❌ API文档不存在: $APIDoc" -ForegroundColor Red
    }
}

function Test-ArchitectureDocumentation($ModuleName) {
    Write-Host "📋 架构文档维护验证 - $ModuleName" -ForegroundColor Yellow
    
    $ArchDocs = @(
        "docs/architecture/system-architecture.md",
        "docs/architecture/module-architecture.md"
    )
    
    foreach ($Doc in $ArchDocs) {
        if (Test-Path $Doc) {
            $Content = Get-Content $Doc -Raw
            if ($Content -match $ModuleName) {
                Write-Host "   ✅ $Doc 包含模块信息" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️  $Doc 建议添加模块信息" -ForegroundColor Yellow
            }
        }
    }
}

function Test-DeploymentDocumentation($ModuleName) {
    Write-Host "📋 部署文档完善验证 - $ModuleName" -ForegroundColor Yellow
    
    $DeployDocs = @(
        "docs/operations/deployment-guide.md",
        "docker-compose.yml",
        "README.md"
    )
    
    foreach ($Doc in $DeployDocs) {
        if (Test-Path $Doc) {
            Write-Host "   ✅ 部署文档: $Doc" -ForegroundColor Green
        } else {
            Write-Host "   ❌ 缺少部署文档: $Doc" -ForegroundColor Red
        }
    }
}

# 新增检查函数
function Test-CodeStandards($ModuleName, $FilePath) {
    Write-Host "📋 代码规范完备性验证 - $ModuleName" -ForegroundColor Yellow
    
    $CheckFiles = @()
    
    if ($FilePath) {
        $CheckFiles += $FilePath
    } elseif ($ModuleName) {
        $CheckFiles = Get-ChildItem "app/modules/$ModuleName" -Filter "*.py" -Recurse
    } else {
        Write-Host "❌ 需要指定文件路径或模块名" -ForegroundColor Red
        return
    }
    
    foreach ($File in $CheckFiles) {
        $FullPath = if ($FilePath) { $File } else { $File.FullName }
        Write-Host "📄 检查文件: $FullPath" -ForegroundColor Gray
        
        if (Test-Path $FullPath) {
            $Content = Get-Content $FullPath -Raw
            
            # 检查文件头部文档
            if ($FullPath -match "\.py$") {
                if ($Content -match '^\s*"""[\s\S]*?"""') {
                    Write-Host "   ✅ Python文件头部文档存在" -ForegroundColor Green
                } else {
                    Write-Host "   ❌ 缺少Python文件头部docstring" -ForegroundColor Red
                }
            } elseif ($FullPath -match "\.ps1$") {
                if ($Content -match '<#[\s\S]*?#>') {
                    Write-Host "   ✅ PowerShell文件头部注释存在" -ForegroundColor Green
                } else {
                    Write-Host "   ❌ 缺少PowerShell文件头部注释块" -ForegroundColor Red
                }
            }
            
            # 检查函数文档覆盖
            $Functions = ($Content -split "`n" | Select-String "def |function ").Count
            $Docstrings = ($Content -split "`n" | Select-String '"""|\<#').Count
            
            if ($Functions -gt 0) {
                $DocCoverage = [Math]::Round(($Docstrings / $Functions) * 100, 1)
                if ($DocCoverage -ge 90) {
                    Write-Host "   ✅ 函数文档覆盖率: $DocCoverage%" -ForegroundColor Green
                } else {
                    Write-Host "   ❌ 函数文档覆盖率: $DocCoverage% (需要≥90%)" -ForegroundColor Red
                }
            }
            
            # 检查注释密度
            $CodeLines = ($Content -split "`n" | Where-Object { $_.Trim() -and $_ -notmatch '^\s*#' }).Count
            $CommentLines = ($Content -split "`n" | Select-String '^\s*#').Count
            
            if ($CodeLines -gt 0) {
                $CommentRatio = [Math]::Round(($CommentLines / $CodeLines) * 100, 1)
                if ($CommentRatio -ge 15) {
                    Write-Host "   ✅ 注释密度: $CommentRatio%" -ForegroundColor Green
                } else {
                    Write-Host "   ⚠️  注释密度: $CommentRatio% (建议≥15%)" -ForegroundColor Yellow
                }
            }
        }
    }
}

function Test-DocumentSync($DirectoryPath) {
    Write-Host "📋 文档目录同步验证 - $DirectoryPath" -ForegroundColor Yellow
    
    if (-not $DirectoryPath) {
        $DirectoryPath = "."
    }
    
    if (Test-Path $DirectoryPath) {
        # 检查README.md存在性
        $ReadmePath = Join-Path $DirectoryPath "README.md"
        if (Test-Path $ReadmePath) {
            Write-Host "   ✅ README.md存在: $ReadmePath" -ForegroundColor Green
            
            # 检查README内容完整性
            $ReadmeContent = Get-Content $ReadmePath -Raw
            $Files = Get-ChildItem $DirectoryPath -File | Where-Object { $_.Name -ne "README.md" }
            
            $UndocumentedFiles = @()
            foreach ($File in $Files) {
                if ($ReadmeContent -notmatch [Regex]::Escape($File.Name)) {
                    $UndocumentedFiles += $File.Name
                }
            }
            
            if ($UndocumentedFiles.Count -eq 0) {
                Write-Host "   ✅ 所有文件都在README中有说明" -ForegroundColor Green
            } else {
                Write-Host "   ❌ 未在README中说明的文件:" -ForegroundColor Red
                $UndocumentedFiles | ForEach-Object { Write-Host "      - $_" -ForegroundColor Red }
            }
        } else {
            Write-Host "   ❌ 缺少README.md文件: $DirectoryPath" -ForegroundColor Red
        }
        
        # 检查子目录README
        $SubDirs = Get-ChildItem $DirectoryPath -Directory
        foreach ($SubDir in $SubDirs) {
            $SubReadme = Join-Path $SubDir.FullName "README.md"
            if (Test-Path $SubReadme) {
                Write-Host "   ✅ 子目录README: $($SubDir.Name)" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️  子目录缺少README: $($SubDir.Name)" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "❌ 目录不存在: $DirectoryPath" -ForegroundColor Red
    }
}

function Test-ToolDocumentation($FilePath) {
    Write-Host "📋 工具文档完整性验证 - $FilePath" -ForegroundColor Yellow
    
    if (-not $FilePath) {
        Write-Host "❌ 需要指定工具文件路径" -ForegroundColor Red
        return
    }
    
    if (Test-Path $FilePath) {
        $Content = Get-Content $FilePath -Raw
        $FileName = Split-Path $FilePath -Leaf
        
        # 检查PowerShell帮助注释
        if ($FilePath -match "\.ps1$") {
            if ($Content -match '<#[\s\S]*?\.SYNOPSIS[\s\S]*?\.DESCRIPTION[\s\S]*?#>') {
                Write-Host "   ✅ 标准PowerShell帮助注释存在" -ForegroundColor Green
            } else {
                Write-Host "   ❌ 缺少标准PowerShell帮助注释" -ForegroundColor Red
            }
            
            # 检查参数文档
            if ($Content -match '\.PARAMETER') {
                Write-Host "   ✅ 参数说明存在" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️  建议添加参数说明" -ForegroundColor Yellow
            }
            
            # 检查使用示例
            if ($Content -match '\.EXAMPLE') {
                Write-Host "   ✅ 使用示例存在" -ForegroundColor Green
            } else {
                Write-Host "   ❌ 缺少使用示例" -ForegroundColor Red
            }
        }
        
        # 检查scripts/README.md更新
        $ScriptsReadme = "scripts/README.md"
        if (Test-Path $ScriptsReadme) {
            $ReadmeContent = Get-Content $ScriptsReadme -Raw
            if ($ReadmeContent -match [Regex]::Escape($FileName)) {
                Write-Host "   ✅ 工具已在scripts/README.md中说明" -ForegroundColor Green
            } else {
                Write-Host "   ❌ 需要在scripts/README.md中添加工具说明" -ForegroundColor Red
            }
        }
        
        # 检查MASTER.md引用
        if (Test-Path "MASTER.md") {
            $MasterContent = Get-Content "MASTER.md" -Raw
            if ($MasterContent -match [Regex]::Escape($FileName)) {
                Write-Host "   ✅ 工具已在MASTER.md中引用" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️  建议在MASTER.md中添加工具引用" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "❌ 工具文件不存在: $FilePath" -ForegroundColor Red
    }
}

# 执行主检查流程
Invoke-CheckpointCard -CardType $CardType -ModuleName $ModuleName -FilePath $FilePath -TestLevel $TestLevel

Write-Host "=" * 50
Write-Host "🎉 检查卡片 $CardType 执行完成" -ForegroundColor Green