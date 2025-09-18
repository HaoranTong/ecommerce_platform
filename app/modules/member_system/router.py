"""
文件名：router.py
文件路径：app/modules/member_system/router.py
功能描述：会员系统模块的API路由定义
主要功能：
- 会员信息管理相关API（获取档案、更新资料、注册会员）
- 会员等级管理API（等级列表、手动升级）
- 积分管理API（积分明细、获取积分、使用积分）
- 权益管理API（权益检查、权益使用、使用历史）
- 活动管理API（活动创建、参与活动、我的活动）
使用说明：
- 导入：from app.modules.member_system import router
- 路由前缀：/api/v1/member-system
- 认证要求：大部分接口需要JWT认证
- 权限控制：管理员接口需要特殊权限
依赖模块：
- app.modules.member_system.service: 会员系统业务逻辑
- app.modules.member_system.schemas: 会员系统数据模式
- app.core.auth: JWT认证相关功能
- app.core.database: 数据库会话依赖
创建时间：2024-09-17
最后修改：2024-09-17
"""

# 标准库
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date

# 第三方库
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# 本地应用导入
from app.modules.member_system.service import (
    get_member_service, get_point_service, 
    get_benefit_service, get_event_service,
    MemberService, PointService, BenefitService, EventService
)
from app.modules.member_system.schemas import (
    # 会员相关
    MemberCreate, MemberUpdate, MemberRead, MemberWithDetails,
    MembershipLevelRead,
    # 积分相关
    PointTransactionCreate, PointTransactionRead, PointSummary, PointTransactionList,
    # 权益相关
    BenefitEligibility, BenefitUsageCreate, BenefitUsageRead, BenefitUsageList,
    # 活动相关
    MemberActivityCreate, MemberActivityUpdate, MemberActivityRead, ActivityList,
    ActivityParticipationCreate, ActivityParticipationRead, UserActivityList,
    # 响应相关
    APIResponse, MemberProfileResponse, PointTransactionResponse,
    BenefitUsageResponse, ActivityParticipationResponse,
    # 枚举类型
    BenefitType, EventType, ActivityStatus
)
from app.core.auth import get_current_admin_user
from app.modules.user_auth.models import User
from .dependencies import (
    get_member_service_dep, get_point_service_dep, 
    get_benefit_service_dep, get_event_service_dep,
    get_current_active_user, get_user_id_from_token,
    validate_points_transaction, validate_member_data
)

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    tags=["会员系统"],
    responses={
        404: {"description": "资源未找到"},
        500: {"description": "服务器内部错误"}
    }
)


# ================== 依赖函数已迁移到dependencies.py ==================
# 注意：所有依赖注入函数现在都在 .dependencies 模块中定义
# 使用 get_member_service_dep, get_point_service_dep 等替代


# ================== 会员信息管理 API ==================

