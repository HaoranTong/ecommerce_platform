"""
用户认证模块依赖项

包含模块特定的依赖注入函数
"""

from fastapi import Depends
from app.core.auth import get_current_user, get_current_active_user


def get_authenticated_user():
    """获取已认证用户"""
    return Depends(get_current_active_user)