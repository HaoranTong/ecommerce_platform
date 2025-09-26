#!/usr/bin/env python3
"""
测试配置验证脚本
用于验证测试环境配置是否正确，独立于实际测试代码运行

使用方法：
    python tools/validate_test_config.py

验证内容：
1. 虚拟环境检查和激活提示
2. 单元测试配置验证（内存SQLite）
3. 烟雾测试配置验证（文件SQLite）
4. 集成测试配置验证（MySQL连接）
5. 测试依赖包验证
6. 测试fixture功能验证
"""

import sys
import os
import tempfile
import subprocess
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_virtual_environment():
    """检查并处理虚拟环境状态"""
    print("🔍 检查虚拟环境状态")
    print("=" * 50)
    
    # 检查是否在虚拟环境中
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if in_venv:
        print(f"✅ 虚拟环境已激活: {sys.prefix}")
        return True
    
    print(f"❌ 未检测到虚拟环境，当前Python路径: {sys.prefix}")
    print()
    print("🔧 尝试自动激活虚拟环境...")
    
    # 寻找常见的虚拟环境路径
    possible_venv_paths = [
        project_root / "venv",
        project_root / ".venv", 
        project_root / "env",
        project_root / ".env"
    ]
    
    for venv_path in possible_venv_paths:
        if venv_path.exists():
            print(f"📁 发现虚拟环境目录: {venv_path}")
            
            # 检查激活脚本
            if os.name == 'nt':  # Windows
                activate_script = venv_path / "Scripts" / "activate.bat"
                powershell_script = venv_path / "Scripts" / "Activate.ps1"
            else:  # Unix/Linux/Mac
                activate_script = venv_path / "bin" / "activate"
                powershell_script = None
            
            if activate_script.exists() or (powershell_script and powershell_script.exists()):
                print()
                print("⚠️  请手动激活虚拟环境后再运行此脚本：")
                print()
                if os.name == 'nt':  # Windows
                    if powershell_script and powershell_script.exists():
                        print(f"   PowerShell: & '{powershell_script}'")
                    if activate_script.exists():
                        print(f"   Command Prompt: {activate_script}")
                else:
                    print(f"   source {activate_script}")
                print()
                print("然后重新运行：python tools/validate_test_config.py")
                return False
    
    print()
    print("❌ 未找到虚拟环境目录")
    print()
    print("🆘 请先创建虚拟环境：")
    print("   python -m venv venv")
    print("   然后激活虚拟环境：")
    if os.name == 'nt':  # Windows
        print("   PowerShell: venv\\Scripts\\Activate.ps1")
        print("   Command Prompt: venv\\Scripts\\activate.bat")
    else:
        print("   source venv/bin/activate")
    print()
    print("最后安装依赖：")
    print("   pip install -r requirements.txt")
    print("   pip install -r requirements_dev.txt")
    print()
    
    return False

def validate_python_environment():
    """验证Python环境配置"""
    print("=== Python环境验证 ===")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查项目根目录
    if project_root.exists():
        print(f"✅ 项目根目录: {project_root}")
    else:
        print(f"❌ 项目根目录不存在: {project_root}")
        return False
    
    return True

def validate_test_dependencies():
    """验证测试依赖包"""
    print("\n=== 测试依赖包验证 ===")
    
    required_packages = [
        'pytest',
        'pytest-asyncio',
        'sqlalchemy',
        'fastapi',
        'httpx'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - 已安装")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install " + " ".join(missing_packages))
        return False
    
    return True

def validate_unit_test_config():
    """验证单元测试配置（内存SQLite）"""
    print("\n=== 单元测试配置验证 ===")
    
    try:
        # 测试内存数据库连接
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False}
        )
        
        # 测试基本操作
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test_value"))
            test_value = result.fetchone()[0]
            
        if test_value == 1:
            print("✅ SQLite内存数据库连接成功")
        else:
            print("❌ SQLite内存数据库测试失败")
            return False
        
        # 测试会话创建
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        session.close()
        print("✅ 数据库会话创建成功")
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ 单元测试配置验证失败: {e}")
        return False