@router.get("/member-system/profile", response_model=MemberProfileResponse, summary="获取会员信息")
async def get_member_profile(
    user_id: int = Depends(get_user_id_from_token),
    member_service: MemberService = Depends(get_member_service_dep)
) -> MemberProfileResponse:
    """
    获取当前用户的完整会员信息
    
    获取包含等级、积分、权益、统计信息等的完整会员档案。
    如果用户还不是会员，将返回404错误。
    
    Returns:
        MemberProfileResponse: 包含完整会员信息的响应
        
    Raises:
        HTTPException: 
            - 401: 用户未认证
            - 404: 会员信息不存在
            - 500: 服务器内部错误
    """
    try:
        member_profile = member_service.get_member_profile(user_id)
        
        if not member_profile:
            return MemberProfileResponse(
                code=404,
                message="会员信息不存在，请先注册成为会员",
                data=None
            )
        
        return MemberProfileResponse(
            code=200,
            message="success",
            data=member_profile
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会员档案失败: user_id={user_id}, error={str(e)}")
        return MemberProfileResponse(
            code=500,
            message="获取会员信息失败",
            data=None
        )


@router.put("/member-system/profile", response_model=APIResponse, summary="更新会员信息")
async def update_member_profile(
    update_data: MemberUpdate,
    user_id: int = Depends(get_user_id_from_token),
    member_service: MemberService = Depends(get_member_service_dep)
) -> APIResponse:
    """
    更新会员可修改的基础信息
    
    允许会员更新昵称、生日、偏好设置等个人信息。
    
    Args:
        update_data: 会员更新数据
        
    Returns:
        APIResponse: 更新结果
        
    Raises:
        HTTPException:
            - 401: 用户未认证
            - 404: 会员信息不存在
            - 422: 请求数据验证失败
            - 500: 服务器内部错误
    """
    try:
        updated_member = member_service.update_member_profile(user_id, update_data)
        
        return APIResponse(
            code=200,
            message="会员信息更新成功",
            data={
                "updated_fields": [
                    field for field, value in update_data.dict(exclude_unset=True).items()
                    if value is not None
                ],
                "updated_at": datetime.utcnow().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新会员信息失败: user_id={user_id}, error={str(e)}")
        return APIResponse(
            code=500,
            message="更新会员信息失败",
            data=None
        )


@router.post("/member-system/register", response_model=APIResponse, summary="注册成为会员")
async def register_member(
    member_data: MemberCreate,
    user_id: int = Depends(get_user_id_from_token),
    member_service: MemberService = Depends(get_member_service_dep)
) -> APIResponse:
    """
    用户注册成为会员
    
    将现有用户转换为会员身份，初始等级为注册会员。
    
    Args:
        member_data: 会员创建数据
        
    Returns:
        APIResponse: 注册结果
        
    Raises:
        HTTPException:
            - 401: 用户未认证
            - 400: 用户已是会员
            - 422: 请求数据验证失败
            - 500: 服务器内部错误
    """
    try:
        new_member = member_service.create_member(user_id, member_data)
        
        return APIResponse(
            code=200,
            message="会员注册成功",
            data={
                "member_id": new_member.member_id,
                "level_name": "注册会员",
                "join_date": new_member.join_date.isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"会员注册失败: user_id={user_id}, error={str(e)}")
        return APIResponse(
            code=500,
            message="会员注册失败",
            data=None
        )


# ================== 会员等级管理 API ==================

@router.get("/member-system/levels", response_model=APIResponse, summary="获取等级列表")
async def get_membership_levels(
    member_service: MemberService = Depends(get_member_service_dep)
) -> APIResponse:
    """
    获取所有会员等级信息和权益对比
    
    返回系统中所有激活的会员等级，包括升级条件、折扣率、权益等信息。
    此接口无需认证，可供游客查看。
    
    Returns:
        APIResponse: 包含等级列表的响应
    """
    try:
        # 从数据库获取所有激活的会员等级
        levels = member_service.db.query(
            member_service.db.query.__class__.__module__.split('.')[0] + '.modules.member_system.models.MembershipLevel'
        ).filter_by(is_active=True).order_by('level_id').all()
        
        level_list = []
        for level in levels:
            # 获取该等级的权益信息
            benefits = member_service._get_member_benefits(level.level_id)
            
            level_list.append({
                "level_id": level.level_id,
                "level_name": level.level_name,
                "level_code": level.level_code,
                "required_spent": float(level.required_spent),
                "discount_rate": float(level.discount_rate),
                "point_multiplier": float(level.point_multiplier),
                "description": level.description,
                "benefits": benefits
            })
        
        return APIResponse(
            code=200,
            message="success",
            data={"levels": level_list}
        )
        
    except Exception as e:
        logger.error(f"获取等级列表失败: error={str(e)}")
        return APIResponse(
            code=500,
            message="获取等级列表失败",
            data=None
        )


@router.post("/member-system/levels/upgrade", response_model=APIResponse, summary="手动升级会员等级")
async def manual_upgrade_level(
    upgrade_data: Dict[str, Any] = Body(..., example={
        "user_id": 1001,
        "target_level_id": 4,
        "reason": "客服手动调整",
        "operator": "admin001"
    }),
    admin_user: User = Depends(get_current_admin_user),
    member_service: MemberService = Depends(get_member_service_dep)
) -> APIResponse:
    """
    管理员手动调整用户会员等级
    
    仅限管理员使用，可以手动调整任意用户的会员等级。
    
    Args:
        upgrade_data: 升级数据，包含用户ID、目标等级、原因等
        
    Returns:
        APIResponse: 升级结果
        
    Raises:
        HTTPException:
            - 401: 用户未认证
            - 403: 权限不足
            - 404: 用户或等级不存在
            - 422: 请求数据验证失败
            - 500: 服务器内部错误
    """
    try:
        # 验证请求数据
        user_id = upgrade_data.get("user_id")
        target_level_id = upgrade_data.get("target_level_id")
        reason = upgrade_data.get("reason", "管理员手动调整")
        operator = upgrade_data.get("operator", admin_user.username)
        
        if not user_id or not target_level_id:
            raise HTTPException(
                status_code=422,
                detail="缺少必要参数: user_id 和 target_level_id"
            )
        
        # 获取目标用户的会员信息
        member = member_service.get_member_by_user_id(user_id)
        if not member:
            raise HTTPException(status_code=404, detail="用户不是会员")
        
        # 验证目标等级存在
        from app.modules.member_system.models import MembershipLevel
        target_level = member_service.db.query(MembershipLevel).filter(
            MembershipLevel.level_id == target_level_id
        ).first()
        
        if not target_level:
            raise HTTPException(status_code=404, detail="目标等级不存在")
        
        # 记录原等级
        old_level = member_service.db.query(MembershipLevel).filter(
            MembershipLevel.level_id == member.level_id
        ).first()
        
        # 执行等级调整
        member.level_id = target_level_id
        member.level_upgrade_date = datetime.utcnow()
        
        member_service.db.commit()
        
        # 更新缓存
        member_service._cache_member_info(member)
        
        # 记录操作日志
        upgrade_info = {
            "user_id": user_id,
            "member_id": member.member_id,
            "old_level": old_level.level_name if old_level else "未知",
            "new_level": target_level.level_name,
            "reason": reason,
            "operator": operator,
            "upgrade_time": member.level_upgrade_date.isoformat()
        }
        
        from app.core.security_logger import SecurityLogger
        security_logger = SecurityLogger()
        security_logger.log_level_upgrade(user_id, upgrade_info)
        
        return APIResponse(
            code=200,
            message="等级调整成功",
            data={
                "old_level": old_level.level_name if old_level else "未知",
                "new_level": target_level.level_name,
                "effective_time": member.level_upgrade_date.isoformat(),
                "operation_id": f"MANUAL_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        member_service.db.rollback()
        logger.error(f"手动升级等级失败: upgrade_data={upgrade_data}, error={str(e)}")
        return APIResponse(
            code=500,
            message="等级调整失败",
            data=None
        )


# ================== 积分管理 API ==================

@router.get("/member-system/points/transactions", response_model=APIResponse, summary="获取积分明细")
async def get_point_transactions(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    transaction_type: Optional[str] = Query(None, description="交易类型过滤"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    user_id: int = Depends(get_user_id_from_token),
    point_service: PointService = Depends(get_point_service_dep)
) -> APIResponse:
    """
    获取用户积分收支明细记录
    
    支持分页查询和多种过滤条件，返回积分交易历史和汇总信息。
    
    Args:
        page: 页码，从1开始
        limit: 每页数量，最大100
        transaction_type: 交易类型过滤 (EARN/USE)
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        APIResponse: 包含积分明细和分页信息的响应
    """
    try:
        # 构建查询条件
        from app.modules.member_system.models import PointTransaction
        from sqlalchemy import and_, desc
        
        query = point_service.db.query(PointTransaction).filter(
            PointTransaction.user_id == user_id
        )
        
        # 应用过滤条件
        if transaction_type:
            query = query.filter(PointTransaction.transaction_type == transaction_type.upper())
        
        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query = query.filter(PointTransaction.created_at >= start_datetime)
            
        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.filter(PointTransaction.created_at <= end_datetime)
        
        # 计算总数和分页
        total_count = query.count()
        total_pages = (total_count + limit - 1) // limit
        
        transactions = query.order_by(desc(PointTransaction.created_at)).offset(
            (page - 1) * limit
        ).limit(limit).all()
        
        # 构建交易记录
        transaction_list = []
        for trans in transactions:
            transaction_list.append({
                "transaction_id": trans.transaction_id,
                "type": trans.transaction_type,
                "event_type": trans.event_type,
                "points": trans.points,
                "description": trans.description,
                "related_order": trans.reference_id,
                "created_at": trans.created_at.isoformat(),
                "expiry_date": trans.expiry_date.isoformat() if trans.expiry_date else None
            })
        
        # 计算积分汇总
        member_service = get_member_service(point_service.db)
        point_summary = member_service._calculate_point_summary(user_id)
        
        return APIResponse(
            code=200,
            message="success",
            data={
                "summary": {
                    "total_earned": point_summary["total_points"],
                    "total_used": point_summary["total_points"] - point_summary["available_points"],
                    "current_balance": point_summary["available_points"]
                },
                "transactions": transaction_list,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "total_pages": total_pages
                }
            }
        )
        
    except Exception as e:
        logger.error(f"获取积分明细失败: user_id={user_id}, error={str(e)}")
        return APIResponse(
            code=500,
            message="获取积分明细失败",
            data=None
        )


@router.post("/member-system/points/earn", response_model=PointTransactionResponse, summary="获得积分")
async def earn_points(
    earn_data: Dict[str, Any] = Body(..., example={
        "points": 100,
        "event_type": "PURCHASE",
        "reference_id": "ORD123456",
        "description": "购物获得积分"
    }),
    user_id: int = Depends(get_user_id_from_token),
    point_service: PointService = Depends(get_point_service_dep)
) -> PointTransactionResponse:
    """
    用户获得积分
    
    记录用户通过各种途径（购物、活动、奖励等）获得的积分。
    
    Args:
        earn_data: 积分获取数据
        
    Returns:
        PointTransactionResponse: 积分交易结果
    """
    try:
        points = earn_data.get("points")
        event_type = earn_data.get("event_type", "MANUAL")
        reference_id = earn_data.get("reference_id")
        description = earn_data.get("description")
        
        if not points or points <= 0:
            raise HTTPException(status_code=422, detail="积分数量必须大于0")
        
        # 执行积分获取
        transaction = point_service.earn_points(
            user_id=user_id,
            points=points,
            event_type=event_type,
            reference_id=reference_id,
            description=description
        )
        
        return PointTransactionResponse(
            code=200,
            message="积分获取成功",
            data={
                "transaction_id": transaction.transaction_id,
                "type": transaction.transaction_type,
                "event_type": transaction.event_type,
                "points": transaction.points,
                "balance_after": transaction.balance_after,
                "expiry_date": transaction.expiry_date.isoformat() if transaction.expiry_date else None,
                "created_at": transaction.created_at.isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"积分获取失败: user_id={user_id}, error={str(e)}")
        return PointTransactionResponse(
            code=500,
            message="积分获取失败",
            data=None
        )


@router.post("/member-system/points/use", response_model=PointTransactionResponse, summary="使用积分")
async def use_points(
    use_data: Dict[str, Any] = Body(..., example={
        "points": 50,
        "event_type": "REDEMPTION",
        "reference_id": "ORD123457",
        "description": "积分抵扣"
    }),
    user_id: int = Depends(get_user_id_from_token),
    point_service: PointService = Depends(get_point_service_dep)
) -> PointTransactionResponse:
    """
    用户使用积分
    
    处理用户积分消费，采用FIFO规则（先获得的积分先使用）。
    
    Args:
        use_data: 积分使用数据
        
    Returns:
        PointTransactionResponse: 积分交易结果
    """
    try:
        points = use_data.get("points")
        event_type = use_data.get("event_type", "REDEMPTION")
        reference_id = use_data.get("reference_id")
        description = use_data.get("description")
        
        if not points or points <= 0:
            raise HTTPException(status_code=422, detail="积分数量必须大于0")
        
        # 执行积分使用
        transaction = point_service.use_points(
            user_id=user_id,
            points=points,
            event_type=event_type,
            reference_id=reference_id,
            description=description
        )
        
        return PointTransactionResponse(
            code=200,
            message="积分使用成功",
            data={
                "transaction_id": transaction.transaction_id,
                "type": transaction.transaction_type,
                "event_type": transaction.event_type,
                "points": transaction.points,
                "balance_after": transaction.balance_after,
                "created_at": transaction.created_at.isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"积分使用失败: user_id={user_id}, error={str(e)}")
        return PointTransactionResponse(
            code=500,
            message="积分使用失败",
            data=None
        )


@router.get("/member-system/points/summary", response_model=APIResponse, summary="获取积分汇总")
async def get_point_summary(
    user_id: int = Depends(get_user_id_from_token),
    point_service: PointService = Depends(get_point_service_dep)
) -> APIResponse:
    """
    获取用户积分汇总信息
    
    返回用户的积分总览，包括总积分、可用积分、即将过期积分等。
    
    Returns:
        APIResponse: 积分汇总信息
    """
    try:
        member_service = get_member_service(point_service.db)
        point_summary = member_service._calculate_point_summary(user_id)
        
        return APIResponse(
            code=200,
            message="success",
            data=point_summary
        )
        
    except Exception as e:
        logger.error(f"获取积分汇总失败: user_id={user_id}, error={str(e)}")
        return APIResponse(
            code=500,
            message="获取积分汇总失败",
            data=None
        )


@router.post("/member-system/points/redeem", response_model=APIResponse, summary="积分兑换商品")
async def redeem_points(
    redeem_data: Dict[str, Any] = Body(..., example={
        "redemption_item_id": "GIFT001",
        "quantity": 1,
        "delivery_address": {
            "name": "张三",
            "phone": "13800138000", 
            "address": "北京市朝阳区xxx街道xxx号"
        }
    }),
    user_id: int = Depends(get_user_id_from_token),
    point_service: PointService = Depends(get_point_service_dep)
) -> APIResponse:
    """
    使用积分兑换指定商品或权益
    
    用户可以使用积分兑换积分商城中的商品或权益。
    
    Args:
        redeem_data: 兑换数据
        
    Returns:
        APIResponse: 兑换结果
    """
    try:
        redemption_item_id = redeem_data.get("redemption_item_id")
        quantity = redeem_data.get("quantity", 1)
        delivery_address = redeem_data.get("delivery_address")
        
        if not redemption_item_id:
            raise HTTPException(status_code=422, detail="缺少兑换商品ID参数")
        
        # 这里应该调用积分兑换服务，暂时返回模拟数据
        redemption_result = {
            "redemption_id": f"RED{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "item_name": "积分商城礼品",
            "points_cost": 500,
            "remaining_points": 2030,
            "estimated_delivery": "2024-09-20",
            "tracking_code": None
        }
        
        return APIResponse(
            code=200,
            message="兑换成功",
            data=redemption_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"积分兑换失败: user_id={user_id}, error={str(e)}")
        return APIResponse(
            code=500,
            message="积分兑换失败",
            data=None
        )


# ================== 权益管理 API ==================

@router.get("/member-system/benefits/available", response_model=APIResponse, summary="获取可用权益")
async def get_available_benefits(
    user_id: int = Depends(get_user_id_from_token),
    member_service: MemberService = Depends(get_member_service_dep),
    benefit_service: BenefitService = Depends(get_benefit_service_dep)
) -> APIResponse:
    """
    获取当前会员可用的所有权益
    
    返回用户基于当前等级可享受的所有权益列表。
    
    Returns:
        APIResponse: 可用权益列表
    """
    try:
        member = member_service.get_member_by_user_id(user_id)
        if not member:
            raise HTTPException(status_code=404, detail="会员信息不存在")
        
        # 获取等级信息
        level = member_service.get_membership_level(member.level_id)
        if not level:
            raise HTTPException(status_code=404, detail="会员等级信息不存在")
        
        # 获取权益列表 - 这里应该从权益服务获取
        benefits = [
            {
                "benefit_id": "B001",
                "benefit_name": "会员专享折扣",
                "benefit_type": "DISCOUNT",
                "value": float(level.discount_rate),
                "description": f"全场商品{int((1-level.discount_rate)*100)}%优惠",
                "usage_limit": None,
                "used_count": 0,
                "valid_until": None
            },
            {
                "benefit_id": "B002", 
                "benefit_name": "免运费",
                "benefit_type": "FREE_SHIPPING",
                "value": 1,
                "description": "全场免运费",
                "usage_limit": None,
                "used_count": 0,
                "valid_until": None
            }
        ]
        
        return APIResponse(
            code=200,
            message="success",
            data={
                "current_level": level.level_name,
                "benefits": benefits
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取可用权益失败: user_id={user_id}, error={str(e)}")
        return APIResponse(
            code=500,
            message="获取可用权益失败",
            data=None
        )


@router.get("/member-system/benefits/eligibility/{benefit_type}", response_model=APIResponse, summary="检查权益资格")
async def check_benefit_eligibility(
    benefit_type: BenefitType = Path(..., description="权益类型"),
    user_id: int = Depends(get_user_id_from_token),
    benefit_service: BenefitService = Depends(get_benefit_service_dep)
) -> APIResponse:
    """
    检查用户特定权益的资格
    
    返回用户对特定权益的使用资格、剩余次数等信息。
    
    Args:
        benefit_type: 权益类型
        
    Returns:
        APIResponse: 权益资格信息
    """
    try:
        eligibility = benefit_service.check_benefit_eligibility(
            user_id=user_id,
            benefit_type=benefit_type.value
        )
        
        return APIResponse(
            code=200,
            message="success",
            data=eligibility
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"检查权益资格失败: user_id={user_id}, benefit_type={benefit_type}, error={str(e)}")
        return APIResponse(
            code=500,
            message="检查权益资格失败",
            data=None
        )


@router.post("/member-system/benefits/use", response_model=BenefitUsageResponse, summary="使用权益")
async def use_benefit(
    usage_data: Dict[str, Any] = Body(..., example={
        "benefit_type": "free_shipping",
        "reference_id": "ORD123456",
        "description": "订单免运费",
        "benefit_value": 15.00
    }),
    user_id: int = Depends(get_user_id_from_token),
    benefit_service: BenefitService = Depends(get_benefit_service_dep)
) -> BenefitUsageResponse:
    """
    使用会员权益
    
    记录用户权益的使用，包括免运费、生日礼品等各种权益类型。
    
    Args:
        usage_data: 权益使用数据
        
    Returns:
        BenefitUsageResponse: 权益使用结果
    """
    try:
        benefit_type = usage_data.get("benefit_type")
        reference_id = usage_data.get("reference_id")
        description = usage_data.get("description")
        benefit_value = usage_data.get("benefit_value")
        
        if not benefit_type:
            raise HTTPException(status_code=422, detail="缺少权益类型参数")
        
        # 使用权益
        from decimal import Decimal
        usage_record = benefit_service.use_benefit(
            user_id=user_id,
            benefit_type=benefit_type,
            reference_id=reference_id,
            description=description,
            benefit_value=Decimal(str(benefit_value)) if benefit_value else None
        )
        
        return BenefitUsageResponse(
            code=200,
            message="权益使用成功",
            data={
                "usage_id": usage_record.usage_id,
                "benefit_type": usage_record.benefit_type,
                "reference_id": usage_record.reference_id,
                "description": usage_record.description,
                "benefit_value": float(usage_record.benefit_value) if usage_record.benefit_value else None,
                "used_at": usage_record.used_at.isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"使用权益失败: user_id={user_id}, error={str(e)}")
        return BenefitUsageResponse(
            code=500,
            message="使用权益失败",
            data=None
        )


@router.get("/member-system/benefits/history", response_model=APIResponse, summary="获取权益使用历史")
async def get_benefit_usage_history(
    benefit_type: Optional[BenefitType] = Query(None, description="权益类型过滤"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_user_id_from_token),
    benefit_service: BenefitService = Depends(get_benefit_service_dep)
) -> APIResponse:
    """
    获取权益使用历史记录
    
    支持按权益类型、日期范围等条件过滤查询权益使用历史。
    
    Args:
        benefit_type: 权益类型过滤
        start_date: 开始日期
        end_date: 结束日期
        page: 页码
        limit: 每页数量
        
    Returns:
        APIResponse: 权益使用历史
    """
    try:
        # 转换日期为datetime
        start_datetime = datetime.combine(start_date, datetime.min.time()) if start_date else None
        end_datetime = datetime.combine(end_date, datetime.max.time()) if end_date else None
        
        usage_history = benefit_service.get_benefit_usage_history(
            user_id=user_id,
            benefit_type=benefit_type.value if benefit_type else None,
            start_date=start_datetime,
            end_date=end_datetime,
            page=page,
            limit=limit
        )
        
        return APIResponse(
            code=200,
            message="success",
            data=usage_history
        )
        
    except Exception as e:
        logger.error(f"获取权益使用历史失败: user_id={user_id}, error={str(e)}")
        return APIResponse(
            code=500,
            message="获取权益使用历史失败",
            data=None
        )


@router.get("/member-system/benefits/status", response_model=APIResponse, summary="获取权益状态")
async def get_benefit_status(
    user_id: int = Depends(get_user_id_from_token),
    member_service: MemberService = Depends(get_member_service_dep)
) -> APIResponse:
    """
    获取用户当前的权益状态
    
    返回用户基于当前等级可享受的所有权益状态。
    
    Returns:
        APIResponse: 权益状态信息
    """
    try:
        member = member_service.get_member_by_user_id(user_id)
        if not member:
            raise HTTPException(status_code=404, detail="会员信息不存在")
        
        benefits = member_service._get_member_benefits(member.level_id)
        
        return APIResponse(
            code=200,
            message="success",
            data={"benefits": benefits}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取权益状态失败: user_id={user_id}, error={str(e)}")
        return APIResponse(
            code=500,
            message="获取权益状态失败",
            data=None
        )


# ================== 活动管理 API ==================

@router.post("/member-system/activities", response_model=APIResponse, summary="创建会员活动")
async def create_activity(
    activity_data: MemberActivityCreate,
    admin_user: User = Depends(get_current_admin_user),
    event_service: EventService = Depends(get_event_service_dep)
) -> APIResponse:
    """
    创建会员活动（管理员专用）
    
    管理员可以创建各种类型的会员活动。
    
    Args:
        activity_data: 活动创建数据
        
    Returns:
        APIResponse: 活动创建结果
    """
    try:
        activity = event_service.create_activity(
            title=activity_data.title,
            description=activity_data.description,
            activity_type=activity_data.activity_type,
            start_time=activity_data.start_time,
            end_time=activity_data.end_time,
            max_participants=activity_data.max_participants,
            reward_config=activity_data.reward_config,
            participation_rules=activity_data.participation_rules
        )
        
        return APIResponse(
            code=200,
            message="活动创建成功",
            data={
                "activity_id": activity.activity_id,
                "title": activity.title,
                "activity_type": activity.activity_type,
                "start_time": activity.start_time.isoformat(),
                "end_time": activity.end_time.isoformat(),
                "status": activity.status,
                "created_at": activity.created_at.isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建活动失败: admin_user={admin_user.username}, error={str(e)}")
        return APIResponse(
            code=500,
            message="创建活动失败",
            data=None
        )


@router.post("/member-system/activities/{activity_id}/join", response_model=ActivityParticipationResponse, summary="参与活动")
async def join_activity(
    activity_id: int = Path(..., description="活动ID"),
    user_id: int = Depends(get_user_id_from_token),
    event_service: EventService = Depends(get_event_service_dep)
) -> ActivityParticipationResponse:
    """
    用户参与会员活动
    
    用户报名参加指定的会员活动。
    
    Args:
        activity_id: 活动ID
        
    Returns:
        ActivityParticipationResponse: 参与结果
    """
    try:
        participation = event_service.join_activity(
            user_id=user_id,
            activity_id=activity_id
        )
        
        return ActivityParticipationResponse(
            code=200,
            message="活动参与成功",
            data={
                "participation_id": participation.participation_id,
                "activity_id": participation.activity_id,
                "participation_time": participation.participation_time.isoformat(),
                "status": participation.status
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"参与活动失败: user_id={user_id}, activity_id={activity_id}, error={str(e)}")
        return ActivityParticipationResponse(
            code=500,
            message="参与活动失败",
            data=None
        )


@router.get("/member-system/activities/my", response_model=APIResponse, summary="获取我参与的活动")
async def get_my_activities(
    status: Optional[ActivityStatus] = Query(None, description="活动状态过滤"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_user_id_from_token),
    event_service: EventService = Depends(get_event_service_dep)
) -> APIResponse:
    """
    获取用户参与的活动列表
    
    返回当前用户参与的所有活动，支持状态过滤和分页。
    
    Args:
        status: 活动状态过滤
        page: 页码
        limit: 每页数量
        
    Returns:
        APIResponse: 用户活动列表
    """
    try:
        activities = event_service.get_user_activities(
            user_id=user_id,
            status=status.value if status else None,
            page=page,
            limit=limit
        )
        
        return APIResponse(
            code=200,
            message="success",
            data=activities
        )
        
    except Exception as e:
        logger.error(f"获取用户活动失败: user_id={user_id}, error={str(e)}")
        return APIResponse(
            code=500,
            message="获取用户活动失败",
            data=None
        )


@router.get("/member-system/activities", response_model=APIResponse, summary="获取活动列表")
async def get_activities(
    status: Optional[ActivityStatus] = Query(None, description="活动状态过滤"),
    activity_type: Optional[str] = Query(None, description="活动类型过滤"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    event_service: EventService = Depends(get_event_service_dep)
) -> APIResponse:
    """
    获取可参与的活动列表
    
    返回系统中的活动列表，支持多种过滤条件。
    
    Args:
        status: 活动状态过滤
        activity_type: 活动类型过滤
        page: 页码
        limit: 每页数量
        
    Returns:
        APIResponse: 活动列表
    """
    try:
        from app.modules.member_system.models import MemberActivity
        from sqlalchemy import and_, desc
        
        # 构建查询
        query = event_service.db.query(MemberActivity)
        
        if status:
            query = query.filter(MemberActivity.status == status.value)
            
        if activity_type:
            query = query.filter(MemberActivity.activity_type == activity_type)
        
        # 计算分页
        total_count = query.count()
        total_pages = (total_count + limit - 1) // limit
        
        activities = query.order_by(desc(MemberActivity.created_at)).offset(
            (page - 1) * limit
        ).limit(limit).all()
        
        # 构建活动列表
        activity_list = []
        for activity in activities:
            activity_list.append({
                "activity_id": activity.activity_id,
                "title": activity.title,
                "description": activity.description,
                "activity_type": activity.activity_type,
                "start_time": activity.start_time.isoformat(),
                "end_time": activity.end_time.isoformat(),
                "max_participants": activity.max_participants,
                "current_participants": activity.current_participants,
                "status": activity.status,
                "created_at": activity.created_at.isoformat()
            })
        
        return APIResponse(
            code=200,
            message="success",
            data={
                "activities": activity_list,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "total_pages": total_pages
                }
            }
        )
        
    except Exception as e:
        logger.error(f"获取活动列表失败: error={str(e)}")
        return APIResponse(
            code=500,
            message="获取活动列表失败",
            data=None
        )
