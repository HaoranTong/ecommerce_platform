<#
.SYNOPSIS
    命名规范合规性检查脚本
    
.DESCRIPTION
    此脚本用于检查代码仓库的命名规范合规性，完全符合 docs/standards/naming-conventions-standards.md 标准。
    支持检查 API路径、数据库表/字段、文档目录、代码文件的命名规范。
    
.PARAMETER CheckType
    检查类型，可选值: all, api, database, docs, code
    - all: 检查所有类型（默认）
    - api: 仅检查API路径命名
    - database: 仅检查数据库表/字段命名
    - docs: 仅检查文档目录/文件命名
    - code: 仅检查代码文件/类/函数命名
    
.PARAMETER DocsPath
    文档目录路径，默认为 "docs/design/modules"
    可指定其他目录进行文档命名检查
    
.PARAMETER ModuleName
    指定模块名称（业务概念名），如 product-catalog
    如果指定，将自动调整DocsPath到该模块的设计文档目录
    
.PARAMETER CodePath
    代码目录路径，默认为 "app"
    可指定其他目录进行代码命名检查
    
.PARAMETER TargetPath
    目标检查路径，可以是文件或目录
    用于检查指定路径下的命名规范
    
.PARAMETER Fix
    是否尝试自动修复部分问题（暂未实现）
    
.PARAMETER Help
    显示帮助信息
    
.EXAMPLE
    .\check_naming_compliance.ps1
    执行完整的命名规范检查
    
.EXAMPLE
    .\check_naming_compliance.ps1 -CheckType api
    仅检查API路径命名规范
    
.EXAMPLE
    .\check_naming_compliance.ps1 -CheckType docs -DocsPath "docs/design/modules/product-catalog"
    检查指定模块的文档命名规范
    
.EXAMPLE
    .\check_naming_compliance.ps1 -CheckType code -CodePath "app/modules/user_auth"
    检查指定模块的代码命名规范
    
.EXAMPLE
    .\check_naming_compliance.ps1 -ModuleName "product-catalog"
    检查product-catalog模块的所有命名规范
    
.EXAMPLE
    .\check_naming_compliance.ps1 -TargetPath "app/modules/user_auth/models.py"
    检查指定文件的命名规范
    
.EXAMPLE
    .\check_naming_compliance.ps1 -Help
    显示详细帮助信息
    
.NOTES
    文件名: check_naming_compliance.ps1
    作者: GitHub Copilot
    版本: v2.0
    创建日期: 2025-10-09
    更新日期: 2025-10-09
    依赖标准: docs/standards/naming-conventions-standards.md
    
.LINK
    https://github.com/ecommerce_platform/docs/standards/naming-conventions-standards.md
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("all", "api", "database", "docs", "code")]
    [string]$CheckType = "all",
    
    [Parameter(Mandatory = $false)]
    [string]$DocsPath = "docs/design/modules",
    
    [Parameter(Mandatory = $false)]
    [string]$ModuleName = "",
    
    [Parameter(Mandatory = $false)]
    [string]$CodePath = "app",
    
    [Parameter(Mandatory = $false)]
    [string]$TargetPath = "",
    
    [Parameter(Mandatory = $false)]
    [switch]$Fix = $false,
    
    [Parameter(Mandatory = $false)]
    [switch]$Help = $false
)
# 显示帮助信息
if ($Help) {
    Write-Host @"
🔍 命名规范合规性检查工具 v2.0
===============================================

📋 功能说明：
此工具用于检查项目中各种实体的命名规范合规性，完全符合项目命名标准文档。

🎯 检查范围：
• API路径命名（RESTful端点、参数、HTTP方法）
• 数据库命名（表名、字段名、外键、索引）  
• 文档命名（目录结构、文件名、模块映射）
• 代码命名（类名、函数名、变量名、常量名）

⚙️ 参数说明：
-CheckType      检查类型 [all|api|database|docs|code]
-DocsPath       文档目录路径 (默认: docs/design/modules)
-ModuleName     指定模块名称 (如: product-catalog)
-CodePath       代码目录路径 (默认: app)
-TargetPath     指定检查的文件或目录路径
-Fix            尝试自动修复问题 (暂未实现)
-Help           显示此帮助信息

📝 使用示例：

基础检查：
  .\check_naming_compliance.ps1                    # 完整检查
  .\check_naming_compliance.ps1 -CheckType api    # 仅检查API

模块检查：
  .\check_naming_compliance.ps1 -ModuleName "product-catalog"
  .\check_naming_compliance.ps1 -CheckType docs -DocsPath "docs/design/modules/user-auth"

目录检查：
  .\check_naming_compliance.ps1 -CheckType code -CodePath "app/modules/user_auth"
  .\check_naming_compliance.ps1 -TargetPath "app/modules/product_catalog/models.py"

文档检查：
  .\check_naming_compliance.ps1 -CheckType docs -DocsPath "docs/api/modules"
  .\check_naming_compliance.ps1 -CheckType docs -TargetPath "docs/design/overview.md"

🔧 标准参考：
命名规范标准: docs/standards/naming-conventions-standards.md
API设计标准:  docs/standards/api-standards.md

📞 技术支持：
如遇问题，请查阅项目文档或联系开发团队。
"@ -ForegroundColor Cyan
    exit 0
}

