# 模块文档自动生成脚本
# 基于标准模板自动生成完整的模块文档结构

param(
    [Parameter(Mandatory = $true)]
    [string]$ModuleName,           # 模块业务概念名（连字符格式），如 user-auth
    
    [Parameter(Mandatory = $false)]
    [string]$ChineseName = "",     # 中文名称，如 用户认证模块
    
    [Parameter(Mandatory = $false)]
    [string]$Owner = "",           # 负责人姓名
    
    [Parameter(Mandatory = $false)]
    [switch]$Force = $false        # 强制覆盖已存在的文档
)

# 模块文档生成配置
$ModuleDocsConfig = @{
    # 必需的7个文档
    RequiredDocs = @(
        @{
            FileName = "README.md"
            Template = "module-readme-template.md"
            Description = "模块导航入口"
        },
        @{
            FileName = "overview.md"
            Template = "module-template.md"
            Description = "详细技术概述"
        },
        @{
            FileName = "requirements.md"
            Template = "module-requirements-template.md"
            Description = "业务需求规格"
        },
        @{
            FileName = "design.md"
            Template = "module-design-template.md"
            Description = "技术设计决策"
        },
        @{
            FileName = "api-spec.md"
            Template = $null
            Description = "API规范定义"
            Content = "# {ModuleName} - API规范文档`n`n## API端点定义`n`n### 基础信息`n- **模块名**: {ModuleName}`n- **API前缀**: `/api/v1/{ModuleName}/`n- **认证**: JWT Bearer Token`n`n### 端点列表`n`n| 方法 | 路径 | 功能 | 状态 |`n|------|------|------|------|`n| GET | `/api/v1/{ModuleName}/health` | 健康检查 | 待实现 |`n`n详细API规范请参考 [standards/openapi.yaml](../../standards/openapi.yaml)"
        },
        @{
            FileName = "api-implementation.md"
            Template = $null
            Description = "API实施记录"
            Content = "# {ModuleName} - API实施记录`n`n## 实施状态`n`n### 已实现接口`n`n| 接口 | 实施日期 | 开发者 | 状态 |`n|------|----------|--------|------|`n| 待添加 | - | - | - |`n`n### 实施细节`n`n#### 接口实现记录`n`n详细实施过程将在开发过程中更新。"
        },
        @{
            FileName = "implementation.md"
            Template = "module-implementation-template.md"
            Description = "开发实现记录"
        }
    )
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    
    $colorMap = @{
        "Red" = [ConsoleColor]::Red
        "Green" = [ConsoleColor]::Green
        "Yellow" = [ConsoleColor]::Yellow
        "Blue" = [ConsoleColor]::Blue
        "Cyan" = [ConsoleColor]::Cyan
        "Magenta" = [ConsoleColor]::Magenta
        "White" = [ConsoleColor]::White
    }
    
    if ($colorMap.ContainsKey($Color)) {
        Write-Host $Message -ForegroundColor $colorMap[$Color]
    } else {
        Write-Host $Message
    }
}

function Test-ModuleNameFormat {
    param([string]$Name)
    
    # 检查是否符合连字符格式
    if ($Name -notmatch "^[a-z]+(-[a-z]+)*$") {
        Write-ColorOutput "❌ 模块名格式错误: $Name" "Red"
        Write-ColorOutput "   正确格式: 小写字母+连字符，如 user-auth, product-catalog" "Yellow"
        return $false
    }
    return $true
}

function Get-ModuleCodeName {
    param([string]$BusinessName)
    
    # 将业务概念名转换为代码名（连字符转下划线）
    return $BusinessName -replace '-', '_'
}

function Get-TemplateVariables {
    param(
        [string]$ModuleName,
        [string]$ChineseName,
        [string]$Owner
    )
    
    $today = Get-Date -Format "yyyy-MM-dd"
    $codeName = Get-ModuleCodeName -BusinessName $ModuleName
    
    return @{
        "{模块名称}" = if ($ChineseName) { $ChineseName } else { "${ModuleName}模块" }
        "{module-name}" = $ModuleName
        "{module_name}" = $codeName
        "{YYYY-MM-DD}" = $today
        "{负责人姓名}" = if ($Owner) { $Owner } else { "待指定" }
        "{ModuleName}" = $ModuleName
    }
}

function Update-TemplateVariables {
    param(
        [string]$Content,
        [hashtable]$Variables
    )
    
    $result = $Content
    foreach ($var in $Variables.GetEnumerator()) {
        $result = $result -replace [regex]::Escape($var.Key), $var.Value
    }
    return $result
}

function New-ModuleDirectory {
    param([string]$ModuleName)
    
    $moduleDir = "docs\modules\$ModuleName"
    
    if (-not (Test-Path $moduleDir)) {
        New-Item -Path $moduleDir -ItemType Directory -Force | Out-Null
        Write-ColorOutput "✅ 创建模块目录: $moduleDir" "Green"
    } else {
        Write-ColorOutput "📁 模块目录已存在: $moduleDir" "Yellow"
    }
    
    return $moduleDir
}

