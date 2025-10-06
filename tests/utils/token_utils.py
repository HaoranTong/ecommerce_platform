"""
统一的测试JWT Token工具模块
用于确保所有测试中的JWT token格式一致性

设计原则:
1. 统一的token创建接口
2. 符合生产环境的token格式标准
3. 内置格式验证
4. 易于维护和扩展
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.core.auth import create_access_token, decode_token
from app.modules.user_auth.models import User


class TestTokenManager:
    """测试Token管理器 - 确保token格式一致性"""
    
    @staticmethod
    def create_test_token(
        user_id: int,
        expires_delta: Optional[timedelta] = None,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        创建符合标准格式的测试JWT token
        
        Args:
            user_id: 用户ID（必须是整数）
            expires_delta: 过期时间（默认1小时）
            additional_claims: 额外的声明（可选）
            
        Returns:
            str: JWT token字符串
            
        Raises:
            ValueError: 当user_id不是有效整数时
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError(f"user_id must be a positive integer, got: {user_id}")
        
        if expires_delta is None:
            expires_delta = timedelta(hours=1)
        
        # 标准token格式：sub字段为用户ID字符串
        token_data = {"sub": str(user_id)}
        
        # 添加额外声明（如果有）
        if additional_claims:
            token_data.update(additional_claims)
        
        return create_access_token(data=token_data, expires_delta=expires_delta)
    
    @staticmethod
    def create_test_user_token(user: User, **kwargs) -> str:
        """
        从User对象创建测试token
        
        Args:
            user: User模型实例
            **kwargs: 传递给create_test_token的额外参数
            
        Returns:
            str: JWT token字符串
        """
        if not isinstance(user, User):
            raise ValueError(f"Expected User instance, got: {type(user)}")
        
        if not user.id:
            raise ValueError("User must have a valid ID")
        
        return TestTokenManager.create_test_token(user.id, **kwargs)
    
    @staticmethod
    def validate_token_format(token: str) -> Dict[str, Any]:
        """
        验证token格式是否符合标准
        
        Args:
            token: JWT token字符串
            
        Returns:
            Dict[str, Any]: token的payload
            
        Raises:
            ValueError: 当token格式不符合标准时
        """
        try:
            payload = decode_token(token)
        except Exception as e:
            raise ValueError(f"Invalid token format: {e}")
        
        # 检查必需字段
        if "sub" not in payload:
            raise ValueError("Token missing required 'sub' field")
        
        # 检查sub字段格式
        sub = payload.get("sub")
        if not isinstance(sub, str):
            raise ValueError(f"Token 'sub' field must be string, got: {type(sub)}")
        
        # 检查sub是否可以转换为用户ID
        try:
            user_id = int(sub)
            if user_id <= 0:
                raise ValueError(f"Token 'sub' field must be positive integer string, got: {sub}")
        except ValueError:
            raise ValueError(f"Token 'sub' field must be valid integer string, got: {sub}")
        
        return payload
    
    @staticmethod
    def create_test_admin_token(user_id: int = 999999) -> str:
        """
        创建测试管理员token（使用固定ID避免数据库依赖）
        
        Args:
            user_id: 管理员用户ID（默认999999）
            
        Returns:
            str: 管理员JWT token
        """
        return TestTokenManager.create_test_token(
            user_id=user_id,
            additional_claims={"role": "admin"}
        )
    
    @staticmethod
    def create_test_user_token_simple(user_id: int = 888888) -> str:
        """
        创建测试普通用户token（使用固定ID避免数据库依赖）
        
        Args:
            user_id: 普通用户ID（默认888888）
            
        Returns:
            str: 普通用户JWT token
        """
        return TestTokenManager.create_test_token(
            user_id=user_id,
            additional_claims={"role": "user"}
        )


# 便捷函数，兼容现有代码
def create_test_token(user_id: int, **kwargs) -> str:
    """便捷函数：创建测试token"""
    return TestTokenManager.create_test_token(user_id, **kwargs)


def validate_test_token(token: str) -> Dict[str, Any]:
    """便捷函数：验证token格式"""
    return TestTokenManager.validate_token_format(token)


# 常用的测试token模板
TEST_ADMIN_TOKEN = lambda: TestTokenManager.create_test_admin_token()
TEST_USER_TOKEN = lambda: TestTokenManager.create_test_user_token_simple()