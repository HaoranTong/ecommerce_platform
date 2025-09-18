"""
用户认证模块单元测试
测试账户锁定、登录验证等核心功能
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 直接导入认证模块的模型和函数，避免加载整个应用
from app.modules.user_auth.models import Base, User
from app.core.auth import (
    get_password_hash, 
    verify_password,
    is_account_locked,
    increment_failed_attempts,
    reset_failed_attempts
)

# 注释：使用 conftest.py 中的标准 fixture

@pytest.fixture
def test_user(unit_test_db):
    """测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
        is_active=True,
        role="user",
        status="active",
        failed_login_attempts=0
    )
    unit_test_db.add(user)
    unit_test_db.commit()
    unit_test_db.refresh(user)
    return user

class TestAccountLocking:
    """账户锁定功能测试"""
    
    def test_account_not_locked_initially(self, test_user):
        """测试账户初始状态不被锁定"""
        assert not is_account_locked(test_user)
        assert test_user.failed_login_attempts == 0
        assert test_user.locked_until is None
    
    def test_increment_failed_attempts(self, unit_test_db, test_user):
        """测试增加失败次数"""
        initial_attempts = test_user.failed_login_attempts
        increment_failed_attempts(unit_test_db, test_user)
        
        assert test_user.failed_login_attempts == initial_attempts + 1
        assert test_user.status == "active"  # 未达到锁定阈值
    
    def test_account_locked_after_max_attempts(self, unit_test_db, test_user):
        """测试达到最大失败次数后账户被锁定"""
        # 模拟5次失败登录
        for _ in range(5):
            increment_failed_attempts(unit_test_db, test_user)
        
        assert test_user.failed_login_attempts == 5
        assert test_user.status == "locked"
        assert test_user.locked_until is not None
        assert is_account_locked(test_user)
    
    def test_expired_lock_allows_login(self, test_user):
        """测试过期的锁定允许登录"""
        # 设置已过期的锁定时间
        test_user.locked_until = datetime.utcnow() - timedelta(minutes=1)
        
        assert not is_account_locked(test_user)
    
    def test_reset_failed_attempts_on_successful_login(self, unit_test_db, test_user):
        """测试成功登录重置失败次数"""
        # 设置一些失败次数
        test_user.failed_login_attempts = 3
        unit_test_db.commit()
        
        # 重置失败次数
        reset_failed_attempts(unit_test_db, test_user)
        
        assert test_user.failed_login_attempts == 0
        assert test_user.locked_until is None

class TestPasswordSecurity:
    """密码安全功能测试"""
    
    def test_password_hashing(self):
        """测试密码哈希功能"""
        password = "testpass123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpass", hashed)
    
    def test_password_verification(self):
        """测试密码验证功能"""
        password = "secretpass456"
        hashed = get_password_hash(password)
        
        # 正确密码验证
        assert verify_password(password, hashed)
        
        # 错误密码验证
        assert not verify_password("wrongpass", hashed)
        assert not verify_password("", hashed)
        assert not verify_password("secretpass", hashed)

class TestUserModel:
    """用户模型测试"""
    
    def test_user_creation(self, unit_test_db):
        """测试用户创建"""
        user = User(
            username="newuser",
            email="newuser@example.com",
            password_hash=get_password_hash("newpass123"),
            is_active=True,
            role="user"
        )
        
        unit_test_db.add(user)
        unit_test_db.commit()
        unit_test_db.refresh(user)
        
        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.is_active is True
        assert user.role == "user"
        assert user.status == "active"  # 默认值
        assert user.failed_login_attempts == 0  # 默认值
    
    def test_user_repr(self, test_user):
        """测试用户字符串表示"""
        repr_str = repr(test_user)
        assert "User" in repr_str
        assert str(test_user.id) in repr_str
        assert test_user.username in repr_str
        assert test_user.email in repr_str
