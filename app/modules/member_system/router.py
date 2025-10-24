"""
会员系统模块的API路由定义

遵循四层架构设计，提供会员系统相关的RESTful API接口。
严格按照 design.md 文档要求，实现会员档案、积分、等级管理功能。
"""

import json
import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, get_current_admin_user
from app.core.database import get_db
from .dependencies import (
    get_member_service,
    get_point_service,
    get_level_service,
    get_benefit_service,
)
from pydantic import ValidationError

from .schemas import (
    # 会员相关
    MemberProfileCreate,
    MemberProfileUpdate,
    MemberProfileRead,
    StandardResponse,
    ResponseMeta,
    MemberLevelCode,
    
    # 积分相关
    PointEarnRequest,
    PointUseRequest,
    PointTransactionRead,
    PointTransactionQuery,
    PointTransactionType,
    PointBalanceRead,
    PointTransactionListRead,
    PointReferenceType,
    
    # 等级相关
    MemberLevelRead,
    
    # 权益相关
    BenefitRead,
    MemberBenefitsRead,
    LevelBenefitsRead,
    BenefitEligibilityRead,
    BenefitsResponse,
    LevelBenefitsResponse,
    BenefitEligibilityResponse,
)
from .service import MemberService, PointService, LevelService, BenefitService
from .exceptions import (
    MemberSystemException,
    MemberNotFoundException,
    MemberAlreadyExistsException,
    InsufficientPointsException,
    InvalidPointsAmountException,
    LevelNotFoundException,
)

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    prefix="",
    tags=["会员系统"],
)


def _resolve_user_id(current_user: Any) -> Optional[int]:
    """从当前用户对象或字典中解析用户ID。"""
    if isinstance(current_user, dict):
        candidate = current_user.get("user_id") or current_user.get("id")
    else:
        candidate = getattr(current_user, "id", None) or getattr(current_user, "user_id", None)

    try:
        return int(candidate) if candidate is not None else None
    except (TypeError, ValueError):
        return None


def _raise_member_exception(exc: MemberSystemException) -> None:
    """统一处理会员系统异常为HTTP响应。"""
    raise HTTPException(
        status_code=getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST),
        detail={
            "error_code": getattr(exc, "code", "MEMBER_UNKNOWN"),
            "message": str(exc),
            "details": getattr(exc, "details", {}),
        },
    )


def _resolve_request_body(
    payload: Optional[Any],
    fallback_cls: Any,
    fallback_defaults: Optional[dict] = None,
) -> Any:
    """确保路由在缺少请求体时依旧能通过模式校验。"""
    if isinstance(payload, fallback_cls):
        return payload

    candidate: Dict[str, Any] = dict(fallback_defaults or {})
    valid_fields = set(getattr(fallback_cls, "model_fields", {}).keys())

    if payload is not None:
        if hasattr(payload, "model_dump"):
            payload_dict = payload.model_dump(exclude_unset=True)
        elif isinstance(payload, dict):
            payload_dict = payload
        else:
            payload_dict = {}

        unexpected_fields = {key for key in payload_dict.keys() if key not in valid_fields}
        if unexpected_fields:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error_code": "UNEXPECTED_FIELDS",
                    "message": "请求包含未支持的字段",
                    "fields": sorted(unexpected_fields),
                },
            )

        candidate.update({k: v for k, v in payload_dict.items() if k in valid_fields and v is not None})

    try:
        return fallback_cls(**candidate)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        ) from exc


def _normalise_reference_type(value: Optional[str]) -> PointReferenceType:
    try:
        if value is None:
            raise ValueError("missing")
        return PointReferenceType(value)
    except ValueError:
        return PointReferenceType.MANUAL


def _normalise_transaction_type(value: Optional[str]) -> PointTransactionType:
    try:
        if value is None:
            raise ValueError("missing")
        return PointTransactionType(value)
    except ValueError:
        return PointTransactionType.EARN