function New-DocumentFromTemplate {
    param(
        [string]$ModuleDir,
        [hashtable]$DocInfo,
        [hashtable]$Variables,
        [bool]$Force
    )
    
    $docPath = Join-Path $ModuleDir $DocInfo.FileName
    
    # 检查文件是否已存在
    if ((Test-Path $docPath) -and -not $Force) {
        Write-ColorOutput "⚠️  文档已存在，跳过: $($DocInfo.FileName)" "Yellow"
        return $false
    }
    
    $content = ""
    
    if ($DocInfo.Template) {
        # 从模板文件读取内容
        $templatePath = "docs\templates\$($DocInfo.Template)"
        if (Test-Path $templatePath) {
            $content = Get-Content -Path $templatePath -Raw -Encoding UTF8
        } else {
            Write-ColorOutput "❌ 模板文件不存在: $templatePath" "Red"
            return $false
        }
    } elseif ($DocInfo.Content) {
        # 使用预定义内容
        $content = $DocInfo.Content
    } else {
        Write-ColorOutput "❌ 文档配置错误: $($DocInfo.FileName)" "Red"
        return $false
    }
    
    # 替换模板变量
    $content = Update-TemplateVariables -Content $content -Variables $Variables
    
    # 创建文档文件
    $content | Out-File -FilePath $docPath -Encoding UTF8
    
    $action = if ((Test-Path $docPath) -and $Force) { "覆盖" } else { "创建" }
    Write-ColorOutput "✅ ${action}文档: $($DocInfo.FileName) - $($DocInfo.Description)" "Green"
    
    return $true
}

function Update-ModulesReadme {
    param([string]$ModuleName, [string]$ChineseName)
    
    $modulesReadme = "docs\modules\README.md"
    
    if (Test-Path $modulesReadme) {
        $content = Get-Content -Path $modulesReadme -Raw -Encoding UTF8
        
        # 检查是否已经包含该模块
        if ($content -match "\| \*\*$ModuleName\*\*") {
            Write-ColorOutput "📝 模块已在索引中: $ModuleName" "Yellow"
        } else {
            Write-ColorOutput "📝 需要手动更新 docs/design/modules/README.md，添加新模块: $ModuleName" "Cyan"
        }
    }
}

function Show-Summary {
    param(
        [string]$ModuleName,
        [string]$ModuleDir,
        [array]$CreatedDocs
    )
    
    Write-ColorOutput "`n🎉 模块文档生成完成！" "Green"
    Write-ColorOutput "📂 模块目录: $ModuleDir" "Blue"
    Write-ColorOutput "📋 生成的文档 ($($CreatedDocs.Count)/7):" "Blue"
    
    foreach ($doc in $CreatedDocs) {
        Write-ColorOutput "   ✅ $doc" "Green"
    }
    
    Write-ColorOutput "`n📝 后续步骤:" "Blue"
    Write-ColorOutput "   1. 编辑各文档文件，填入具体内容" "Cyan"
    Write-ColorOutput "   2. 更新 docs/design/modules/README.md 添加模块索引" "Cyan"
    Write-ColorOutput "   3. 运行检查脚本验证文档完整性:" "Cyan"
    Write-ColorOutput "      .\scripts\check_docs.ps1 -Path docs\modules\$ModuleName" "Yellow"
}

# 主程序开始
Write-ColorOutput "🚀 模块文档生成工具" "Blue"
Write-ColorOutput "=========================" "Blue"

# 验证模块名格式
if (-not (Test-ModuleNameFormat -Name $ModuleName)) {
    exit 1
}

Write-ColorOutput "📋 模块信息:" "Blue"
Write-ColorOutput "   业务名称: $ModuleName" "Cyan"
Write-ColorOutput "   代码名称: $(Get-ModuleCodeName -BusinessName $ModuleName)" "Cyan"
Write-ColorOutput "   中文名称: $(if ($ChineseName) { $ChineseName } else { '自动生成' })" "Cyan"
Write-ColorOutput "   负责人: $(if ($Owner) { $Owner } else { '待指定' })" "Cyan"

# 创建模块目录
$moduleDir = New-ModuleDirectory -ModuleName $ModuleName

# 准备模板变量
$variables = Get-TemplateVariables -ModuleName $ModuleName -ChineseName $ChineseName -Owner $Owner

# 生成所有必需文档
$createdDocs = @()
Write-ColorOutput "`n📄 生成文档文件:" "Blue"

foreach ($docInfo in $ModuleDocsConfig.RequiredDocs) {
    if (New-DocumentFromTemplate -ModuleDir $moduleDir -DocInfo $docInfo -Variables $variables -Force $Force) {
        $createdDocs += $docInfo.FileName
    }
}

# 更新模块索引
Update-ModulesReadme -ModuleName $ModuleName -ChineseName $ChineseName

# 显示总结
Show-Summary -ModuleName $ModuleName -ModuleDir $moduleDir -CreatedDocs $createdDocs

Write-ColorOutput "`n✨ 文档生成完成！请根据实际需求编辑文档内容。" "Green"