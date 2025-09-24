<!--version info: v1.0.0, created: 2025-09-23, level: L2, dependencies: naming-conventions-standards.md,project-structure-standards.md-->

# 脚本管理标准 (Scripts Standards)

## 概述

本文档专门规范DevOps自动化脚本的管理、分类和维护流程，涵盖开发辅助、测试执行、部署管理、文档生成等各类脚本的标准化管理，属于L2领域标准。

## 依赖标准

本标准依赖以下L1核心标准：
- `naming-conventions-standards.md` - 获取PowerShell、Python脚本的统一命名规范
- `project-structure-standards.md` - 获取scripts目录结构和脚本分类管理标准

## 具体标准
创建说明：基于真实项目结构定义DevOps脚本管理标准，规范开发运维自动化流程
-->

⬆️ **脚本命名规范**: 参见 [naming-conventions-standards.md](naming-conventions-standards.md#脚本命名规范) - 脚本文件命名标准
⬆️ **项目结构标准**: 参见 [project-structure-standards.md](project-structure-standards.md#scripts目录结构) - 脚本目录组织
⬆️ **模块命名映射**: 参见 [project-structure-standards.md](project-structure-standards.md#业务模块标准结构)

## 📋 文档说明

本文档定义DevOps脚本管理、自动化工具、开发辅助脚本等标准，基于L1核心标准制定具体的脚本开发和管理规范。

### 🎯 文档职责
- **脚本分类标准**: 开发、测试、部署、检查脚本的分类和组织
- **脚本管理规范**: 脚本分类、版本管理、维护更新标准
- **自动化流程**: CI/CD集成、工作流程自动化规范
- **工具链管理**: 开发工具、检查工具、生成工具的标准化
- **维护和更新**: 脚本版本管理、文档同步、废弃管理

---

## 🗂️ 脚本分类和组织标准

### 脚本功能分类体系
```tree
scripts/
├── README.md                           # 脚本目录说明文档
├── development/                        # 开发辅助脚本
│   ├── dev_env.ps1                    # 开发环境设置
│   ├── dev_tools.ps1                  # 开发工具管理
│   ├── sync_env.ps1                   # 环境同步
│   └── setup_test_env.ps1             # 测试环境搭建
├── testing/                           # 测试相关脚本
│   ├── run_module_tests.ps1           # 模块测试执行
│   ├── integration_test.ps1           # 集成测试
│   ├── smoke_test.ps1                 # 冒烟测试
│   ├── e2e_test_verification.py       # 端到端测试验证
│   └── check_test_env.ps1             # 测试环境检查
├── validation/                        # 脚本验证工具
│   ├── validate_standards.ps1         # 标准文档验证
│   ├── validate_pydantic_v2.py        # 依赖版本验证
│   └── validate_test_config.py        # 配置验证工具
├── database/                          # 数据库管理脚本
│   ├── check_database_schema.ps1      # 数据库架构检查
│   └── rebuild_database.ps1           # 数据库重建
├── documentation/                     # 文档管理脚本
│   ├── check_docs.ps1                 # 文档检查
│   ├── create_module_docs.ps1         # 模块文档生成
│   ├── sync_readme.ps1                # README同步
│   └── generate_test_template.py      # 测试模板生成
├── workflow/                          # 工作流程脚本
│   ├── ai_checkpoint.ps1              # AI检查点
│   ├── dev_checkpoint.ps1             # 开发检查点
│   ├── feature_finish.ps1             # 功能完成流程
│   ├── release_to_main.ps1            # 发布到主分支
│   └── update_module_status.ps1       # 模块状态更新
├── analysis/                          # 分析工具脚本
│   ├── api_service_mapping_analyzer.py # API服务映射分析
│   ├── model_analyzer.py              # 模型分析
│   └── verify_inventory_module.py     # 库存模块验证
└── utilities/                         # 通用工具脚本
    └── log_status.ps1                 # 状态日志记录
```

### 脚本类型和用途定义
| 脚本类型 | 用途范围 | 执行频率 | 权限要求 |
|----------|----------|----------|----------|
| **开发辅助** | 环境设置、工具管理 | 每日/按需 | 开发者 |
| **测试执行** | 自动化测试、验证 | 持续/按需 | 开发者/CI |
| **验证脚本** | 配置验证、环境检查 | 部署前/CI | 运维/CI |
| **数据库管理** | 迁移、备份、重建 | 按需/定时 | 数据库管理员 |
| **文档管理** | 生成、同步、验证 | 提交时/按需 | 开发者/CI |
| **工作流程** | 发布、集成、检查点 | 里程碑/按需 | 项目管理员 |
| **分析工具** | 架构分析、依赖检查 | 定期/按需 | 架构师/开发者 |

## 📝 脚本管理标准

### PowerShell脚本标准模板
```powershell
<#
.SYNOPSIS
脚本功能的简要描述

.DESCRIPTION
脚本的详细功能说明，包括：
- 主要功能和用途
- 执行的具体操作
- 预期的输出结果
- 使用场景和注意事项

.PARAMETER ParameterName
参数说明（如果有参数）

.EXAMPLE
PS> .\script_name.ps1
脚本执行示例和预期输出

.EXAMPLE  
PS> .\script_name.ps1 -Parameter "value"
带参数的执行示例

.NOTES
作者: 开发者姓名
创建日期: 2025-09-23
最后修改: 2025-09-23
版本: 1.0.0
依赖项: 
- PowerShell 5.1+
- 相关模块或工具

.LINK
相关文档链接

#>

# =================================================================
# 脚本配置和全局变量
# =================================================================
[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$Environment = "development",
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose
)

# 设置错误处理
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# 脚本根目录和日志配置
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptRoot
$LogFile = Join-Path $ProjectRoot "logs\$(Get-Date -Format 'yyyyMMdd')_$(Split-Path -Leaf $MyInvocation.MyCommand.Name).log"

# =================================================================
# 日志和输出函数
# =================================================================
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    # 控制台输出
    switch ($Level) {
        "ERROR" { Write-Host $LogMessage -ForegroundColor Red }
        "WARN"  { Write-Host $LogMessage -ForegroundColor Yellow }
        "INFO"  { Write-Host $LogMessage -ForegroundColor Green }
        "DEBUG" { if ($Verbose) { Write-Host $LogMessage -ForegroundColor Cyan } }
    }
    
    # 文件日志
    Add-Content -Path $LogFile -Value $LogMessage -ErrorAction SilentlyContinue
}

function Write-Success {
    param([string]$Message)
    Write-Log -Message "✅ $Message" -Level "INFO"
}

function Write-Error-Log {
    param([string]$Message)
    Write-Log -Message "❌ $Message" -Level "ERROR"
}

function Write-Warning-Log {
    param([string]$Message) 
    Write-Log -Message "⚠️ $Message" -Level "WARN"
}

# =================================================================
# 前置检查函数
# =================================================================
function Test-Prerequisites {
    Write-Log "检查脚本执行前置条件..." "INFO"
    
    # 检查PowerShell版本
    $PSVersion = $PSVersionTable.PSVersion
    if ($PSVersion.Major -lt 5) {
        Write-Error-Log "需要PowerShell 5.0或更高版本，当前版本: $($PSVersion.ToString())"
        exit 1
    }
    
    # 检查项目根目录
    if (-not (Test-Path $ProjectRoot)) {
        Write-Error-Log "项目根目录不存在: $ProjectRoot"
        exit 1
    }
    
    # 检查必需的目录
    $RequiredDirs = @("app", "docs", "scripts")
    foreach ($Dir in $RequiredDirs) {
        $DirPath = Join-Path $ProjectRoot $Dir
        if (-not (Test-Path $DirPath)) {
            Write-Error-Log "必需目录不存在: $DirPath"
            exit 1
        }
    }
    
    Write-Success "前置条件检查通过"
}

# =================================================================
# 主要业务函数
# =================================================================
function Invoke-MainOperation {
    param(
        [string]$OperationName
    )
    
    try {
        Write-Log "开始执行: $OperationName" "INFO"
        
        # 主要业务逻辑在这里实现
        # 示例操作...
        
        Write-Success "操作完成: $OperationName"
        return $true
    }
    catch {
        Write-Error-Log "操作失败: $OperationName - $($_.Exception.Message)"
        return $false
    }
}

# =================================================================
# 主执行流程
# =================================================================
function Main {
    try {
        Write-Log "==================== 脚本开始执行 ====================" "INFO"
        Write-Log "脚本: $($MyInvocation.MyCommand.Name)" "INFO"
        Write-Log "环境: $Environment" "INFO"
        Write-Log "执行时间: $(Get-Date)" "INFO"
        
        # 1. 前置检查
        Test-Prerequisites
        
        # 2. 主要操作
        $Result = Invoke-MainOperation -OperationName "示例操作"
        
        # 3. 结果处理
        if ($Result) {
            Write-Success "脚本执行成功完成"
            exit 0
        } else {
            Write-Error-Log "脚本执行失败"
            exit 1
        }
    }
    catch {
        Write-Error-Log "脚本执行异常: $($_.Exception.Message)"
        Write-Error-Log "堆栈跟踪: $($_.ScriptStackTrace)"
        exit 1
    }
    finally {
        Write-Log "==================== 脚本执行结束 ====================" "INFO"
    }
}

# 脚本入口点
if ($MyInvocation.InvocationName -ne '.') {
    Main
}
```

### Python脚本标准模板
```python
#!/usr/bin/env python3
"""
脚本功能的简要描述

这个脚本实现了[具体功能]，主要用于[使用场景]。
支持[具体功能列表]，并提供[输出内容]。

Usage:
    python script_name.py [options]
    python script_name.py --help

Examples:
    python script_name.py --environment development
    python script_name.py --config config.json --verbose

Requirements:
    - Python 3.8+
    - 依赖包列表

Author: 开发者姓名
Created: 2025-09-23
Modified: 2025-09-23
Version: 1.0.0
"""

import sys
import os
import argparse
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# =================================================================
# 全局配置和常量
# =================================================================
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
LOG_DIR = PROJECT_ROOT / "logs"

# 确保日志目录存在
LOG_DIR.mkdir(exist_ok=True)

# =================================================================
# 日志配置
# =================================================================
def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    配置日志记录
    
    Args:
        verbose: 是否启用详细日志输出
        
    Returns:
        Logger: 配置好的日志记录器
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # 创建日志文件名
    log_filename = f"{datetime.now().strftime('%Y%m%d')}_{Path(__file__).stem}.log"
    log_file = LOG_DIR / log_filename
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 创建Logger
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# =================================================================
# 前置检查函数
# =================================================================
def check_prerequisites() -> bool:
    """
    检查脚本执行的前置条件
    
    Returns:
        bool: 检查是否通过
    """
    logger.info("检查脚本执行前置条件...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        logger.error(f"需要Python 3.8或更高版本，当前版本: {sys.version}")
        return False
    
    # 检查项目结构
    required_dirs = ["app", "docs", "scripts"]
    for dir_name in required_dirs:
        dir_path = PROJECT_ROOT / dir_name
        if not dir_path.exists():
            logger.error(f"必需目录不存在: {dir_path}")
            return False
    
    # 检查必要的文件
    required_files = ["pyproject.toml", "README.md"]
    for file_name in required_files:
        file_path = PROJECT_ROOT / file_name
        if not file_path.exists():
            logger.error(f"必需文件不存在: {file_path}")
            return False
    
    logger.info("✅ 前置条件检查通过")
    return True

# =================================================================
# 主要业务函数
# =================================================================
class ScriptOperations:
    """脚本操作类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化脚本操作
        
        Args:
            config: 脚本配置字典
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def execute_main_operation(self) -> bool:
        """
        执行主要操作
        
        Returns:
            bool: 操作是否成功
        """
        try:
            self.logger.info("开始执行主要操作...")
            
            # 在这里实现主要的业务逻辑
            # 示例操作...
            
            self.logger.info("✅ 主要操作完成")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 操作失败: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("清理资源...")
        # 实现清理逻辑

# =================================================================
# 命令行参数解析
# =================================================================
def parse_arguments() -> argparse.Namespace:
    """
    解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(
        description="脚本功能描述",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s --environment development
  %(prog)s --config config.json --verbose
  %(prog)s --help
        """
    )
    
    parser.add_argument(
        "--environment",
        default="development",
        choices=["development", "testing", "staging", "production"],
        help="运行环境 (默认: development)"
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="启用详细输出"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式，不执行实际操作"
    )
    
    return parser.parse_args()

# =================================================================
# 主执行函数
# =================================================================
def main():
    """主执行函数"""
    global logger
    
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 设置日志
        logger = setup_logging(args.verbose)
        
        logger.info("=" * 60)
        logger.info(f"脚本开始执行: {Path(__file__).name}")
        logger.info(f"执行时间: {datetime.now()}")
        logger.info(f"环境: {args.environment}")
        logger.info(f"试运行: {args.dry_run}")
        logger.info("=" * 60)
        
        # 前置检查
        if not check_prerequisites():
            logger.error("❌ 前置检查失败")
            return 1
        
        # 加载配置
        config = {
            "environment": args.environment,
            "dry_run": args.dry_run
        }
        
        if args.config and args.config.exists():
            with open(args.config, 'r', encoding='utf-8') as f:
                config.update(json.load(f))
        
        # 执行主要操作
        operations = ScriptOperations(config)
        
        try:
            success = operations.execute_main_operation()
            
            if success:
                logger.info("✅ 脚本执行成功完成")
                return 0
            else:
                logger.error("❌ 脚本执行失败")
                return 1
                
        finally:
            operations.cleanup()
            
    except KeyboardInterrupt:
        logger.warning("⚠️ 用户中断脚本执行")
        return 130
    except Exception as e:
        logger.error(f"❌ 脚本执行异常: {e}")
        logger.debug("异常详情:", exc_info=True)
        return 1
    finally:
        logger.info("=" * 60)
        logger.info("脚本执行结束")
        logger.info("=" * 60)

if __name__ == "__main__":
    sys.exit(main())
```

## 🔧 脚本集成和自动化标准

### CI/CD集成规范
```yaml
# =================================================================
# GitHub Actions工作流示例 - .github/workflows/scripts-validation.yml
# =================================================================
name: 脚本验证和部署

on:
  push:
    branches: [dev, main]
  pull_request:
    branches: [main]

jobs:
  script_validation:
    runs-on: ubuntu-latest
    
    steps:
    - name: 检出代码
      uses: actions/checkout@v3
      
    - name: 设置PowerShell环境
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
        
    - name: 验证脚本语法
      run: |
        pwsh -Command "Get-ChildItem scripts/*.ps1 | ForEach-Object { Test-ScriptSyntax $_.FullName }"
        
    - name: 检查脚本文档
      run: |
        python scripts/validation/validate_standards.py -Action format
        
    - name: 环境配置验证
      run: |
        python scripts/validation/validate_test_config.py
```

### 脚本依赖管理
```powershell
# =================================================================
# 脚本依赖检查函数示例
# =================================================================
function Test-ScriptDependencies {
    param(
        [string[]]$RequiredCommands = @(),
        [string[]]$RequiredModules = @(),
        [hashtable]$RequiredVersions = @{}
    )
    
    Write-Log "检查脚本依赖..." "INFO"
    
    # 检查必需的命令
    foreach ($Command in $RequiredCommands) {
        if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
            Write-Error-Log "缺少必需的命令: $Command"
            return $false
        }
    }
    
    # 检查PowerShell模块
    foreach ($Module in $RequiredModules) {
        if (-not (Get-Module -ListAvailable $Module)) {
            Write-Warning-Log "缺少PowerShell模块: $Module，尝试安装..."
            try {
                Install-Module $Module -Force -AllowClobber
                Write-Success "模块安装成功: $Module"
            }
            catch {
                Write-Error-Log "模块安装失败: $Module - $($_.Exception.Message)"
                return $false
            }
        }
    }
    
    # 检查版本要求
    foreach ($Tool in $RequiredVersions.Keys) {
        $RequiredVersion = $RequiredVersions[$Tool]
        try {
            $CurrentVersion = & $Tool --version 2>$null | Select-String -Pattern "\d+\.\d+\.\d+"
            if ($CurrentVersion -and ([Version]$CurrentVersion.Matches[0].Value -lt [Version]$RequiredVersion)) {
                Write-Error-Log "$Tool 版本过低。要求: $RequiredVersion，当前: $($CurrentVersion.Matches[0].Value)"
                return $false
            }
        }
        catch {
            Write-Warning-Log "无法检查 $Tool 版本"
        }
    }
    
    Write-Success "依赖检查通过"
    return $true
}

# 使用示例
$Dependencies = @{
    RequiredCommands = @("git", "python", "docker")
    RequiredModules = @("PSReadLine", "Pester")
    RequiredVersions = @{
        "python" = "3.8.0"
        "git" = "2.30.0"
    }
}

if (-not (Test-ScriptDependencies @Dependencies)) {
    Write-Error-Log "依赖检查失败，脚本无法执行"
    exit 1
}
```

## 📊 脚本执行监控和报告

### 执行结果报告格式
```json
{
  "script_execution": {
    "script_name": "check_code_standards.ps1",
    "execution_id": "exec_20250923_120000",
    "start_time": "2025-09-23T12:00:00Z",
    "end_time": "2025-09-23T12:05:30Z",
    "duration_seconds": 330,
    "status": "success",
    "environment": "development",
    "exit_code": 0
  },
  "execution_context": {
    "user": "developer",
    "machine": "dev-workstation",
    "working_directory": "E:\\ecommerce_platform",
    "parameters": {
      "environment": "development",
      "verbose": true
    }
  },
  "results": {
    "checks_performed": [
      {
        "check_name": "代码格式检查",
        "status": "passed",
        "files_checked": 45,
        "issues_found": 0
      },
      {
        "check_name": "类型注解检查",
        "status": "passed",
        "files_checked": 45,
        "issues_found": 2,
        "details": ["缺少类型注解: app/modules/user_auth/service.py:123"]
      }
    ],
    "summary": {
      "total_checks": 8,
      "passed": 6,
      "warnings": 2,
      "failures": 0
    }
  },
  "resources": {
    "memory_peak_mb": 156,
    "cpu_time_seconds": 45,
    "disk_io_mb": 23
  },
  "logs": {
    "log_file": "logs/20250923_check_code_standards.log",
    "log_level": "INFO",
    "total_log_lines": 234
  }
}
```

### 脚本执行状态追踪
```python
# =================================================================
# 脚本执行状态追踪器
# =================================================================
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class ExecutionResult:
    """脚本执行结果数据类"""
    check_name: str
    status: str  # "passed", "warning", "failed"
    files_checked: int = 0
    issues_found: int = 0
    details: list = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = []

class ScriptExecutionTracker:
    """脚本执行追踪器"""
    
    def __init__(self, script_name: str, environment: str = "development"):
        self.script_name = script_name
        self.environment = environment
        self.execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now(timezone.utc)
        self.results = []
        self.context = {}
        
    def add_result(self, result: ExecutionResult):
        """添加执行结果"""
        self.results.append(result)
    
    def set_context(self, **kwargs):
        """设置执行上下文"""
        self.context.update(kwargs)
    
    def generate_report(self, exit_code: int = 0) -> Dict[str, Any]:
        """生成执行报告"""
        end_time = datetime.now(timezone.utc)
        duration = (end_time - self.start_time).total_seconds()
        
        # 统计结果
        summary = {
            "total_checks": len(self.results),
            "passed": len([r for r in self.results if r.status == "passed"]),
            "warnings": len([r for r in self.results if r.status == "warning"]),
            "failures": len([r for r in self.results if r.status == "failed"])
        }
        
        status = "success" if exit_code == 0 and summary["failures"] == 0 else "failed"
        
        report = {
            "script_execution": {
                "script_name": self.script_name,
                "execution_id": self.execution_id,
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": int(duration),
                "status": status,
                "environment": self.environment,
                "exit_code": exit_code
            },
            "execution_context": self.context,
            "results": {
                "checks_performed": [asdict(r) for r in self.results],
                "summary": summary
            }
        }
        
        return report
    
    def save_report(self, report_dir: Path, exit_code: int = 0):
        """保存执行报告"""
        report = self.generate_report(exit_code)
        
        report_file = report_dir / f"{self.execution_id}_{self.script_name}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report_file

# 使用示例
tracker = ScriptExecutionTracker("check_code_standards", "development")
tracker.set_context(
    user=os.getenv("USERNAME", "unknown"),
    working_directory=str(Path.cwd()),
    parameters={"verbose": True}
)

# 添加检查结果
result1 = ExecutionResult(
    check_name="代码格式检查",
    status="passed",
    files_checked=45,
    issues_found=0
)
tracker.add_result(result1)

# 保存报告
report_file = tracker.save_report(Path("reports"), exit_code=0)
```

## 🚀 脚本维护和更新标准

### 版本管理规范
- **版本标识**: 所有脚本使用语义化版本 `v{major}.{minor}.{patch}`
- **变更记录**: 脚本头部维护变更历史记录
- **向后兼容**: 主版本内保持参数接口的向后兼容性
- **废弃管理**: 废弃脚本保留6个月过渡期，并提供迁移指导

### 文档同步要求
- **脚本文档**: 每个脚本必须有对应的README说明
- **参数文档**: 所有参数必须有详细说明和示例
- **依赖文档**: 清晰列出所有依赖项和版本要求
- **故障排除**: 提供常见问题和解决方案

### 质量保证检查点
1. **代码审查**: 所有脚本变更必须经过代码审查
2. **测试验证**: 在多个环境中测试脚本功能
3. **性能检查**: 监控脚本执行时间和资源消耗
4. **安全审计**: 检查脚本中的安全风险和敏感信息

---

## ❌ 脚本开发禁止项

### 绝对禁止的行为
- 在脚本中硬编码密码、API密钥等敏感信息
- 使用`rm -rf`或类似的危险删除命令
- 不进行错误检查的文件操作
- 在生产环境执行未经测试的脚本
- 修改系统关键文件或注册表
- 使用不安全的网络下载或执行远程代码

### 强制要求
- 所有脚本必须有完整的帮助文档
- 必须实现适当的错误处理和日志记录
- 必须进行前置条件检查
- 必须提供试运行模式
- 必须遵循最小权限原则