# 路径处理和参数验证
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    
    switch ($Color) {
        "Red" { Write-Host $Message -ForegroundColor Red }
        "Green" { Write-Host $Message -ForegroundColor Green }
        "Yellow" { Write-Host $Message -ForegroundColor Yellow }
        "Blue" { Write-Host $Message -ForegroundColor Blue }
        "Cyan" { Write-Host $Message -ForegroundColor Cyan }
        default { Write-Host $Message }
    }
}

if ($TargetPath) {
    if (-not (Test-Path $TargetPath)) {
        Write-ColorOutput "❌ 指定的目标路径不存在: $TargetPath" "Red"
        exit 1
    }
    
    # 根据目标路径自动判断检查类型
    if ($CheckType -eq "all") {
        if ($TargetPath -like "*\.py") {
            $CheckType = "code"
            Write-ColorOutput "🎯 检测到Python文件，自动设置检查类型为: code" "Yellow"
        } elseif ($TargetPath -like "*docs*") {
            $CheckType = "docs"
            Write-ColorOutput "🎯 检测到文档路径，自动设置检查类型为: docs" "Yellow"
        } elseif ($TargetPath -like "*models.py" -or $TargetPath -like "*app*") {
            Write-ColorOutput "🎯 检测到应用代码路径，将进行综合检查" "Yellow"
        }
    }
}

# 根据 ModuleName 参数调整路径
if ($ModuleName) {
    # 这里将在配置加载后处理
    $ModuleNameToProcess = $ModuleName
} else {
    $TechModule = ""
    $ModuleNameToProcess = ""
}