def validate_smoke_test_config():
    """验证烟雾测试配置（文件SQLite）"""
    print("\n=== 烟雾测试配置验证 ===")
    
    try:
        # 创建测试目录
        test_dir = project_root / "tests"
        test_dir.mkdir(exist_ok=True)
        
        # 测试文件数据库
        test_db_path = test_dir / "smoke_test.db"
        database_url = f"sqlite:///{test_db_path}"
        
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False}
        )
        
        # 测试基本操作
        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY)"))
            conn.execute(text("INSERT INTO test_table (id) VALUES (1)"))
            result = conn.execute(text("SELECT COUNT(*) FROM test_table"))
            count = result.fetchone()[0]
            conn.execute(text("DROP TABLE test_table"))
            conn.commit()
        
        if count >= 1:
            print("✅ SQLite文件数据库操作成功")
        else:
            print("❌ SQLite文件数据库测试失败")
            return False
        
        engine.dispose()
        
        # 清理测试文件
        if test_db_path.exists():
            try:
                test_db_path.unlink()
                print("✅ 测试文件清理成功")
            except PermissionError:
                print("⚠️  测试文件清理跳过（文件可能被其他进程使用）")
        
        return True
        
    except Exception as e:
        print(f"❌ 烟雾测试配置验证失败: {e}")
        return False

def validate_integration_test_config():
    """验证集成测试配置（MySQL）"""
    print("\n=== 集成测试配置验证 ===")
    
    try:
        # MySQL连接URL
        mysql_url = "mysql+pymysql://root:test_password@localhost:3308/ecommerce_platform_test"
        
        try:
            import pymysql
            print("✅ PyMySQL驱动已安装")
        except ImportError:
            print("❌ PyMySQL驱动未安装")
            return False
        
        # 尝试连接MySQL
        try:
            engine = create_engine(mysql_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT VERSION()"))
                version = result.fetchone()[0]
                print(f"✅ MySQL连接成功，版本: {version}")
            engine.dispose()
            return True
        except Exception as mysql_error:
            print(f"⚠️  MySQL测试数据库不可用: {mysql_error}")
            print("  集成测试将在运行时跳过（这是正常的）")
            return True  # MySQL不可用是可接受的
        
    except Exception as e:
        print(f"❌ 集成测试配置验证失败: {e}")
        return False

def validate_app_imports():
    """验证应用模块导入"""
    print("\n=== 应用模块导入验证 ===")
    
    try:
        # 测试核心模块导入
        from app.core.database import Base
        print("✅ 核心数据库模块导入成功")
        
        # 测试主应用导入
        try:
            from app.main import app
            print("✅ 主应用模块导入成功")
        except Exception as app_error:
            print(f"⚠️  主应用导入警告: {app_error}")
        
        # 测试模型导入
        try:
            from app.modules.user_auth.models import User
            print("✅ 用户认证模型导入成功")
        except Exception as model_error:
            print(f"❌ 模型导入失败: {model_error}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 应用模块导入验证失败: {e}")
        return False

def validate_pytest_config():
    """验证pytest配置"""
    print("\n=== pytest配置验证 ===")
    
    try:
        import pytest
        print(f"✅ pytest版本: {pytest.__version__}")
        
        # 检查conftest.py文件
        conftest_path = project_root / "tests" / "conftest.py"
        if conftest_path.exists():
            print("✅ tests/conftest.py文件存在")
        else:
            print("❌ tests/conftest.py文件不存在")
            return False
        
        # 检查测试目录结构
        test_dirs = ["tests/unit", "tests/integration", "tests/e2e"]
        for test_dir in test_dirs:
            dir_path = project_root / test_dir
            if dir_path.exists():
                print(f"✅ {test_dir} 目录存在")
            else:
                print(f"⚠️  {test_dir} 目录不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ pytest配置验证失败: {e}")
        return False

def main():
    """主验证流程"""
    print("🔍 测试环境配置验证开始")
    print("=" * 50)
    
    # 首先检查虚拟环境 - 这是最重要的前置条件
    if not check_virtual_environment():
        print("\n❌ 虚拟环境检查失败，请按照上述提示激活虚拟环境后重试")
        return False
    
    print()  # 添加分隔符
    
    # 验证步骤列表
    validation_steps = [
        ("Python环境", validate_python_environment),
        ("测试依赖包", validate_test_dependencies),
        ("应用模块导入", validate_app_imports),
        ("单元测试配置", validate_unit_test_config),
        ("烟雾测试配置", validate_smoke_test_config),
        ("集成测试配置", validate_integration_test_config),
        ("pytest配置", validate_pytest_config),
    ]
    
    results = []
    for name, validator in validation_steps:
        try:
            result = validator()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}验证时发生异常: {e}")
            results.append((name, False))
    
    # 总结验证结果
    print("\n" + "=" * 50)
    print("🏁 测试环境配置验证总结")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        if result:
            print(f"✅ {name}: 通过")
            passed += 1
        else:
            print(f"❌ {name}: 失败")
            failed += 1
    
    print(f"\n📊 验证结果: {passed}个通过, {failed}个失败")
    
    if failed == 0:
        print("🎉 所有测试环境配置验证通过！可以开始运行测试。")
        return True
    else:
        print("⚠️  存在配置问题，请根据上述错误信息进行修复。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
