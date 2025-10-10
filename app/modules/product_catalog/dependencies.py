"""
商品管理模块依赖项
"""

from fastapi import Depends

from app.core.auth import get_current_admin_user


def require_admin():
    """依赖注入：仅管理员可访问"""
    return get_current_admin_user  # 返回函数本身，不是Depends对象