$NamingConfig = @{
    # 模块标准映射 - 符合命名规范标准的完整映射表
    ModuleMappings = @{
        # 核心业务模块: 业务概念名 -> 技术实现名映射
        "user-auth" = "user_auth"
        "shopping-cart" = "shopping_cart"
        "product-catalog" = "product_catalog"
        "order-management" = "order_management"
        "payment-service" = "payment_service"
        "inventory-management" = "inventory_management"
        "member-system" = "member_system"
        "logistics-management" = "logistics_management"
        "notification-service" = "notification_service"
        "quality-control" = "quality_control"
        "recommendation-system" = "recommendation_system"
        "risk-control-system" = "risk_control_system"
        "social-features" = "social_features"
        "supplier-management" = "supplier_management"
        "marketing-campaigns" = "marketing_campaigns"
        "customer-service-system" = "customer_service_system"
        "data-analytics-platform" = "data_analytics_platform"
        "distributor-management" = "distributor_management"
        "batch-traceability" = "batch_traceability"
        
        # 技术组件模块
        "application-core" = "application_core"
        "database-core" = "database_core"
        "database-utils" = "database_utils"
        "data-models" = "base_models"
        "redis-cache" = "redis_cache"
    }
    
    # API端点规范 - 符合命名规范标准的路径模式
    ApiPatterns = @{
        # 完整API路径模式: /api/v1/{完整模块名}/{资源名}[/{资源id}][/{子资源或操作}]
        "FullApiPath" = "^/api/v1/[a-z][a-z0-9-]+/[a-z0-9-]+(/[a-z0-9-]+)*(/\{[a-z_]+\})?(/[a-z0-9-]+)*$"
        # 模块路由文件中的路径模式: /{完整模块名}/{资源名}[/{资源id}][/{子资源或操作}]
        "ModuleRoute" = "^/[a-z][a-z0-9-]+/[a-z0-9-]+(/[a-z0-9-]+)*(/\{[a-z_]+\})?(/[a-z0-9-]+)*$"
        # 参数命名: snake_case格式
        "Parameters" = "^[a-z][a-z0-9_]*$"
        # 完整模块名模式: kebab-case格式的业务概念名
        "CompleteModuleName" = "^[a-z]+(-[a-z]+)*$"
        # 资源名模式: 复数形式，kebab-case
        "ResourceName" = "^[a-z][a-z0-9-]*s?$"
    }
    
    # 数据库命名规范 - 符合命名规范标准
    DatabasePatterns = @{
        # 表名: 模块英文名 + 复数形式，snake_case格式
        "TableName" = "^[a-z][a-z0-9_]*s?$"
        # 字段名: snake_case格式
        "FieldName" = "^[a-z][a-z0-9_]*$"
        # 外键: {表名单数}_id格式
        "ForeignKey" = "^[a-z][a-z0-9_]*_id$"
        # 时间戳字段: {动作}_at格式
        "TimestampField" = "^[a-z][a-z0-9_]*_at$"
        # 布尔字段: is_{状态}格式
        "BooleanField" = "^is_[a-z][a-z0-9_]*$"
        # 数量字段: {名称}_quantity格式
        "QuantityField" = "^[a-z][a-z0-9_]*_quantity$"
        # 金额字段: {名称}_amount格式
        "AmountField" = "^[a-z][a-z0-9_]*_amount$"
    }
    
        # 代码命名规范 - 符合命名规范标准
    CodePatterns = @{
        # 类名: PascalCase格式
        "ClassName" = "^[A-Z][a-zA-Z0-9]*$"
        # 函数名: snake_case格式，支持私有函数(_开头)
        "FunctionName" = "^(_*[a-z][a-zA-Z0-9_]*|[a-z][a-zA-Z0-9_]*)$"
        # 变量名: snake_case格式
        "VariableName" = "^[a-z][a-zA-Z0-9_]*$"
        # 常量名: UPPER_SNAKE_CASE格式
        "ConstantName" = "^[A-Z][A-Z0-9_]*$"
        # 模块级文件名: 简化命名，符合模块化单体架构
        "ModuleFileName" = "^(router|models|repository|service|schemas|dependencies|utils|__init__|[a-z][a-z0-9_]*_service|auth_helpers)\.py$"
    }
}

# 处理模块名参数（在配置加载后）
if ($ModuleNameToProcess) {
    if ($NamingConfig.ModuleMappings.ContainsKey($ModuleNameToProcess)) {
        $TechModule = $NamingConfig.ModuleMappings[$ModuleNameToProcess]
    } else {
        $TechModule = $ModuleNameToProcess -replace '-','_'
    }
    
    # 如果指定了 ModuleName 且使用默认路径，则调整到该模块的目录
    if ($DocsPath -eq "docs/design/modules") {
        $DocsPath = "docs/design/modules/$ModuleNameToProcess"
    }
    if ($CodePath -eq "app") {
        $CodePath = "app/modules/$TechModule"
    }
    
    Write-ColorOutput "🎯 指定模块: $ModuleNameToProcess (技术实现: $TechModule)" "Blue"
    Write-ColorOutput "📁 文档路径: $DocsPath" "Blue"
    Write-ColorOutput "💻 代码路径: $CodePath" "Blue"
}

