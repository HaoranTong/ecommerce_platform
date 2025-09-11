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
    # 模块标准映射
    ModuleMappings = @{
        "user" = "user-auth"
        "cart" = "shopping-cart"
        "product" = "product-catalog"
        "order" = "order-management"
        "category" = "category-management"
        "payment" = "payment-service"
        "inventory" = "inventory-management"
        "notification" = "notification-service"
        "distributor" = "distributor-management"
        "recommendation" = "recommendation-system"
        "batch" = "batch-traceability"
        "app" = "application-core"
        "db" = "database-core"
        "utils" = "database-utils"
        "model" = "data-models"
        "cache" = "redis-cache"
    }
    
    # API端点规范
    ApiPatterns = @{
        "RESTful" = "^/(auth|api)/[a-z]+(/[a-z-]+)*(/\{[a-z_]+\})?(/[a-z-]+)*$"
        "Parameters" = "^[a-z][a-z0-9_]*$"
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
        "FunctionName" = "^[a-z][a-zA-Z0-9_]*$"  # camelCase或snake_case
        "VariableName" = "^[a-z][a-zA-Z0-9_]*$"  # camelCase或snake_case
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

function Check-ApiNaming {
    Write-ColorOutput "🌐 检查API命名规范..." "Blue"
    
    $violations = @()
    $apiFiles = Get-ChildItem -Path "app/api" -Filter "*_routes.py" -Recurse
    
    foreach ($file in $apiFiles) {
        $content = Get-Content $file.FullName
        
        # 检查路由定义
        $routes = $content | Select-String -Pattern '@router\.(get|post|put|delete|patch)\("([^"]+)"'
        
        foreach ($route in $routes) {
            $endpoint = $route.Matches[0].Groups[2].Value
            
            # 检查RESTful规范
            if ($endpoint -notmatch $NamingConfig.ApiPatterns.RESTful) {
                $violations += @{
                    Type = "API路由"
                    File = $file.Name
                    Issue = "路由不符合RESTful规范: $endpoint"
                    Line = $route.LineNumber
                    Suggestion = "使用标准RESTful路径格式"
                }
            }
        }
        
        # 检查函数参数命名
        $functions = $content | Select-String -Pattern 'async def [a-zA-Z_][a-zA-Z0-9_]*\('
        foreach ($func in $functions) {
            # 这里可以添加更详细的参数检查逻辑
        }
    }
    
    return $violations
}

function Check-DatabaseNaming {
    Write-ColorOutput "🗄️ 检查数据库命名规范..." "Blue"
    
    $violations = @()
    $modelsFile = "app/models.py"
    
    if (Test-Path $modelsFile) {
        $content = Get-Content $modelsFile
        
        # 检查表名定义
        $tables = $content | Select-String -Pattern "__tablename__\s*=\s*['\""]([^'\""`]+)['\""]"
        
        foreach ($table in $tables) {
            $tableName = $table.Matches[0].Groups[1].Value
            
            if ($tableName -notmatch $NamingConfig.DatabasePatterns.TableName) {
                $violations += @{
                    Type = "数据库表名"
                    File = "models.py"
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
                    File = "models.py"
                    Issue = "字段名不符合规范: $fieldName"
                    Line = $field.LineNumber
                    Suggestion = "使用snake_case格式"
                }
            }
        }
    }
    
    return $violations
}

function Check-DocumentationNaming {
    Write-ColorOutput "📚 检查文档命名规范..." "Blue"
    
    $violations = @()
    
    # 检查模块文档目录命名
    $modulesDirs = Get-ChildItem -Path "docs/modules" -Directory
    
    foreach ($dir in $modulesDirs) {
        $dirName = $dir.Name
        
        # 检查是否使用了完整描述名
        $isValidModuleName = $false
        foreach ($mapping in $NamingConfig.ModuleMappings.GetEnumerator()) {
            if ($dirName -eq $mapping.Value) {
                $isValidModuleName = $true
                break
            }
        }
        
        if (-not $isValidModuleName -and $dirName -ne "api") {
            $violations += @{
                Type = "文档目录命名"
                File = "docs/modules/$dirName"
                Issue = "模块目录名称不符合规范: $dirName"
                Line = 0
                Suggestion = "使用完整描述名称，参考模块映射表"
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

function Check-CodeNaming {
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
        $allViolations += Check-ApiNaming
    }
    "database" {
        $allViolations += Check-DatabaseNaming
    }
    "docs" {
        $allViolations += Check-DocumentationNaming
    }
    "code" {
        $allViolations += Check-CodeNaming
    }
    "all" {
        $allViolations += Check-ApiNaming
        $allViolations += Check-DatabaseNaming
        $allViolations += Check-DocumentationNaming
        $allViolations += Check-CodeNaming
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
