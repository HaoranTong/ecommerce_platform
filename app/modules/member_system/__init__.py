"""
会员系统模块

提供完整的会员管理功能，包括会员档案、积分管理、等级系统等。
遵循四层架构设计：Router → Service → Repository → Model
"""

from .router import router
from .models import MemberProfile, MemberLevel, MemberPoint, PointTransaction
from .schemas import (
    MemberProfileCreate,
    MemberProfileUpdate,
    MemberProfileRead,
    PointEarnRequest,
    PointUseRequest,
    PointTransactionRead,
    PointBalanceRead,
    MemberLevelRead,
)
from .service import MemberService, PointService, LevelService
from .repository import MemberRepository, PointRepository, LevelRepository
from .dependencies import (
    get_member_service,
    get_point_service,
    get_level_service,
    get_current_active_user,
    get_current_member_user,
)

__version__ = "1.0.0"
__description__ = "会员系统模块 - 提供会员档案、积分、等级管理功能"

__all__ = [
    # 路由
    "router",
    
    # 模型
    "MemberProfile",
    "MemberLevel", 
    "MemberPoint",
    "PointTransaction",
    
    # 数据模式
    "MemberProfileCreate",
    "MemberProfileUpdate",
    "MemberProfileRead",
    "PointEarnRequest",
    "PointUseRequest",
    "PointTransactionRead",
    "PointBalanceRead",
    "MemberLevelRead",
    
    # 服务层
    "MemberService",
    "PointService",
    "LevelService",
    
    # 仓储层
    "MemberRepository",
    "PointRepository", 
    "LevelRepository",
    
    # 依赖注入
    "get_member_service",
    "get_point_service",
    "get_level_service",
    "get_current_active_user",
    "get_current_member_user",
]