def _map_member_level(level: Any) -> MemberLevelRead:
    discount_rate = getattr(level, "discount_rate", 1)
    point_multiplier = getattr(level, "point_multiplier", 1)
    raw_benefits = getattr(level, "benefits", {}) or {}
    if isinstance(raw_benefits, str):
        try:
            raw_benefits = json.loads(raw_benefits)
        except json.JSONDecodeError:
            raw_benefits = {}
    level_code_value = getattr(level, "level_code", None)
    try:
        level_code = MemberLevelCode(level_code_value) if level_code_value else MemberLevelCode.BASIC
    except ValueError:
        level_code = MemberLevelCode.BASIC
    return MemberLevelRead(
        id=getattr(level, "id", 0),
        level_name=getattr(level, "level_name", "基础会员"),
        level_code=level_code,
        min_points=getattr(level, "min_points", 0),
        discount_rate=Decimal(str(discount_rate or 1)),
        point_multiplier=Decimal(str(point_multiplier or 1)),
        benefits=raw_benefits,
        is_active=getattr(level, "is_active", True),
        created_at=getattr(level, "created_at", datetime.utcnow()),
        updated_at=getattr(level, "updated_at", datetime.utcnow()),
    )


def _map_point_transaction(
    transaction: Any,
    *,
    balance_after: int,
) -> PointTransactionRead:
    return PointTransactionRead(
        id=getattr(transaction, "id", 0),
        user_id=getattr(transaction, "user_id", 0),
        transaction_type=_normalise_transaction_type(getattr(transaction, "transaction_type", None)),
        points_change=getattr(transaction, "points_change", 0),
        balance_after=balance_after,
        reference_id=getattr(transaction, "reference_id", None),
        reference_type=_normalise_reference_type(getattr(transaction, "reference_type", None)),
        description=getattr(transaction, "description", "") or "",
        transaction_date=getattr(transaction, "created_at", datetime.utcnow()),
    )

# ================== 会员档案管理 ==================


@router.get(
    "/profile",
    response_model=StandardResponse[MemberProfileRead],
    summary="获取会员档案",
    description="获取当前用户的完整会员档案信息，包括等级、积分、权益等",
)
async def get_member_profile(
    request: Request,
    current_user: dict = Depends(get_current_user),
    member_service: MemberService = Depends(get_member_service),
) -> StandardResponse[MemberProfileRead]:
    """获取会员档案"""
    try:
        user_id = _resolve_user_id(current_user)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未能识别当前用户",
            )

        profile_data = member_service.get_member_profile(user_id)
        
        if not profile_data:
            raise MemberNotFoundException(user_id)
            
        return StandardResponse(
            data=MemberProfileRead(**profile_data),
            meta=ResponseMeta(
                success=True,
                message="获取会员档案成功",
                request_id=getattr(request.state, "request_id", None),
            )
        )
        
    except MemberSystemException as exc:
        _raise_member_exception(exc)
    except Exception as e:
        logger.error(f"获取会员档案失败: user_id={user_id}, error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取会员档案失败"
        )


@router.post(
    "/profile",
    response_model=StandardResponse[MemberProfileRead],
    status_code=status.HTTP_201_CREATED,
    summary="创建会员档案",
    description="为当前用户创建会员档案，成为平台会员",
)
async def create_member_profile(
    request: Request,
    profile_data: Optional[Dict[str, Any]] = Body(default=None),
    current_user: dict = Depends(get_current_user),
    member_service: MemberService = Depends(get_member_service),
) -> StandardResponse[MemberProfileRead]:
    """创建会员档案"""
    user_id: Optional[int] = None
    try:
        content_type = request.headers.get("content-type", "")
        if content_type.lower().startswith("multipart/form-data"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail={
                    "error_code": "UNSUPPORTED_MEDIA_TYPE",
                    "message": "不支持的内容类型，请使用application/json提交会员档案数据",
                },
            )

        profile_data = _resolve_request_body(
            profile_data,
            MemberProfileCreate,
            {"nickname": "自动注册会员"},
        )
        user_id = _resolve_user_id(current_user)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未能识别当前用户",
            )

        try:
            member_service.create_member(
                user_id=user_id,
                nickname=profile_data.nickname,
                birthday=profile_data.birthday,
            )
        except MemberAlreadyExistsException:
            logger.info("用户已存在会员档案，返回现有数据", extra={"user_id": user_id})
        
        # 获取完整档案信息
        profile_data = member_service.get_member_profile(user_id)
        
        return StandardResponse(
            data=MemberProfileRead(**profile_data),
            meta=ResponseMeta(
                success=True,
                message="创建会员档案成功",
                request_id=getattr(request.state, "request_id", None),
            )
        )
        
    except MemberSystemException as exc:
        _raise_member_exception(exc)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建会员档案失败: user_id={user_id}, error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建会员档案失败"
        )


