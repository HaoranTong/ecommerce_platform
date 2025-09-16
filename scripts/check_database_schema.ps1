# 数据库架构完整性检查脚本
# 检查SQLAlchemy模型定义的常见问题和最佳实践合规性

param(
    [Parameter(Mandatory = $false)]
    [string]$ModuleName = "",     # 指定模块名，为空则检查所有模块
    
    [Parameter(Mandatory = $false)]
    [switch]$Fix = $false,        # 是否尝试自动修复
    
    [Parameter(Mandatory = $false)]
    [switch]$Detailed = $false    # 详细输出
)

# 数据库架构检查配置
$DatabaseConfig = @{
    # 字段类型规范
    FieldTypes = @{
        "主键字段" = @{
            Pattern = "id\s*=\s*Column\("
            ValidTypes = @("Integer", "BigInteger")
            RequiredAttributes = @("primary_key=True", "autoincrement=True")
            ForbiddenAttributes = @("nullable=False")  # 主键默认不能为空
        }
        "外键字段" = @{
            Pattern = "Column\(.*ForeignKey"
            RequiredAttributes = @("ForeignKey\('[\w.]+'\)")
            RecommendedAttributes = @("index=True")
        }
        "时间字段" = @{
            Pattern = "(created_at|updated_at|deleted_at)\s*=\s*Column\("
            ValidTypes = @("DateTime", "TIMESTAMP")
            RequiredAttributes = @("default=")
        }
        "字符串字段" = @{
            Pattern = "Column\(.*String"
            RequiredAttributes = @("String\(\d+\)")  # 必须指定长度
        }
        "布尔字段" = @{
            Pattern = "Column\(.*Boolean"
            RecommendedAttributes = @("default=")
        }
    }
    
    # 表结构规范
    TableRules = @{
        "表名规范" = @{
            Pattern = "__tablename__\s*=\s*['""]([^'""]+)['""]"
            Rule = "^[a-z][a-z0-9_]*s?$"  # snake_case，建议复数
        }
        "必需字段" = @("id", "created_at", "updated_at")
        "索引规范" = @{
            "主键索引" = "primary_key=True"
            "外键索引" = "index=True"
            "唯一索引" = "unique=True"
        }
    }
    
    # 关系定义规范
    RelationshipRules = @{
        "外键命名" = "^[a-z][a-z0-9_]*_id$"
        "反向引用" = "back_populates|backref"
        "级联规则" = "cascade="
    }
    
    # 常见错误模式
    CommonIssues = @{
        "主键nullable冲突" = "primary_key.*True.*nullable.*False|nullable.*False.*primary_key.*True"
        "缺少长度的String" = "Column\(String\s*[,\)]"
        "未索引的外键" = "ForeignKey\([^)]+\)(?![^,]*index\s*=\s*True)"
        "缺少时间戳" = "class\s+\w+.*:"  # 需要进一步检查是否有created_at/updated_at
        "硬编码默认值" = "default\s*=\s*['""](?!func\.)[^'""]*['""]"
    }
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

function Check-PrimaryKeyIssues {
    param([string]$FilePath, [array]$Content)
    
    $issues = @()
    $lineNumber = 0
    
    foreach ($line in $Content) {
        $lineNumber++
        
        # 检查主键字段定义
        if ($line -match "^\s*id\s*=\s*Column\(") {
            # 检查是否有nullable=False（冗余）
            if ($line -match "nullable\s*=\s*False") {
                $issues += @{
                    Type = "主键定义冗余"
                    File = $FilePath
                    Line = $lineNumber
                    Issue = "主键字段无需设置nullable=False（默认不可空）"
                    Content = $line.Trim()
                    Severity = "Warning"
                    Suggestion = "移除nullable=False参数"
                }
            }
            
            # 检查是否缺少index=True（推荐）
            if ($line -notmatch "index\s*=\s*True") {
                $issues += @{
                    Type = "主键索引缺失"
                    File = $FilePath
                    Line = $lineNumber
                    Issue = "建议为主键添加index=True以提升查询性能"
                    Content = $line.Trim()
                    Severity = "Info"
                    Suggestion = "添加index=True参数"
                }
            }
            
            # 检查主键类型
            if ($line -notmatch "(Integer|BigInteger)") {
                $issues += @{
                    Type = "主键类型不规范"
                    File = $FilePath
                    Line = $lineNumber
                    Issue = "主键应使用Integer或BigInteger类型"
                    Content = $line.Trim()
                    Severity = "Error"
                    Suggestion = "使用Integer或BigInteger类型"
                }
            }
        }
    }
    
    return $issues
}

function Check-ForeignKeyIssues {
    param([string]$FilePath, [array]$Content)
    
    $issues = @()
    $lineNumber = 0
    
    foreach ($line in $Content) {
        $lineNumber++
        
        # 检查外键字段定义
        if ($line -match "Column\(.*ForeignKey" -and $line -match "(\w+)\s*=\s*Column") {
            $fieldName = $matches[1]
            
            # 检查外键命名规范
            if ($fieldName -notmatch "^[a-z][a-z0-9_]*_id$") {
                $issues += @{
                    Type = "外键命名不规范"
                    File = $FilePath
                    Line = $lineNumber
                    Issue = "外键字段应以'_id'结尾: $fieldName"
                    Content = $line.Trim()
                    Severity = "Warning"
                    Suggestion = "使用格式：{table_name}_id"
                }
            }
            
            # 检查是否缺少索引
            if ($line -notmatch "index\s*=\s*True") {
                $issues += @{
                    Type = "外键索引缺失"
                    File = $FilePath
                    Line = $lineNumber
                    Issue = "外键字段缺少索引，可能影响查询性能"
                    Content = $line.Trim()
                    Severity = "Warning"
                    Suggestion = "添加index=True参数"
                }
            }
        }
    }
    
    return $issues
}

function Check-StringFieldIssues {
    param([string]$FilePath, [array]$Content)
    
    $issues = @()
    $lineNumber = 0
    
    foreach ($line in $Content) {
        $lineNumber++
        
        # 检查String字段定义
        if ($line -match "Column\(String[^,)]*[\),]") {
            # 检查是否指定了长度
            if ($line -notmatch "String\(\d+\)") {
                $issues += @{
                    Type = "String字段缺少长度限制"
                    File = $FilePath
                    Line = $lineNumber
                    Issue = "String字段必须指定长度限制"
                    Content = $line.Trim()
                    Severity = "Error"
                    Suggestion = "使用String(length)格式，如String(255)"
                }
            }
        }
    }
    
    return $issues
}

function Check-TimestampFields {
    param([string]$FilePath, [array]$Content)
    
    $issues = @()
    $hasCreatedAt = $false
    $hasUpdatedAt = $false
    $lineNumber = 0
    
    foreach ($line in $Content) {
        $lineNumber++
        
        if ($line -match "created_at\s*=\s*Column") {
            $hasCreatedAt = $true
            
            # 检查时间字段类型和默认值
            if ($line -notmatch "DateTime") {
                $issues += @{
                    Type = "时间字段类型不规范"
                    File = $FilePath
                    Line = $lineNumber
                    Issue = "created_at应使用DateTime类型"
                    Content = $line.Trim()
                    Severity = "Warning"
                    Suggestion = "使用DateTime类型"
                }
            }
            
            if ($line -notmatch "default\s*=") {
                $issues += @{
                    Type = "时间字段缺少默认值"
                    File = $FilePath
                    Line = $lineNumber
                    Issue = "created_at缺少默认值设置"
                    Content = $line.Trim()
                    Severity = "Warning"
                    Suggestion = "添加default=func.now()"
                }
            }
        }
        
        if ($line -match "updated_at\s*=\s*Column") {
            $hasUpdatedAt = $true
            
            if ($line -notmatch "DateTime") {
                $issues += @{
                    Type = "时间字段类型不规范"
                    File = $FilePath
                    Line = $lineNumber
                    Issue = "updated_at应使用DateTime类型"
                    Content = $line.Trim()
                    Severity = "Warning"
                    Suggestion = "使用DateTime类型"
                }
            }
            
            if ($line -notmatch "onupdate\s*=") {
                $issues += @{
                    Type = "更新时间字段配置不完整"
                    File = $FilePath
                    Line = $lineNumber
                    Issue = "updated_at缺少onupdate配置"
                    Content = $line.Trim()
                    Severity = "Warning"
                    Suggestion = "添加onupdate=func.now()"
                }
            }
        }
    }
    
    # 检查表是否包含必需的时间戳字段
    $classDefinitions = $Content | Select-String -Pattern "class\s+(\w+).*Base.*:"
    if ($classDefinitions -and !$hasCreatedAt) {
        $issues += @{
            Type = "缺少创建时间字段"
            File = $FilePath
            Line = 1
            Issue = "数据模型缺少created_at字段"
            Content = "Model Definition"
            Severity = "Info"
            Suggestion = "添加created_at = Column(DateTime, default=func.now())"
        }
    }
    
    if ($classDefinitions -and !$hasUpdatedAt) {
        $issues += @{
            Type = "缺少更新时间字段"
            File = $FilePath
            Line = 1
            Issue = "数据模型缺少updated_at字段"
            Content = "Model Definition"
            Severity = "Info"
            Suggestion = "添加updated_at = Column(DateTime, default=func.now(), onupdate=func.now())"
        }
    }
    
    return $issues
}

function Check-TableNaming {
    param([string]$FilePath, [array]$Content)
    
    $issues = @()
    $lineNumber = 0
    
    foreach ($line in $Content) {
        $lineNumber++
        
        if ($line -match "__tablename__\s*=\s*['""]([^'""]+)['""]") {
            $tableName = $matches[1]
            
            # 检查表名命名规范
            if ($tableName -notmatch "^[a-z][a-z0-9_]*$") {
                $issues += @{
                    Type = "表名命名不规范"
                    File = $FilePath
                    Line = $lineNumber
                    Issue = "表名应使用snake_case格式: $tableName"
                    Content = $line.Trim()
                    Severity = "Error"
                    Suggestion = "使用小写字母和下划线"
                }
            }
            
            # 检查是否使用复数形式（推荐）
            if ($tableName -notmatch "s$" -and $tableName -ne "user_auth" -and $tableName -notmatch "(data|info)$") {
                $issues += @{
                    Type = "表名建议使用复数"
                    File = $FilePath
                    Line = $lineNumber
                    Issue = "建议使用复数形式的表名: $tableName"
                    Content = $line.Trim()
                    Severity = "Info"
                    Suggestion = "考虑使用复数形式，如users, products等"
                }
            }
        }
    }
    
    return $issues
}

function Check-DatabaseModule {
    param([string]$ModulePath, [string]$ModuleName)
    
    Write-ColorOutput "🔍 检查模块: $ModuleName" "Cyan"
    
    $modelFile = Join-Path $ModulePath "models.py"
    if (-not (Test-Path $modelFile)) {
        Write-ColorOutput "  ⚠️  未找到models.py文件" "Yellow"
        return @()
    }
    
    $content = Get-Content $modelFile
    $allIssues = @()
    
    # 执行各项检查
    $allIssues += Check-PrimaryKeyIssues -FilePath $modelFile -Content $content
    $allIssues += Check-ForeignKeyIssues -FilePath $modelFile -Content $content
    $allIssues += Check-StringFieldIssues -FilePath $modelFile -Content $content
    $allIssues += Check-TimestampFields -FilePath $modelFile -Content $content
    $allIssues += Check-TableNaming -FilePath $modelFile -Content $content
    
    if ($allIssues.Count -eq 0) {
        Write-ColorOutput "  ✅ 未发现问题" "Green"
    } else {
        Write-ColorOutput "  ❌ 发现 $($allIssues.Count) 个问题" "Red"
        
        if ($Detailed) {
            foreach ($issue in $allIssues) {
                Write-ColorOutput "    📍 第$($issue.Line)行 [$($issue.Severity)] $($issue.Issue)" "Yellow"
                if ($issue.Content -ne "Model Definition") {
                    Write-ColorOutput "       代码: $($issue.Content)" "Gray"
                }
                Write-ColorOutput "       建议: $($issue.Suggestion)" "Green"
                Write-Host ""
            }
        }
    }
    
    return $allIssues
}

function Main {
    Write-ColorOutput "🗄️ 数据库架构完整性检查工具" "Blue"
    Write-Host "=" -ForegroundColor Blue
    
    $allIssues = @()
    
    if ($ModuleName) {
        # 检查指定模块
        $modulePath = "app/modules/$ModuleName"
        if (Test-Path $modulePath) {
            $allIssues += Check-DatabaseModule -ModulePath $modulePath -ModuleName $ModuleName
        } else {
            Write-ColorOutput "❌ 模块不存在: $ModuleName" "Red"
            exit 1
        }
    } else {
        # 检查所有模块
        $modules = Get-ChildItem -Path "app/modules" -Directory
        
        foreach ($module in $modules) {
            $allIssues += Check-DatabaseModule -ModulePath $module.FullName -ModuleName $module.Name
        }
        
        # 检查共享模型
        $sharedModelsPath = "app/shared/models.py"
        if (Test-Path $sharedModelsPath) {
            Write-ColorOutput "🔍 检查共享模型文件" "Cyan"
            $content = Get-Content $sharedModelsPath
            $sharedIssues = @()
            $sharedIssues += Check-PrimaryKeyIssues -FilePath $sharedModelsPath -Content $content
            $sharedIssues += Check-ForeignKeyIssues -FilePath $sharedModelsPath -Content $content
            $sharedIssues += Check-StringFieldIssues -FilePath $sharedModelsPath -Content $content
            $sharedIssues += Check-TableNaming -FilePath $sharedModelsPath -Content $content
            
            $allIssues += $sharedIssues
            
            if ($sharedIssues.Count -eq 0) {
                Write-ColorOutput "  ✅ 未发现问题" "Green"
            } else {
                Write-ColorOutput "  ❌ 发现 $($sharedIssues.Count) 个问题" "Red"
            }
        }
    }
    
    # 汇总报告
    Write-Host ""
    Write-ColorOutput "📊 检查汇总报告" "Blue"
    Write-Host "=" -ForegroundColor Blue
    
    if ($allIssues.Count -eq 0) {
        Write-ColorOutput "🎉 所有数据库模型都符合最佳实践！" "Green"
    } else {
        # 按严重程度分组
        $errorIssues = $allIssues | Where-Object { $_.Severity -eq "Error" }
        $warningIssues = $allIssues | Where-Object { $_.Severity -eq "Warning" }
        $infoIssues = $allIssues | Where-Object { $_.Severity -eq "Info" }
        
        Write-ColorOutput "❌ 发现 $($allIssues.Count) 个数据库架构问题：" "Red"
        
        if ($errorIssues.Count -gt 0) {
            Write-ColorOutput "  🚨 错误 ($($errorIssues.Count)个):" "Red"
            $errorGroups = $errorIssues | Group-Object Type
            foreach ($group in $errorGroups) {
                Write-ColorOutput "    - $($group.Name): $($group.Count)个" "Red"
            }
        }
        
        if ($warningIssues.Count -gt 0) {
            Write-ColorOutput "  ⚠️  警告 ($($warningIssues.Count)个):" "Yellow"
            $warningGroups = $warningIssues | Group-Object Type
            foreach ($group in $warningGroups) {
                Write-ColorOutput "    - $($group.Name): $($group.Count)个" "Yellow"
            }
        }
        
        if ($infoIssues.Count -gt 0) {
            Write-ColorOutput "  ℹ️  建议 ($($infoIssues.Count)个):" "Cyan"
            $infoGroups = $infoIssues | Group-Object Type
            foreach ($group in $infoGroups) {
                Write-ColorOutput "    - $($group.Name): $($group.Count)个" "Cyan"
            }
        }
        
        Write-Host ""
        Write-ColorOutput "🔧 修复建议：" "Blue"
        Write-ColorOutput "1. 优先修复错误级别的问题" "White"
        Write-ColorOutput "2. 使用 -Detailed 参数查看详细信息" "White"
        Write-ColorOutput "3. 参考SQLAlchemy最佳实践文档" "White"
        
        if ($Fix) {
            Write-ColorOutput "4. 自动修复功能开发中..." "Yellow"
        } else {
            Write-ColorOutput "4. 使用 -Fix 参数尝试自动修复（开发中）" "White"
        }
    }
    
    return $allIssues.Count
}

# 执行主函数
$exitCode = Main
exit $exitCode