function Test-ApiNaming {
    Write-ColorOutput "🌐 检查API命名规范..." "Blue"
    
    $violations = @()
    
    # 检查主路由文件的前缀设置
    $mainRoutesFile = "app/api/main_routes.py"
    if (Test-Path $mainRoutesFile) {
        $mainContent = Get-Content $mainRoutesFile
        $prefixLines = $mainContent | Select-String -Pattern "prefix.*api.*v1"
        if ($prefixLines) {
            Write-ColorOutput "✅ 发现正确的API前缀设置: /api/v1" "Green"
        }
    }
    
    # 确定检查路径
    $searchPath = if ($TargetPath -and (Test-Path $TargetPath)) {
        if ((Get-Item $TargetPath).PSIsContainer) {
            $TargetPath
        } else {
            if ($TargetPath -like "*router.py") {
                # 如果是router.py文件，直接检查该文件
                $moduleFiles = @(Get-Item $TargetPath)
            } else {
                $moduleFiles = @()
            }
        }
    } else {
        $searchPath = $CodePath
    }
    
    # 检查模块路由文件
    if (-not $moduleFiles) {
        if ($searchPath -and (Test-Path $searchPath)) {
            $moduleFiles = Get-ChildItem -Path $searchPath -Filter "router.py" -Recurse
        } else {
            $moduleFiles = Get-ChildItem -Path "app/modules" -Filter "router.py" -Recurse
        }
    }
    
    foreach ($file in $moduleFiles) {
        $content = Get-Content $file.FullName
        
        # 提取模块名称
        $moduleName = if ($file.Directory) { $file.Directory.Name } else { "unknown" }
        
        # 根据ModuleMappings找到对应的业务概念名
        $businessModuleName = $null
        foreach ($mapping in $NamingConfig.ModuleMappings.GetEnumerator()) {
            if ($mapping.Value -eq $moduleName) {
                $businessModuleName = $mapping.Key
                break
            }
        }
        
        if (-not $businessModuleName) {
            $violations += @{
                Type = "模块映射"
                File = "$moduleName/router.py"
                Issue = "模块名不在标准映射表中: $moduleName"
                Line = 0
                Suggestion = "请在ModuleMappings中添加对应的业务概念名映射"
            }
            continue
        }
        
        # 检查路由定义
        $routePattern = '@router\.(get|post|put|delete|patch)\("'
        $routes = $content | Select-String -Pattern $routePattern
        
        foreach ($route in $routes) {
            $line = $route.Line
            # 提取引号内的路径
            if ($line -match '@router\.\w+\("([^"]+)"') {
                $endpoint = $matches[1]
                
                # 检查是否使用完整业务概念名前缀
                $expectedPrefix = "/$businessModuleName/"
                
                if ($endpoint -notmatch "^/$businessModuleName/") {
                    $violations += @{
                        Type = "API路由前缀"
                        File = "$moduleName/router.py"
                        Issue = "API端点未使用完整业务概念名前缀: $endpoint"
                        Line = $route.LineNumber
                        Suggestion = "应该使用完整业务概念名前缀: $expectedPrefix{resource}"
                    }
                }
                
                # 检查路径格式是否符合标准模式
                if ($endpoint -notmatch $NamingConfig.ApiPatterns.ModuleRoute) {
                    $violations += @{
                        Type = "API路径格式"
                        File = "$moduleName/router.py"
                        Issue = "API路径格式不符合规范: $endpoint"
                        Line = $route.LineNumber
                        Suggestion = "使用格式: /{完整业务概念名}/{资源名}[/{资源id}][/{子资源或操作}]"
                    }
                }
                
                # 检查资源名是否使用复数形式（从路径中提取第二部分）
                if ($endpoint -match "^/[a-z][a-z0-9-]+/([a-z0-9-]+)") {
                    $resourceName = $matches[1]
                    # 检查常见的单复数转换
                    $singularWords = @("product", "category", "order", "user", "item", "cart", "payment", "notification")
                    if ($singularWords -contains $resourceName) {
                        $violations += @{
                            Type = "API资源命名"
                            File = "$moduleName/router.py"
                            Issue = "资源名应使用复数形式: $resourceName"
                            Line = $route.LineNumber
                            Suggestion = "资源名使用复数形式，如: ${resourceName}s"
                        }
                    }
                }
            }
        }
        
        # 检查模块路由文件不应该包含prefix配置（由main.py统一管理）
        $prefixLines = $content | Select-String -Pattern "prefix\s*="
        if ($prefixLines) {
            foreach ($prefixLine in $prefixLines) {
                $violations += @{
                    Type = "路由架构"
                    File = "$moduleName/router.py"
                    Issue = "模块路由文件不应包含prefix配置"
                    Line = $prefixLine.LineNumber
                    Suggestion = "移除prefix配置，统一前缀在main.py中设置"
                }
            }
        }
    }
    
    return $violations
}

