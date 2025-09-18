# 命名规范合规性检查脚本
# 此脚本用于检查代码仓库的命名规范合规性

param(
    [Parameter(Mandatory = $false)]
    [string]$CheckType = "all",  # all, api, database, docs, code
    
    [Parameter(Mandatory = $false)]
    [switch]$Fix = $false        # 是否尝试自动修复
)

# 命名规范配置
$NamingConfig = @{
    # 模块标准映射 - 更新为新架构
    ModuleMappings = @{
        # 业务概念名 -> 技术实现名映射
        "user-auth" = "user_auth"
        "shopping-cart" = "shopping_cart"
        "product-catalog" = "product_catalog"
        "order-management" = "order_management"
        "payment-service" = "payment_service"
        "batch-traceability" = "batch_traceability"
        "logistics-management" = "logistics_management"
        "quality-control" = "quality_control"
        "member-system" = "member_system"
        "distributor-management" = "distributor_management"
        "marketing-campaigns" = "marketing_campaigns"
        "social-features" = "social_features"
        "inventory-management" = "inventory_management"
        "notification-service" = "notification_service"
        "supplier-management" = "supplier_management"
        "recommendation-system" = "recommendation_system"
        "customer-service-system" = "customer_service_system"
        "risk-control-system" = "risk_control_system"
        "data-analytics-platform" = "data_analytics_platform"
        "application-core" = "application_core"
        "database-core" = "database_core"
        "base-models" = "base_models"
        "redis-cache" = "redis_cache"
        "database-utils" = "database_utils"
    }
    
    # API端点规范 - 完整模块名称架构
    ApiPatterns = @{
        # 模块路由文件中的路径模式（完整模块名 + 资源路径）
        "ModuleRoute" = "^/[a-z][a-z0-9-]+/[a-z0-9-]+(/[a-z0-9-]+)*(/\{[a-z_]+\})?(/[a-z0-9-]+)*$"
        # 完整API路径模式（包含/api/v1前缀 + 完整模块名）
        "FullApiPath" = "^/api/v1/[a-z][a-z0-9-]+/[a-z0-9-]+(/[a-z0-9-]+)*(/\{[a-z_]+\})?(/[a-z0-9-]+)*$"
        "Parameters" = "^[a-z][a-z0-9_]*$"
        # 完整模块名模式（连字符分隔的业务概念名）
        "CompleteModuleName" = "^[a-z]+(-[a-z]+)*$"
    }
    
    # 数据库命名规范
    DatabasePatterns = @{
        "TableName" = "^[a-z][a-z0-9_]*s?$"  # 复数形式
        "FieldName" = "^[a-z][a-z0-9_]*$"    # snake_case
        "ForeignKey" = "^[a-z][a-z0-9_]*_id$" # table_id格式
    }
    
    # 代码命名规范
    CodePatterns = @{
        "ClassName" = "^[A-Z][a-zA-Z0-9]*$"      # PascalCase
        "FunctionName" = "^(_*[a-z][a-zA-Z0-9_]*|[a-z][a-zA-Z0-9_]*)$"  # snake_case，支持私有函数(_开头)
        "VariableName" = "^[a-z][a-zA-Z0-9_]*$"  # snake_case
    }
}

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
    
    # 检查模块路由文件 - 更新为新架构
    $moduleFiles = Get-ChildItem -Path "app/modules" -Filter "router.py" -Recurse
    
    foreach ($file in $moduleFiles) {
        $content = Get-Content $file.FullName
        
        # 提取模块名称
        $moduleName = $file.Directory.Name
        
        # 检查路由定义
        $routePattern = '@router\.(get|post|put|delete|patch)\("'
        $routes = $content | Select-String -Pattern $routePattern
        
        foreach ($route in $routes) {
            $line = $route.Line
            # 提取引号内的路径
            if ($line -match '@router\.\w+\("([^"]+)"') {
                $endpoint = $matches[1]
                
                # 根据新规范：模块路由应该包含完整模块名作为前缀
                $expectedModuleName = $moduleName -replace "_", "-"
                $expectedPrefix = "/$expectedModuleName/"
                
                # 检查是否使用完整模块名前缀
                if ($endpoint -notmatch "^/$expectedModuleName/") {
                    $violations += @{
                        Type = "API路由"
                        File = "$moduleName/router.py"
                        Issue = "API端点未使用完整模块名前缀: $endpoint"
                        Line = $route.LineNumber
                        Suggestion = "应该使用完整模块名前缀，如: $expectedPrefix{resource}"
                    }
                }
                
                # 检查路径格式（完整模块名 + 资源路径）
                if ($endpoint -notmatch "^/[a-z][a-z0-9-]+/[a-z][a-z0-9-]*") {
                    $violations += @{
                        Type = "API路由格式"
                        File = "$moduleName/router.py"
                        Issue = "API路径格式不符合规范: $endpoint"
                        Line = $route.LineNumber
                        Suggestion = "使用格式: /{完整模块名}/{资源名}，如 /user-auth/login, /product-catalog/products"
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
    
    # 检查模块级models.py文件 - 更新为新架构
    $moduleModelFiles = Get-ChildItem -Path "app/modules" -Filter "models.py" -Recurse
    
    foreach ($file in $moduleModelFiles) {
        $content = Get-Content $file.FullName
        $moduleName = $file.Directory.Name
        
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
                    Suggestion = "使用snake_case格式的复数形式"
                }
            }
        }
        
        # 检查字段名定义
        $fields = $content | Select-String -Pattern "Column\s*\("
        foreach ($field in $fields) {
            # 检查字段命名规范
            if ($field.Line -match "Column\s*\(\s*(\w+)") {
                $fieldType = $matches[1]
                Write-Verbose "检查字段类型: $fieldType 在行 $($field.LineNumber)"
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
                    Suggestion = "使用snake_case格式的复数形式"
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
                    Suggestion = "使用snake_case格式"
                }
            }
        }
    }
    
    return $violations
}

