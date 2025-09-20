"""
简化的conftest.py用于端到端测试验证
避免复杂依赖，专注测试核心功能
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


@pytest.fixture(scope="session")
def simple_test_db():
    """简单的测试数据库fixture"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # 这里可以添加表创建逻辑，但为了简化暂时跳过
    # from app.shared.models import Base
    # Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    engine.dispose()


@pytest.fixture
def mock_factory():
    """Mock工厂fixture"""
    from unittest.mock import Mock
    return Mock()
