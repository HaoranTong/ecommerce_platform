"""
简单的认证测试路由
用于调试认证问题
"""
from fastapi import APIRouter, Depends
from ..auth import get_current_user
from ..models import User

router = APIRouter()

@router.get("/test-auth")
async def test_auth(current_user: User = Depends(get_current_user)):
    """简单的认证测试端点"""
    return {
        "message": "认证成功",
        "user_id": current_user.id,
        "username": current_user.username
    }