function Test-DocumentationNaming {
    Write-ColorOutput "📚 检查文档命名规范..." "Blue"
    
    $violations = @()
    
    # 检查模块文档目录命名
    $modulesDirs = Get-ChildItem -Path "docs/modules" -Directory
    
    foreach ($dir in $modulesDirs) {
        $dirName = $dir.Name
        
        # 文档目录应该使用业务概念名（kebab-case）
        # 检查是否在模块映射表的键中（业务概念名）
        $isValidModuleName = $false
        if ($NamingConfig.ModuleMappings.ContainsKey($dirName)) {
            $isValidModuleName = $true
        }
        
        # 特殊目录名称也是合法的
        $specialDirs = @("api", "README.md")
        if ($dirName -in $specialDirs) {
            $isValidModuleName = $true
        }
        
        if (-not $isValidModuleName) {
            $violations += @{
                Type = "文档目录命名"
                File = "docs/modules/$dirName"
                Issue = "模块目录名称不符合规范: $dirName"
                Line = 0
                Suggestion = "使用kebab-case格式的业务概念名，参考模块映射表的键名"
            }
        }
    }
    
    # 检查API文档目录命名
    if (Test-Path "docs/api/modules") {
        $apiDirs = Get-ChildItem -Path "docs/api/modules" -Directory
        
        foreach ($dir in $apiDirs) {
            $dirName = $dir.Name
            
            # API文档应该使用简短的模块英文名
            if (-not $NamingConfig.ModuleMappings.ContainsKey($dirName)) {
                $violations += @{
                    Type = "API文档目录命名"
                    File = "docs/api/modules/$dirName"
                    Issue = "API文档目录名称不符合规范: $dirName"
                    Line = 0
                    Suggestion = "使用模块英文名称，参考模块映射表"
                }
            }
        }
    }
    
    return $violations
}

function Test-CodeNaming {
    Write-ColorOutput "💻 检查代码命名规范..." "Blue"
    
    $violations = @()
    
    # 检查Python文件中的类名、函数名
    $pythonFiles = Get-ChildItem -Path "app" -Filter "*.py" -Recurse
    
    foreach ($file in $pythonFiles) {
        $content = Get-Content $file.FullName
        
        # 检查类名 (PascalCase)
        $classes = $content | Select-String -Pattern "^class\s+([a-zA-Z_][a-zA-Z0-9_]*)"
        foreach ($class in $classes) {
            $className = $class.Matches[0].Groups[1].Value
            
            if ($className -notmatch $NamingConfig.CodePatterns.ClassName) {
                $violations += @{
                    Type = "类命名"
                    File = $file.Name
                    Issue = "类名不符合PascalCase规范: $className"
                    Line = $class.LineNumber
                    Suggestion = "使用PascalCase格式 (如: UserAuth, ProductCatalog)"
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
                    File = $file.Name
                    Issue = "函数名不符合规范: $funcName"
                    Line = $func.LineNumber
                    Suggestion = "使用snake_case格式 (如: get_user, create_product)"
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
    Write-ColorOutput "1. 查阅命名规范文档: docs/standards/naming-conventions.md" "White"
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