function Test-DatabaseNaming {
    Write-ColorOutput "🗄️ 检查数据库命名规范..." "Blue"
    
    $violations = @()
    
    # 确定检查路径
    $searchPath = if ($TargetPath -and (Test-Path $TargetPath)) {
        if ((Get-Item $TargetPath).PSIsContainer) {
            $TargetPath
        } else {
            if ($TargetPath -like "*models.py") {
                # 如果是models.py文件，直接检查该文件
                $moduleModelFiles = @(Get-Item $TargetPath)
            } else {
                $moduleModelFiles = @()
            }
        }
    } else {
        $searchPath = $CodePath
    }
    
    # 检查模块级models.py文件
    if (-not $moduleModelFiles) {
        if ($searchPath -and (Test-Path $searchPath)) {
            $moduleModelFiles = Get-ChildItem -Path $searchPath -Filter "models.py" -Recurse
        } else {
            $moduleModelFiles = Get-ChildItem -Path "app/modules" -Filter "models.py" -Recurse
        }
    }
    
    foreach ($file in $moduleModelFiles) {
        $content = Get-Content $file.FullName
        $moduleName = if ($file.Directory) { $file.Directory.Name } else { "unknown" }
        
        # 检查表名定义
        $tables = $content | Select-String -Pattern "__tablename__\s*=\s*['\""]([^'\""`]+)['\""]"
        
        foreach ($table in $tables) {
            $tableName = $table.Matches[0].Groups[1].Value
            
            if ($tableName -notmatch $NamingConfig.DatabasePatterns.TableName) {
                $violations += @{
                    Type = "数据库表名"
                    File = "$moduleName/models.py"
                    Issue = "表名不符合规范: $tableName"
                    Line = $table.LineNumber
                    Suggestion = "使用snake_case格式的复数形式，如: users, products, categories"
                }
            }
        }
        
        # 检查字段名定义
        $fields = $content | Select-String -Pattern "^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*Column"
        
        foreach ($field in $fields) {
            $fieldName = $field.Matches[0].Groups[1].Value
            
            # 检查字段名格式
            if ($fieldName -notmatch $NamingConfig.DatabasePatterns.FieldName) {
                $violations += @{
                    Type = "数据库字段名"
                    File = "$moduleName/models.py"
                    Issue = "字段名不符合规范: $fieldName"
                    Line = $field.LineNumber
                    Suggestion = "使用snake_case格式，如: user_id, created_at, is_active"
                }
            }
            
            # 检查特殊字段类型的命名规范
            $fieldLine = $field.Line
            
            # 检查外键命名（只检查以_id结尾的字段）
            if ($fieldLine -match "ForeignKey" -and $fieldName -match "_id$" -and 
                $fieldName -notmatch $NamingConfig.DatabasePatterns.ForeignKey) {
                $violations += @{
                    Type = "外键字段命名"
                    File = "$moduleName/models.py"
                    Issue = "外键字段名不符合规范: $fieldName"
                    Line = $field.LineNumber
                    Suggestion = "外键使用{表名单数}_id格式，如: user_id, category_id"
                }
            }
            
            # 检查时间戳字段命名
            if (($fieldLine -match "DateTime" -or $fieldLine -match "timestamp") -and 
                $fieldName -match "_at$" -and 
                $fieldName -notmatch $NamingConfig.DatabasePatterns.TimestampField) {
                $violations += @{
                    Type = "时间戳字段命名"
                    File = "$moduleName/models.py"
                    Issue = "时间戳字段名不符合规范: $fieldName"
                    Line = $field.LineNumber
                    Suggestion = "时间戳使用{动作}_at格式，如: created_at, updated_at, deleted_at"
                }
            }
            
            # 检查布尔字段命名
            if ($fieldLine -match "Boolean" -and 
                $fieldName -match "^is_" -and 
                $fieldName -notmatch $NamingConfig.DatabasePatterns.BooleanField) {
                $violations += @{
                    Type = "布尔字段命名"
                    File = "$moduleName/models.py"
                    Issue = "布尔字段名不符合规范: $fieldName"
                    Line = $field.LineNumber
                    Suggestion = "布尔字段使用is_{状态}格式，如: is_active, is_deleted, is_public"
                }
            }
            
            # 检查数量字段命名
            if ($fieldName -match "_quantity$" -and 
                $fieldName -notmatch $NamingConfig.DatabasePatterns.QuantityField) {
                $violations += @{
                    Type = "数量字段命名"
                    File = "$moduleName/models.py"
                    Issue = "数量字段名不符合规范: $fieldName"
                    Line = $field.LineNumber
                    Suggestion = "数量字段使用{名称}_quantity格式，如: stock_quantity, order_quantity"
                }
            }
            
            # 检查金额字段命名
            if ($fieldName -match "_amount$" -and 
                $fieldName -notmatch $NamingConfig.DatabasePatterns.AmountField) {
                $violations += @{
                    Type = "金额字段命名"
                    File = "$moduleName/models.py"
                    Issue = "金额字段名不符合规范: $fieldName"
                    Line = $field.LineNumber
                    Suggestion = "金额字段使用{名称}_amount格式，如: total_amount, discount_amount"
                }
            }
        }
    }
    
    # 检查共享模型文件
    $sharedModelsFile = "app/shared/base_models.py"
    if (Test-Path $sharedModelsFile) {
        $content = Get-Content $sharedModelsFile
        
        # 检查表名定义
        $tables = $content | Select-String -Pattern "__tablename__\s*=\s*['\""]([^'\""`]+)['\""]"
        
        foreach ($table in $tables) {
            $tableName = $table.Matches[0].Groups[1].Value
            
            if ($tableName -notmatch $NamingConfig.DatabasePatterns.TableName) {
                $violations += @{
                    Type = "数据库表名"
                    File = "shared/base_models.py"
                    Issue = "表名不符合规范: $tableName"
                    Line = $table.LineNumber
                    Suggestion = "使用snake_case格式的复数形式，如: users, products, categories"
                }
            }
        }
        
        # 检查字段名
        $fields = $content | Select-String -Pattern "^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*Column"
        
        foreach ($field in $fields) {
            $fieldName = $field.Matches[0].Groups[1].Value
            
            if ($fieldName -notmatch $NamingConfig.DatabasePatterns.FieldName) {
                $violations += @{
                    Type = "数据库字段名"
                    File = "shared/base_models.py"
                    Issue = "字段名不符合规范: $fieldName"
                    Line = $field.LineNumber
                    Suggestion = "使用snake_case格式，如: user_id, created_at, is_active"
                }
            }
        }
    }
    
    return $violations
}

