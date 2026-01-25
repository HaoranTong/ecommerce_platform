"""
会员系统模块异常定义

定义会员系统相关的业务异常，实现统一的错误码体系。
符合 API 设计标准中的错误码规范。
"""

from typing import Any, Dict, Optional


class MemberSystemException(Exception):
    """会员系统基础异常类"""
    
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class MemberNotFoundException(MemberSystemException):
    """会员信息不存在异常 - MEMBER_001"""
    
    def __init__(self, user_id: Optional[int] = None):
        super().__init__(
            code="MEMBER_001",
            message="会员信息不存在",
            status_code=404,
            details={"user_id": user_id} if user_id else {}
        )


class InsufficientPointsException(MemberSystemException):
    """积分余额不足异常 - MEMBER_002"""
    
    def __init__(self, required: int, available: int):
        super().__init__(
            code="MEMBER_002",
            message="积分余额不足",
            status_code=409,
            details={
                "required_points": required,
                "available_points": available,
                "shortage": required - available
            }
        )


class InvalidLevelUpgradeException(MemberSystemException):
    """无效的等级升级异常 - MEMBER_003"""
    
    def __init__(self, current_level: str, target_level: str, reason: str):
        super().__init__(
            code="MEMBER_003",
            message="无效的等级升级",
            status_code=409,
            details={
                "current_level": current_level,
                "target_level": target_level,
                "reason": reason
            }
        )


class MemberStatusAbnormalException(MemberSystemException):
    """会员状态异常 - MEMBER_004"""
    
    def __init__(self, status: int, user_id: Optional[int] = None):
        status_map = {1: "正常", 2: "冻结", 3: "注销"}
        super().__init__(
            code="MEMBER_004",
            message="会员状态异常",
            status_code=409,
            details={
                "status": status,
                "status_name": status_map.get(status, "未知"),
                "user_id": user_id
            }
        )


class PointsExpiredException(MemberSystemException):
    """积分已过期异常 - MEMBER_005"""
    
    def __init__(self, transaction_id: Optional[int] = None):
        super().__init__(
            code="MEMBER_005",
            message="积分已过期",
            status_code=409,
            details={"transaction_id": transaction_id} if transaction_id else {}
        )


class DuplicatePointOperationException(MemberSystemException):
    """重复的积分操作异常 - MEMBER_006"""
    
    def __init__(self, reference_id: str, reference_type: str):
        super().__init__(
            code="MEMBER_006",
            message="重复的积分操作",
            status_code=409,
            details={
                "reference_id": reference_id,
                "reference_type": reference_type
            }
        )


class MemberAlreadyExistsException(MemberSystemException):
    """会员已存在异常 - MEMBER_007"""
    
    def __init__(self, user_id: int):
        super().__init__(
            code="MEMBER_007",
            message="用户已是会员",
            status_code=409,
            details={"user_id": user_id}
        )


class LevelNotFoundException(MemberSystemException):
    """等级不存在异常 - MEMBER_008"""
    
    def __init__(self, level_id: Optional[int] = None):
        super().__init__(
            code="MEMBER_008",
            message="会员等级不存在",
            status_code=404,
            details={"level_id": level_id} if level_id else {}
        )


class InvalidPointsAmountException(MemberSystemException):
    """无效的积分数量异常 - MEMBER_009"""
    
    def __init__(self, points: int, reason: str):
        super().__init__(
            code="MEMBER_009",
            message="无效的积分数量",
            status_code=400,
            details={
                "points": points,
                "reason": reason
            }
        )


# 导出所有异常类
__all__ = [
    "MemberSystemException",
    "MemberNotFoundException",
    "InsufficientPointsException",
    "InvalidLevelUpgradeException",
    "MemberStatusAbnormalException",
    "PointsExpiredException",
    "DuplicatePointOperationException",
    "MemberAlreadyExistsException",
    "LevelNotFoundException",
    "InvalidPointsAmountException",
]
