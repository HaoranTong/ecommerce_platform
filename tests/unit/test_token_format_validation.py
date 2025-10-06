"""
JWT Token格式验证测试
确保所有token创建都符合标准格式

测试覆盖：
1. 统一工具函数的正确性
2. token格式验证逻辑
3. 错误格式的检测
4. 与现有代码的兼容性
"""

import pytest
from datetime import datetime, timedelta, timezone
from tests.utils.token_utils import (
    TestTokenManager, 
    create_test_token, 
    validate_test_token,
    TEST_ADMIN_TOKEN,
    TEST_USER_TOKEN
)
from app.core.auth import decode_token, create_access_token
from app.modules.user_auth.models import User


class TestJWTTokenFormat:
    """JWT Token格式标准化测试"""
    
    def test_create_test_token_standard_format(self):
        """测试创建标准格式的token"""
        user_id = 12345
        token = create_test_token(user_id)
        
        # 验证token可以正常解析
        payload = decode_token(token)
        
        # 验证sub字段格式正确
        assert payload["sub"] == str(user_id)
        assert isinstance(payload["sub"], str)
        
        # 验证可以转换为整数
        assert int(payload["sub"]) == user_id
    
    def test_create_test_token_with_additional_claims(self):
        """测试创建包含额外声明的token"""
        user_id = 54321
        additional_claims = {"role": "admin", "permissions": ["read", "write"]}
        
        token = create_test_token(user_id, additional_claims=additional_claims)
        payload = decode_token(token)
        
        # 验证标准字段
        assert payload["sub"] == str(user_id)
        
        # 验证额外声明
        assert payload["role"] == "admin"
        assert payload["permissions"] == ["read", "write"]
    
    def test_create_test_token_invalid_user_id(self):
        """测试无效用户ID的错误处理"""
        invalid_ids = [0, -1, "123", None, 3.14]
        
        for invalid_id in invalid_ids:
            with pytest.raises(ValueError, match="user_id must be a positive integer"):
                create_test_token(invalid_id)
    
    def test_validate_token_format_valid_token(self):
        """测试验证有效token格式"""
        user_id = 98765
        token = create_test_token(user_id)
        
        # 验证通过，返回payload
        payload = validate_test_token(token)
        assert payload["sub"] == str(user_id)
    
    def test_validate_token_format_invalid_formats(self):
        """测试检测无效token格式"""
        # 错误格式1：sub字段使用用户名而不是ID
        wrong_token1 = create_access_token(
            data={"sub": "username", "user_id": 123}
        )
        
        with pytest.raises(ValueError, match="must be valid integer string"):
            validate_test_token(wrong_token1)
        
        # 错误格式2：sub字段为整数而不是字符串
        wrong_token2 = create_access_token(data={"sub": 123})
        with pytest.raises(ValueError, match="Invalid token format"):
            validate_test_token(wrong_token2)
        
        # 错误格式3：缺少sub字段
        wrong_token3 = create_access_token(data={"user_id": 123})
        with pytest.raises(ValueError, match="missing required 'sub' field"):
            validate_test_token(wrong_token3)
    
    def test_test_token_manager_create_from_user(self):
        """测试从User对象创建token"""
        # 创建模拟用户
        user = User(
            id=11111,
            username="test_user",
            email="test@example.com",
            is_active=True
        )
        
        token = TestTokenManager.create_test_user_token(user)
        payload = decode_token(token)
        
        assert payload["sub"] == str(user.id)
    
    def test_test_token_manager_invalid_user_object(self):
        """测试无效User对象的错误处理"""
        # 测试非User对象
        with pytest.raises(ValueError, match="Expected User instance"):
            TestTokenManager.create_test_user_token("not_a_user")
        
        # 测试没有ID的User对象
        user_without_id = User(username="test", email="test@example.com")
        with pytest.raises(ValueError, match="User must have a valid ID"):
            TestTokenManager.create_test_user_token(user_without_id)
    
    def test_convenience_token_functions(self):
        """测试便捷token函数"""
        # 测试管理员token
        admin_token = TEST_ADMIN_TOKEN()
        admin_payload = decode_token(admin_token)
        assert admin_payload["role"] == "admin"
        assert int(admin_payload["sub"]) == 999999
        
        # 测试普通用户token
        user_token = TEST_USER_TOKEN()
        user_payload = decode_token(user_token)
        assert user_payload["role"] == "user"
        assert int(user_payload["sub"]) == 888888
    
    def test_token_expiration_handling(self):
        """测试token过期时间处理"""
        user_id = 77777
        custom_expiry = timedelta(minutes=30)
        
        token = create_test_token(user_id, expires_delta=custom_expiry)
        payload = decode_token(token)
        
        # 验证过期时间设置正确（允许2分钟误差，因为有时间戳生成和处理时间）
        expected_exp = datetime.now(timezone.utc) + custom_expiry
        actual_exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        
        time_diff = abs((expected_exp - actual_exp).total_seconds())
        assert time_diff < 120  # 2分钟误差范围内


class TestTokenStandardCompliance:
    """Token标准合规性测试"""
    
    def test_production_login_token_format(self):
        """测试生产登录token格式符合标准"""
        # 模拟生产环境中的token创建
        user_id = 12345
        production_token = create_access_token(data={"sub": str(user_id)})
        
        # 使用我们的验证器验证
        payload = validate_test_token(production_token)
        assert payload["sub"] == str(user_id)
    
    def test_existing_conftest_token_format(self):
        """测试现有conftest.py中的token格式"""
        # 这个测试确保我们的修复是正确的
        user_id = 56789
        
        # 模拟修复后的conftest.py token创建方式
        conftest_token = create_access_token(
            data={"sub": str(user_id)},
            expires_delta=timedelta(hours=1)
        )
        
        # 验证格式正确
        payload = validate_test_token(conftest_token)
        assert payload["sub"] == str(user_id)
        
        # 验证与我们的工具函数创建的token一致
        our_token = create_test_token(user_id)
        our_payload = decode_token(our_token)
        
        # 两者的sub字段应该相同
        assert payload["sub"] == our_payload["sub"]


class TestBackwardCompatibility:
    """向后兼容性测试"""
    
    def test_integration_with_existing_auth_system(self):
        """测试与现有认证系统的集成"""
        user_id = 13579
        
        # 使用我们的工具创建token
        token = create_test_token(user_id)
        
        # 使用现有的认证系统解析
        payload = decode_token(token)
        
        # 验证认证系统能正确提取用户ID
        extracted_user_id = int(payload["sub"])
        assert extracted_user_id == user_id
    
    def test_performance_test_token_compatibility(self):
        """测试与性能测试的兼容性"""
        user_id = 24680
        
        # 创建token
        token = create_test_token(user_id)
        
        # 模拟性能测试中的使用方式
        headers = {"Authorization": f"Bearer {token}"}
        
        # 验证header格式正确
        assert headers["Authorization"].startswith("Bearer ")
        
        # 验证token可以从header中提取和验证
        token_from_header = headers["Authorization"].split(" ")[1]
        payload = validate_test_token(token_from_header)
        assert int(payload["sub"]) == user_id