function Test-DocumentationNaming {
    Write-ColorOutput "📚 检查文档命名规范..." "Blue"
    
    $violations = @()
    
    # 支持文件或目录路径
    if (Test-Path $DocsPath -PathType Leaf) {
        $items = @(Get-Item $DocsPath)
        $checkFile = $true
    } elseif (Test-Path $DocsPath -PathType Container) {
        $items = Get-ChildItem -Path $DocsPath -Directory
        $checkFile = $false
    } else {
        Write-ColorOutput "❌ 文档路径不存在: $DocsPath" "Red"
        return $violations
    }
    
    foreach ($item in $items) {
        if ($checkFile) {
            # 文件命名检查: kebab-case.md
            $fileName = $item.Name
            if ($fileName -notmatch '^[a-z0-9]+(-[a-z0-9]+)*\.md$') {
                $violations += @{
                    Type = '文档文件命名'
                    File = $DocsPath
                    Issue = "文件名不符合kebab-case规范: $fileName"
                    Line = 0
                    Suggestion = '使用kebab-case命名，末尾.md，如: product-catalog.md, user-authentication.md'
                }
            }
        } else {
            # 模块目录命名检查
            $dirName = $item.Name
            
            # 检查是否为有效的业务概念名（kebab-case格式）
            if ($dirName -notmatch $NamingConfig.ApiPatterns.CompleteModuleName) {
                $violations += @{
                    Type = '文档目录命名格式'
                    File = $item.FullName
                    Issue = "目录名称格式不符合kebab-case规范: $dirName"
                    Line = 0
                    Suggestion = '使用kebab-case格式的业务概念名，如: product-catalog, user-auth'
                }
            }
            
            # 检查是否在标准映射表中
            $isValidModule = $NamingConfig.ModuleMappings.ContainsKey($dirName)
            if (-not $isValidModule) {
                $violations += @{
                    Type = '文档目录映射'
                    File = $item.FullName
                    Issue = "目录名称不在标准模块映射表中: $dirName"
                    Line = 0
                    Suggestion = '使用标准业务概念名，参考ModuleMappings表中的键值'
                }
            }
            
            # 检查模块文档目录结构（如果是模块目录）
            if ($item.FullName -like "*docs/design/modules/*") {
                $requiredFiles = @("overview.md", "api-spec.md", "implementation.md")
                foreach ($reqFile in $requiredFiles) {
                    $filePath = Join-Path $item.FullName $reqFile
                    if (-not (Test-Path $filePath)) {
                        $violations += @{
                            Type = '模块文档完整性'
                            File = $item.FullName
                            Issue = "缺少必需的模块文档文件: $reqFile"
                            Line = 0
                            Suggestion = "创建必需的模块文档文件: $reqFile"
                        }
                    }
                }
            }
        }
    }
    
    return $violations
}

