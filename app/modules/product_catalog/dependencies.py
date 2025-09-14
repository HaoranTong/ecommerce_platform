"""
商品管理模块依赖项
"""

from fastapi import Depends
from app.core.auth import get_current_admin_user


def get_admin_user():
    """获取管理员用户（商品管理需要管理员权限）"""
    return Depends(get_current_admin_user)