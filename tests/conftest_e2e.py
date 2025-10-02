"""
简化测试配置 - 应急隔离和快速验证专用

用途说明：
- 应急隔离：当主 conftest.py (710行) 出现复杂依赖问题时的备用方案
- 快速验证：开发调试时的最小化配置环境
- 故障排除：复杂环境问题时的问题定位工具

使用方法：
1. 应急情况（当主配置出现复杂依赖问题）：
   # 备份主配置
   cp tests/conftest.py tests/conftest_backup.py
   # 使用简化配置替换
   cp tests/conftest_e2e.py tests/conftest.py
   # 运行基础测试
   pytest tests/factories/ -v
   pytest tests/unit/test_models.py -v
   # 恢复主配置
   cp tests/conftest_backup.py tests/conftest.py

2. 快速验证（开发调试时的最小化环境）：
   # 方法1：临时指定配置
   pytest tests/unit/test_user_auth.py --confcutdir=tests -c tests/conftest_e2e.py -v
   # 方法2：单独目录测试
   cd tests && python -m pytest --confcutdir=. -c conftest_e2e.py unit/ -v
   # 方法3：测试特定功能
   pytest tests/smoke/test_basic.py -v  # 使用简化环境

3. 故障排除（问题隔离和定位）：
   # 当主配置文件出现复杂问题时，使用此配置进行问题隔离
   # 帮助确定问题是否来自测试配置本身
   pytest tests/问题测试文件.py --confcutdir=tests/conftest_e2e.py -v

设计原则：
- 符合项目标准：使用 pytest-mock 而非 unittest.mock
- 环境感知：继承主配置的环境适配能力
- 最小化配置：仅提供必要的 fixtures，避免复杂依赖
- 应急备用：保持与主配置的兼容性

注意事项：
- 此文件不是 E2E 测试的默认配置，默认使用 tests/conftest.py
- 仅在应急情况或快速验证时才使用此配置
- 正常情况下应优先使用主配置文件的完整功能

作者: AI Assistant (遵循项目标准化要求)
更新时间: 2025-10-02 (标准化改造)
"""

import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 确保项目根目录在Python路径中
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 继承主配置的环境感知能力
try:
    from tests.conftest import get_smoke_test_config
except ImportError:
    # 如果无法导入主配置，使用默认配置
    def get_smoke_test_config():
        return {
            "database_url": "sqlite:///:memory:",
            "scope": "function",
            "cleanup_mode": "immediate",
            "create_tables": True,
            "description": "简化模式：使用内存数据库"
        }


@pytest.fixture(scope="session")
def simple_test_db():
    """简化的测试数据库fixture - 继承环境感知但保持简化"""
    try:
        # 尝试使用主配置的环境感知，但强制使用内存数据库
        config = get_smoke_test_config()
        print(f"🔍 简化配置: {config['description']}")
        
        # 强制使用内存数据库以保持简化
        engine = create_engine("sqlite:///:memory:", echo=False)
        
        # 如果需要表结构，可以在这里添加，但为了简化暂时跳过
        # from app.core.database import Base
        # Base.metadata.create_all(engine)
        
    except Exception as e:
        print(f"⚠️  使用基础内存数据库: {e}")
        engine = create_engine("sqlite:///:memory:", echo=False)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    engine.dispose()


@pytest.fixture
def mock_factory(mocker):
    """符合标准的Mock工厂 - 使用pytest-mock而非unittest.mock"""
    return mocker.Mock()


@pytest.fixture
def simple_api_client():
    """简化的API客户端 - 仅限应急情况使用"""
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        # 简化的客户端，不进行复杂的依赖覆盖
        return TestClient(app)
    except ImportError as e:
        print(f"⚠️  简化模式：无法创建API客户端 - {e}")
        return None