function Test-CodeNaming {
    Write-ColorOutput "💻 检查代码命名规范..." "Blue"
    
    $violations = @()
    
    # 确定检查路径
    $searchPath = if ($TargetPath -and (Test-Path $TargetPath)) {
        if ((Get-Item $TargetPath).PSIsContainer) {
            $TargetPath
        } else {
            Split-Path $TargetPath -Parent
        }
    } else {
        $CodePath
    }
    
    if (-not (Test-Path $searchPath)) {
        Write-ColorOutput "❌ 代码检查路径不存在: $searchPath" "Red"
        return $violations
    }
    
    Write-ColorOutput "🔍 检查路径: $searchPath" "Blue"
    
    # 检查Python文件中的类名、函数名
    $pythonFiles = if ($TargetPath -and -not (Get-Item $TargetPath).PSIsContainer) {
        # 如果是单个文件
        @(Get-Item $TargetPath)
    } else {
        # 如果是目录
        Get-ChildItem -Path $searchPath -Filter "*.py" -Recurse
    }
    
    foreach ($file in $pythonFiles) {
        $content = Get-Content $file.FullName
        $fileName = $file.Name
        $relativePath = $file.FullName -replace [regex]::Escape((Get-Location).Path), ""
        
        # 检查模块化单体架构下的文件命名规范
        if ($relativePath -like "*app\modules\*") {
            if ($fileName -notmatch $NamingConfig.CodePatterns.ModuleFileName) {
                $violations += @{
                    Type = "模块文件命名"
                    File = $relativePath
                    Issue = "模块文件名不符合模块化单体架构规范: $fileName"
                    Line = 0
                    Suggestion = "使用标准文件名: router.py, models.py, service.py, repository.py, schemas.py, dependencies.py, utils.py 或 {domain}_service.py"
                }
            }
        }
        
        # 检查类名 (PascalCase)
        $classes = $content | Select-String -Pattern "^class\s+([a-zA-Z_][a-zA-Z0-9_]*)"
        foreach ($class in $classes) {
            $className = $class.Matches[0].Groups[1].Value
            
            if ($className -notmatch $NamingConfig.CodePatterns.ClassName) {
                $violations += @{
                    Type = "类命名"
                    File = $relativePath
                    Issue = "类名不符合PascalCase规范: $className"
                    Line = $class.LineNumber
                    Suggestion = "使用PascalCase格式，如: UserAuth, ProductCatalog, OrderService"
                }
            }
        }
        
        # 检查函数名
        $functions = $content | Select-String -Pattern "^(async\s+)?def\s+([a-zA-Z_][a-zA-Z0-9_]*)"
        foreach ($func in $functions) {
            $funcName = $func.Matches[0].Groups[2].Value
            
            if ($funcName -notmatch $NamingConfig.CodePatterns.FunctionName) {
                $violations += @{
                    Type = "函数命名"
                    File = $relativePath
                    Issue = "函数名不符合snake_case规范: $funcName"
                    Line = $func.LineNumber
                    Suggestion = "使用snake_case格式，如: get_user, create_product, update_order_status"
                }
            }
        }
        
        # 检查变量名 (在赋值语句中，排除Python特殊变量)
        $variables = $content | Select-String -Pattern "^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*="
        foreach ($var in $variables) {
            $varName = $var.Matches[0].Groups[1].Value
            
            # 排除Python特殊变量、类定义、函数定义、导入语句等
            if ($var.Line -notmatch "^(class|def|from|import)" -and 
                $varName -notmatch "^__[a-zA-Z_]+__$" -and  # Python魔术方法和特殊变量
                $varName -notmatch "^_[a-zA-Z_]+$" -and     # 私有变量（单下划线开头）
                $varName -notmatch $NamingConfig.CodePatterns.VariableName) {
                $violations += @{
                    Type = "变量命名"
                    File = $relativePath
                    Issue = "变量名不符合snake_case规范: $varName"
                    Line = $var.LineNumber
                    Suggestion = "使用snake_case格式，如: user_data, product_list, order_status"
                }
            }
        }
        
        # 检查常量名 (全大写变量)
        $constants = $content | Select-String -Pattern "^\s*([A-Z][A-Z0-9_]*)\s*="
        foreach ($const in $constants) {
            $constName = $const.Matches[0].Groups[1].Value
            
            if ($constName -notmatch $NamingConfig.CodePatterns.ConstantName) {
                $violations += @{
                    Type = "常量命名"
                    File = $relativePath
                    Issue = "常量名不符合UPPER_SNAKE_CASE规范: $constName"
                    Line = $const.LineNumber
                    Suggestion = "使用UPPER_SNAKE_CASE格式，如: MAX_RETRY_COUNT, DEFAULT_PAGE_SIZE"
                }
            }
        }
    }
    
    return $violations
}