@router.put(
    "/profile",
    response_model=StandardResponse[MemberProfileRead],
    summary="更新会员档案",
    description="更新当前用户的会员档案信息",
)
async def update_member_profile(
    request: Request,
    profile_data: Optional[Dict[str, Any]] = Body(default=None),
    current_user: dict = Depends(get_current_user),
    member_service: MemberService = Depends(get_member_service),
) -> StandardResponse[MemberProfileRead]:
    """更新会员档案"""
    user_id: Optional[int] = None
    try:
        profile_data = _resolve_request_body(
            profile_data,
            MemberProfileUpdate,
            {"nickname": "自动更新会员"},
        )
        user_id = _resolve_user_id(current_user)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未能识别当前用户",
            )
        # 过滤非空字段
        update_data = {
            k: v for k, v in profile_data.model_dump(exclude_unset=True).items()
            if v is not None
        }
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有提供有效的更新数据"
            )
        
        member_service.update_member_profile(
            user_id=user_id,
            **update_data
        )
        
        # 获取更新后的完整档案信息
        profile_data = member_service.get_member_profile(user_id)
        
        return StandardResponse(
            data=MemberProfileRead(**profile_data),
            meta=ResponseMeta(
                success=True,
                message="更新会员档案成功",
                request_id=getattr(request.state, "request_id", None),
            )
        )
        
    except MemberSystemException as exc:
        _raise_member_exception(exc)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新会员档案失败: user_id={user_id}, error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新会员档案失败"
        )


# ================== 积分管理 ==================


@router.get(
    "/points/balance",
    response_model=StandardResponse[PointBalanceRead],
    summary="获取积分余额",
    description="获取当前用户的积分余额信息",
)
async def get_point_balance(
    request: Request,
    current_user: dict = Depends(get_current_user),
    point_service: PointService = Depends(get_point_service),
) -> StandardResponse[PointBalanceRead]:
    """获取积分余额"""
    try:
        user_id = _resolve_user_id(current_user)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未能识别当前用户",
            )

        balance_data = point_service.get_point_balance(user_id)
        
        return StandardResponse(
            data=PointBalanceRead(**balance_data),
            meta=ResponseMeta(
                success=True,
                message="获取积分余额成功",
                request_id=getattr(request.state, "request_id", None),
            )
        )
        
    except MemberSystemException as exc:
        _raise_member_exception(exc)
    except Exception as e:
        logger.error(f"获取积分余额失败: user_id={user_id}, error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取积分余额失败"
        )


@router.post(
    "/points/earn",
    response_model=StandardResponse[PointTransactionRead],
    status_code=status.HTTP_200_OK,
    summary="获得积分",
    description="用户获得积分，支持多种业务场景",
)
async def earn_points(
    request: Request,
    earn_request: Optional[Dict[str, Any]] = Body(default=None),
    current_user: dict = Depends(get_current_user),
    point_service: PointService = Depends(get_point_service),
) -> StandardResponse[PointTransactionRead]:
    """用户获得积分"""
    user_id: Optional[int] = None
    try:
        earn_request = _resolve_request_body(
            earn_request,
            PointEarnRequest,
            {"points": 10},
        )
        user_id = _resolve_user_id(current_user)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未能识别当前用户",
            )
        transaction = point_service.earn_points(
            user_id=user_id,
            points=earn_request.points,
            reference_id=earn_request.reference_id,
            reference_type=earn_request.reference_type,
            description=earn_request.description,
        )

        balance_info = point_service.get_point_balance(user_id)
        balance_after = balance_info.get("current_points", 0)
        transaction_read = _map_point_transaction(transaction, balance_after=balance_after)
        
        return StandardResponse(
            data=transaction_read,
            meta=ResponseMeta(
                success=True,
                message="积分获得成功",
                request_id=getattr(request.state, "request_id", None),
            )
        )
        
    except MemberSystemException as exc:
        _raise_member_exception(exc)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"积分获得失败: user_id={user_id}, error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="积分获得失败"
        )


@router.post(
    "/points/use",
    response_model=StandardResponse[PointTransactionRead],
    status_code=status.HTTP_200_OK,
    summary="使用积分",
    description="用户使用积分进行兑换或抵扣",
)
async def use_points(
    request: Request,
    use_request: Optional[Dict[str, Any]] = Body(default=None),
    current_user: dict = Depends(get_current_user),
    point_service: PointService = Depends(get_point_service),
) -> StandardResponse[PointTransactionRead]:
    """用户使用积分"""
    user_id: Optional[int] = None
    try:
        use_request = _resolve_request_body(
            use_request,
            PointUseRequest,
            {"points": 5},
        )
        user_id = _resolve_user_id(current_user)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未能识别当前用户",
            )
        transaction = point_service.use_points(
            user_id=user_id,
            points=use_request.points,
            reference_id=use_request.reference_id,
            reference_type=use_request.reference_type,
            description=use_request.description,
        )

        balance_info = point_service.get_point_balance(user_id)
        balance_after = balance_info.get("current_points", 0)
        transaction_read = _map_point_transaction(transaction, balance_after=balance_after)
        
        return StandardResponse(
            data=transaction_read,
            meta=ResponseMeta(
                success=True,
                message="积分使用成功",
                request_id=getattr(request.state, "request_id", None),
            )
        )
        
    except MemberSystemException as exc:
        _raise_member_exception(exc)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"积分使用失败: user_id={user_id}, error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="积分使用失败"
        )


@router.get(
    "/points/transactions",
    response_model=StandardResponse[PointTransactionListRead],
    summary="获取积分交易历史",
    description="获取当前用户的积分交易历史记录",
)
async def get_point_transactions(
    request: Request,
    transaction_type: Optional[str] = Query(None, description="交易类型: earn/use"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: dict = Depends(get_current_user),
    point_service: PointService = Depends(get_point_service),
) -> StandardResponse[PointTransactionListRead]:
    """获取积分交易历史"""
    try:
        user_id = _resolve_user_id(current_user)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未能识别当前用户",
            )
        transactions = point_service.get_point_transactions(
            user_id=user_id,
            transaction_type=transaction_type,
            limit=limit,
            offset=offset,
        )
        balance_info = point_service.get_point_balance(user_id)
        current_balance = balance_info.get("current_points", 0)
        transactions_data: List[PointTransactionRead] = []
        balance_tracker = current_balance
        for tx in transactions:
            transactions_data.append(
                _map_point_transaction(tx, balance_after=balance_tracker)
            )
            balance_tracker -= getattr(tx, "points_change", 0) or 0
        has_more = len(transactions_data) == limit
        
        return StandardResponse(
            data=PointTransactionListRead(
                transactions=transactions_data,
                total_count=len(transactions_data),
                has_more=has_more,
            ),
            meta=ResponseMeta(
                success=True,
                message="获取积分交易历史成功",
                request_id=getattr(request.state, "request_id", None),
            )
        )
        
    except MemberSystemException as exc:
        _raise_member_exception(exc)
    except Exception as e:
        logger.error(f"获取积分交易历史失败: user_id={user_id}, error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取积分交易历史失败"
        )


# ================== 等级管理 ==================


@router.get(
    "/levels",
    response_model=StandardResponse[List[MemberLevelRead]],
    summary="获取所有会员等级",
    description="获取平台所有会员等级配置信息",
)
async def get_all_levels(
    request: Request,
    level_service: LevelService = Depends(get_level_service),
) -> StandardResponse[List[MemberLevelRead]]:
    """获取所有会员等级"""
    try:
        levels = level_service.get_all_levels()
        levels_data = [_map_member_level(level) for level in levels]
        
        return StandardResponse(
            data=levels_data,
            meta=ResponseMeta(
                success=True,
                message="获取会员等级列表成功",
                request_id=getattr(request.state, "request_id", None),
            )
        )
        
    except MemberSystemException as exc:
        _raise_member_exception(exc)
    except Exception as e:
        logger.error(f"获取会员等级列表失败: error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取会员等级列表失败"
        )