function Show-CheckResults {
    param([array]$Violations)
    
    if ($Violations.Count -eq 0) {
        Write-ColorOutput "✅ 没有发现命名规范违规问题！" "Green"
        return
    }
    
    Write-ColorOutput "❌ 发现 $($Violations.Count) 个命名规范违规问题：" "Red"
    Write-ColorOutput "=" * 60 "Yellow"
    
    $groupedViolations = $Violations | Group-Object Type
    
    foreach ($group in $groupedViolations) {
        Write-ColorOutput "📋 $($group.Name) 问题 ($($group.Count)个):" "Cyan"
        
        foreach ($violation in $group.Group) {
            Write-ColorOutput "  📄 文件: $($violation.File)" "White"
            if ($violation.Line -gt 0) {
                Write-ColorOutput "  📍 行号: $($violation.Line)" "White"
            }
            Write-ColorOutput "  ❌ 问题: $($violation.Issue)" "Red"
            Write-ColorOutput "  💡 建议: $($violation.Suggestion)" "Green"
            Write-ColorOutput "  " + "-" * 50 "Gray"
        }
        Write-ColorOutput ""
    }
    
    Write-ColorOutput "🔧 修复建议：" "Yellow"
    Write-ColorOutput "1. 查阅命名规范文档: docs/standards/naming-conventions-standards.md" "White"
    Write-ColorOutput "2. 参考模块映射表进行重命名" "White"
    Write-ColorOutput "3. 使用 --Fix 参数尝试自动修复部分问题" "White"
    Write-ColorOutput "4. 完成修复后重新运行检查" "White"
}

# 主执行逻辑
Write-ColorOutput "🔍 命名规范合规性检查工具" "Cyan"
Write-ColorOutput "检查类型: $CheckType" "Blue"
Write-ColorOutput "=" * 50 "Yellow"

$allViolations = @()

switch ($CheckType.ToLower()) {
    "api" {
        $allViolations += Test-ApiNaming
    }
    "database" {
        $allViolations += Test-DatabaseNaming
    }
    "docs" {
        $allViolations += Test-DocumentationNaming
    }
    "code" {
        $allViolations += Test-CodeNaming
    }
    "all" {
        $allViolations += Test-ApiNaming
        $allViolations += Test-DatabaseNaming
        $allViolations += Test-DocumentationNaming
        $allViolations += Test-CodeNaming
    }
    default {
        Write-ColorOutput "❌ 未知的检查类型: $CheckType" "Red"
        Write-ColorOutput "支持的类型: all, api, database, docs, code" "Yellow"
        exit 1
    }
}

Show-CheckResults -Violations $allViolations

# 设置退出码
if ($allViolations.Count -gt 0) {
    exit 1
} else {
    exit 0
}