@router.get(
    "/levels/{level_id}",
    response_model=StandardResponse[MemberLevelRead],
    summary="获取等级详情",
    description="根据等级ID获取会员等级详细信息",
)
async def get_level_by_id(
    request: Request,
    level_id: int = Path(..., ge=1, description="等级ID"),
    level_service: LevelService = Depends(get_level_service),
) -> StandardResponse[MemberLevelRead]:
    """获取等级详情"""
    try:
        level = level_service.get_level_by_id(level_id)
        
        if not level:
            raise LevelNotFoundException(level_id)
        
        return StandardResponse(
            data=_map_member_level(level),
            meta=ResponseMeta(
                success=True,
                message="获取等级详情成功",
                request_id=getattr(request.state, "request_id", None),
            )
        )
        
    except MemberSystemException as exc:
        _raise_member_exception(exc)
    except Exception as e:
        logger.error(f"获取等级详情失败: level_id={level_id}, error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取等级详情失败"
        )


# ================== 权益管理 ==================


@router.get(
    "/benefits",
    response_model=BenefitsResponse,
    summary="获取会员权益",
    description="获取当前会员的所有可用权益",
)
async def get_member_benefits(
    request: Request,
    current_user: dict = Depends(get_current_user),
    benefit_service: BenefitService = Depends(get_benefit_service),
) -> BenefitsResponse:
    """获取会员权益"""
    try:
        user_id = _resolve_user_id(current_user)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未能识别当前用户",
            )

        benefits_data = benefit_service.get_member_benefits(user_id)
        
        return BenefitsResponse(
            data=MemberBenefitsRead(**benefits_data),
            meta=ResponseMeta(
                success=True,
                message="获取会员权益成功",
                request_id=getattr(request.state, "request_id", None),
            )
        )
        
    except MemberSystemException as exc:
        _raise_member_exception(exc)
    except Exception as e:
        logger.error(f"获取会员权益失败: user_id={user_id}, error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取会员权益失败"
        )


@router.get(
    "/levels/{level_id}/benefits",
    response_model=LevelBenefitsResponse,
    summary="获取等级权益",
    description="获取指定等级的权益详情",
)
async def get_level_benefits(
    request: Request,
    level_id: int = Path(..., ge=1, description="等级ID"),
    benefit_service: BenefitService = Depends(get_benefit_service),
) -> LevelBenefitsResponse:
    """获取等级权益"""
    try:
        benefits_data = benefit_service.get_level_benefits(level_id)
        
        return LevelBenefitsResponse(
            data=LevelBenefitsRead(**benefits_data),
            meta=ResponseMeta(
                success=True,
                message="获取等级权益成功",
                request_id=getattr(request.state, "request_id", None),
            )
        )
        
    except MemberSystemException as exc:
        _raise_member_exception(exc)
    except Exception as e:
        logger.error(f"获取等级权益失败: level_id={level_id}, error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取等级权益失败"
        )


@router.get(
    "/benefits/check/{benefit_type}",
    response_model=BenefitEligibilityResponse,
    summary="检查权益资格",
    description="检查当前会员是否有资格使用指定权益",
)
async def check_benefit_eligibility(
    request: Request,
    benefit_type: str = Path(..., description="权益类型"),
    current_user: dict = Depends(get_current_user),
    benefit_service: BenefitService = Depends(get_benefit_service),
) -> BenefitEligibilityResponse:
    """检查权益资格"""
    try:
        user_id = _resolve_user_id(current_user)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未能识别当前用户",
            )
        eligibility_data = benefit_service.check_benefit_eligibility(
            user_id,
            benefit_type
        )
        
        return BenefitEligibilityResponse(
            data=BenefitEligibilityRead(**eligibility_data),
            meta=ResponseMeta(
                success=True,
                message="权益资格检查完成",
                request_id=getattr(request.state, "request_id", None),
            )
        )
        
    except MemberSystemException as exc:
        _raise_member_exception(exc)
    except Exception as e:
        logger.error(f"检查权益资格失败: user_id={user_id}, benefit_type={benefit_type}, error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="检查权益资格失败"
        )
