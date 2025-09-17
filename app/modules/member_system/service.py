"""
文件名：service.py
文件路径：app/modules/member_system/service.py
功能描述：会员系统模块的核心业务逻辑服务
主要功能：
- 会员信息管理和等级升级处理
- 积分获取、使用、过期处理（FIFO规则）
- 会员权益检查和使用统计
- 会员活动管理和参与记录
- 事件驱动的消息处理和缓存管理
使用说明：
- 导入：from app.modules.member_system.service import MemberService, PointService
- 依赖注入：通过构造函数传入数据库会话和Redis客户端
- 缓存策略：多层缓存设计，自动失效和刷新
- 事务处理：关键业务操作包装在数据库事务中
依赖模块：
- app.modules.member_system.models: 会员系统数据模型
- app.modules.member_system.schemas: 会员系统Pydantic模式
- app.shared.models: 共享数据模型
- app.core.redis_client: Redis缓存客户端
- app.core.security_logger: 安全审计日志
创建时间：2024-09-17
最后修改：2024-09-17
"""

# 标准库
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
import json

# 第三方库
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from redis import Redis
from fastapi import HTTPException

# 本地应用导入
from app.modules.member_system.models import (
    Member, MembershipLevel, MembershipBenefit, PointTransaction,
    MemberActivity, ActivityParticipation, BenefitUsage, SystemConfig
)
from app.modules.member_system.schemas import (
    MemberCreate, MemberUpdate, MemberRead, MemberWithDetails,
    PointTransactionCreate, PointSummary,
    BenefitUsageCreate, ActivityParticipationCreate
)
from app.modules.user_auth.models import User
from app.core.redis_client import get_redis_client
from app.core.security_logger import SecurityLogger

# 配置日志
logger = logging.getLogger(__name__)
security_logger = SecurityLogger()


class MemberService:
    """
    会员业务逻辑服务类
    
    功能描述：
        处理会员相关的核心业务逻辑，包括会员信息管理、等级升级、
        资料更新等操作。实现多层缓存策略和事件驱动架构。
        
    主要方法：
        - get_member_profile(): 获取完整会员档案信息
        - update_member_profile(): 更新会员可修改信息
        - check_level_upgrade(): 检查并处理等级升级
        - calculate_upgrade_progress(): 计算升级进度
        
    使用方式：
        ```python
        member_service = MemberService(db_session, redis_client)
        member_profile = member_service.get_member_profile(user_id)
        ```
        
    Dependencies:
        - SQLAlchemy Session: 数据库操作
        - Redis Client: 缓存管理
        - SecurityLogger: 安全审计记录
    """

    def __init__(self, db: Session, redis_client: Optional[Redis] = None):
        """
        初始化会员服务
        
        Args:
            db (Session): 数据库会话
            redis_client (Optional[Redis]): Redis客户端，如果为None则自动获取
        """
        self.db = db
        self.redis = redis_client or get_redis_client()
        self.cache_prefix = "member_system:"
        self.cache_ttl = 3600  # 1小时缓存过期时间

    def get_member_by_user_id(self, user_id: int) -> Optional[Member]:
        """
        根据用户ID获取会员信息
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            Optional[Member]: 会员信息，如果不存在则返回None
            
        Raises:
            HTTPException: 数据库查询异常时抛出500错误
        """
        try:
            # ================== 缓存检查 ==================
            # 先从缓存获取会员基础信息
            cache_key = f"{self.cache_prefix}member:{user_id}"
            cached_member = self.redis.get(cache_key)
            
            if cached_member:
                logger.info(f"从缓存获取会员信息: user_id={user_id}")
                # 缓存命中，但仍需要从数据库获取完整对象用于关联查询
            
            # ================== 数据库查询 ==================
            # 查询会员信息，包含关联的等级信息
            member = self.db.query(Member).filter(
                Member.user_id == user_id
            ).first()
            
            if member and not cached_member:
                # 缓存会员基础信息
                self._cache_member_info(member)
            
            return member
            
        except SQLAlchemyError as e:
            logger.error(f"查询会员信息失败: user_id={user_id}, error={str(e)}")
            raise HTTPException(status_code=500, detail="查询会员信息失败")

    def get_member_profile(self, user_id: int) -> Optional[MemberWithDetails]:
        """
        获取完整的会员档案信息
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            Optional[MemberWithDetails]: 包含等级、积分、权益等完整信息的会员档案
            
        Raises:
            HTTPException: 
                - 404: 会员不存在
                - 500: 数据库查询异常
                
        Example:
            ```python
            profile = member_service.get_member_profile(1001)
            if profile:
                print(f"会员等级: {profile.level.level_name}")
                print(f"可用积分: {profile.points.available_points}")
            ```
        """
        try:
            # ================== 获取会员基础信息 ==================
            member = self.get_member_by_user_id(user_id)
            if not member:
                raise HTTPException(status_code=404, detail="会员信息不存在")
            
            # ================== 获取等级信息 ==================
            level_info = self.db.query(MembershipLevel).filter(
                MembershipLevel.level_id == member.level_id
            ).first()
            
            if not level_info:
                logger.warning(f"会员等级信息缺失: member_id={member.member_id}")
                raise HTTPException(status_code=500, detail="会员等级信息异常")
            
            # ================== 计算积分统计 ==================
            point_summary = self._calculate_point_summary(user_id)
            
            # ================== 获取权益信息 ==================
            benefits = self._get_member_benefits(member.level_id)
            
            # ================== 计算升级进度 ==================
            next_level_info = self._calculate_upgrade_progress(member)
            
            # ================== 构建完整档案 ==================
            profile_data = {
                "member_id": member.member_id,
                "user_id": member.user_id,
                "level": {
                    "level_id": level_info.level_id,
                    "level_name": level_info.level_name,
                    "level_code": level_info.level_code,
                    "discount_rate": float(level_info.discount_rate),
                    "point_multiplier": float(level_info.point_multiplier)
                },
                "points": point_summary,
                "statistics": {
                    "total_spent": float(member.total_spent),
                    "total_orders": member.total_orders,
                    "join_date": member.join_date.isoformat(),
                    "last_active": member.last_active_at.isoformat() if member.last_active_at else None
                },
                "benefits": benefits,
                "next_level": next_level_info
            }
            
            # 记录安全审计日志
            security_logger.log_member_access(user_id, "profile_view", {
                "member_id": member.member_id,
                "level": level_info.level_name,
                "timestamp": datetime.utcnow()
            })
            
            return MemberWithDetails(**profile_data)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取会员档案失败: user_id={user_id}, error={str(e)}")
            raise HTTPException(status_code=500, detail="获取会员档案失败")

    def create_member(self, user_id: int, member_data: MemberCreate) -> Member:
        """
        创建新会员
        
        Args:
            user_id (int): 用户ID
            member_data (MemberCreate): 会员创建数据
            
        Returns:
            Member: 创建的会员信息
            
        Raises:
            HTTPException:
                - 400: 用户已是会员
                - 404: 用户不存在  
                - 500: 数据库操作失败
        """
        try:
            # ================== 验证用户存在性 ==================
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            # ================== 检查是否已是会员 ==================
            existing_member = self.get_member_by_user_id(user_id)
            if existing_member:
                raise HTTPException(status_code=400, detail="用户已是会员")
            
            # ================== 获取初始会员等级 ==================
            # 默认为注册会员（level_id=1）
            initial_level = self.db.query(MembershipLevel).filter(
                MembershipLevel.level_code == "BASIC"
            ).first()
            
            if not initial_level:
                logger.error("系统未配置基础会员等级")
                raise HTTPException(status_code=500, detail="会员系统配置异常")
            
            # ================== 创建会员记录 ==================
            new_member = Member(
                user_id=user_id,
                level_id=initial_level.level_id,
                join_date=datetime.utcnow(),
                nickname=member_data.nickname,
                birthday=member_data.birthday,
                preferences=member_data.preferences or {}
            )
            
            self.db.add(new_member)
            self.db.commit()
            self.db.refresh(new_member)
            
            # ================== 缓存新会员信息 ==================
            self._cache_member_info(new_member)
            
            # ================== 记录安全审计日志 ==================
            security_logger.log_member_creation(user_id, {
                "member_id": new_member.member_id,
                "initial_level": initial_level.level_name,
                "join_date": new_member.join_date,
                "created_by": "system"
            })
            
            logger.info(f"创建新会员成功: user_id={user_id}, member_id={new_member.member_id}")
            return new_member
            
        except HTTPException:
            raise
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"创建会员数据完整性错误: user_id={user_id}, error={str(e)}")
            raise HTTPException(status_code=400, detail="会员数据创建失败")
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建会员失败: user_id={user_id}, error={str(e)}")
            raise HTTPException(status_code=500, detail="创建会员失败")

    def update_member_profile(self, user_id: int, update_data: MemberUpdate) -> Member:
        """
        更新会员资料信息
        
        Args:
            user_id (int): 用户ID
            update_data (MemberUpdate): 更新数据
            
        Returns:
            Member: 更新后的会员信息
            
        Raises:
            HTTPException:
                - 404: 会员不存在
                - 500: 更新失败
        """
        try:
            # ================== 获取会员信息 ==================
            member = self.get_member_by_user_id(user_id)
            if not member:
                raise HTTPException(status_code=404, detail="会员信息不存在")
            
            # ================== 更新字段检查 ==================
            update_fields = []
            
            if update_data.nickname is not None:
                member.nickname = update_data.nickname
                update_fields.append("nickname")
                
            if update_data.birthday is not None:
                member.birthday = update_data.birthday
                update_fields.append("birthday")
                
            if update_data.preferences is not None:
                # 合并偏好设置，保留原有设置
                current_preferences = member.preferences or {}
                current_preferences.update(update_data.preferences)
                member.preferences = current_preferences
                update_fields.append("preferences")
            
            # ================== 更新最后活跃时间 ==================
            member.last_active_at = datetime.utcnow()
            
            # ================== 提交更新 ==================
            self.db.commit()
            self.db.refresh(member)
            
            # ================== 更新缓存 ==================
            self._cache_member_info(member)
            
            # ================== 记录安全审计日志 ==================
            security_logger.log_member_update(user_id, {
                "member_id": member.member_id,
                "updated_fields": update_fields,
                "update_time": member.last_active_at
            })
            
            logger.info(f"更新会员资料成功: user_id={user_id}, fields={update_fields}")
            return member
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新会员资料失败: user_id={user_id}, error={str(e)}")
            raise HTTPException(status_code=500, detail="更新会员资料失败")

    def check_level_upgrade(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        检查并处理会员等级升级
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            Optional[Dict[str, Any]]: 如果发生升级，返回升级信息；否则返回None
            
        Note:
            - 根据总消费金额自动判断是否达到升级条件
            - 升级后自动更新会员等级和相关权益
            - 记录升级日志和发送升级通知
        """
        try:
            # ================== 获取会员信息 ==================
            member = self.get_member_by_user_id(user_id)
            if not member:
                return None
            
            # ================== 获取当前等级信息 ==================
            current_level = self.db.query(MembershipLevel).filter(
                MembershipLevel.level_id == member.level_id
            ).first()
            
            # ================== 查找可升级的等级 ==================
            # 查询比当前等级更高的等级，按升级条件排序
            next_levels = self.db.query(MembershipLevel).filter(
                and_(
                    MembershipLevel.level_id > current_level.level_id,
                    MembershipLevel.required_spent <= member.total_spent,
                    MembershipLevel.is_active == True
                )
            ).order_by(desc(MembershipLevel.required_spent)).all()
            
            if not next_levels:
                # 没有可升级的等级
                return None
            
            # ================== 执行等级升级 ==================
            # 选择最高的可达到等级
            target_level = next_levels[0]
            old_level_name = current_level.level_name
            
            member.level_id = target_level.level_id
            member.level_upgrade_date = datetime.utcnow()
            
            self.db.commit()
            
            # ================== 更新缓存 ==================
            self._cache_member_info(member)
            
            # ================== 构建升级信息 ==================
            upgrade_info = {
                "user_id": user_id,
                "member_id": member.member_id,
                "old_level": {
                    "level_id": current_level.level_id,
                    "level_name": old_level_name,
                    "level_code": current_level.level_code
                },
                "new_level": {
                    "level_id": target_level.level_id,
                    "level_name": target_level.level_name,
                    "level_code": target_level.level_code
                },
                "upgrade_time": member.level_upgrade_date,
                "total_spent": float(member.total_spent),
                "trigger": "auto_upgrade"
            }
            
            # ================== 记录安全审计日志 ==================
            security_logger.log_level_upgrade(user_id, upgrade_info)
            
            logger.info(f"会员等级自动升级: user_id={user_id}, {old_level_name} -> {target_level.level_name}")
            return upgrade_info
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"检查等级升级失败: user_id={user_id}, error={str(e)}")
            return None

    def _calculate_point_summary(self, user_id: int) -> Dict[str, Any]:
        """
        计算用户积分汇总信息
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            Dict[str, Any]: 积分汇总信息
        """
        # 查询积分统计
        total_earned = self.db.query(func.coalesce(func.sum(PointTransaction.points), 0)).filter(
            and_(
                PointTransaction.user_id == user_id,
                PointTransaction.transaction_type == "EARN"
            )
        ).scalar()
        
        total_used = self.db.query(func.coalesce(func.sum(func.abs(PointTransaction.points)), 0)).filter(
            and_(
                PointTransaction.user_id == user_id,
                PointTransaction.transaction_type == "USE"
            )
        ).scalar()
        
        # 计算可用积分（未过期且未冻结）
        available_points = total_earned - total_used
        
        # 查询即将过期的积分
        expiry_threshold = datetime.utcnow() + timedelta(days=30)
        expiring_points = self.db.query(func.coalesce(func.sum(PointTransaction.points), 0)).filter(
            and_(
                PointTransaction.user_id == user_id,
                PointTransaction.transaction_type == "EARN",
                PointTransaction.expiry_date <= expiry_threshold,
                PointTransaction.expiry_date > datetime.utcnow()
            )
        ).scalar()
        
        return {
            "total_points": int(total_earned),
            "available_points": int(available_points),
            "frozen_points": 0,  # 冻结积分逻辑待实现
            "expiring_points": int(expiring_points),
            "expiring_date": expiry_threshold.isoformat() if expiring_points > 0 else None
        }

    def _get_member_benefits(self, level_id: int) -> Dict[str, bool]:
        """
        获取会员等级对应的权益信息
        
        Args:
            level_id (int): 会员等级ID
            
        Returns:
            Dict[str, bool]: 权益开通状态
        """
        benefits = self.db.query(MembershipBenefit).filter(
            MembershipBenefit.level_id == level_id
        ).all()
        
        benefit_status = {
            "free_shipping": False,
            "birthday_gift": False,
            "priority_service": False,
            "exclusive_events": False,
            "points_multiplier": False,
            "custom_service": False
        }
        
        for benefit in benefits:
            if benefit.benefit_type in benefit_status:
                benefit_status[benefit.benefit_type] = benefit.is_active
        
        return benefit_status

    def _calculate_upgrade_progress(self, member: Member) -> Optional[Dict[str, Any]]:
        """
        计算会员升级进度
        
        Args:
            member (Member): 会员信息
            
        Returns:
            Optional[Dict[str, Any]]: 升级进度信息，如果已是最高等级则返回None
        """
        # 查询下一等级信息
        next_level = self.db.query(MembershipLevel).filter(
            and_(
                MembershipLevel.level_id > member.level_id,
                MembershipLevel.is_active == True
            )
        ).order_by(MembershipLevel.level_id).first()
        
        if not next_level:
            return None
        
        required_spent = float(next_level.required_spent)
        current_spent = float(member.total_spent)
        remaining_spent = max(0, required_spent - current_spent)
        progress_percentage = min(100.0, (current_spent / required_spent) * 100) if required_spent > 0 else 100.0
        
        return {
            "level_name": next_level.level_name,
            "level_code": next_level.level_code,
            "required_spent": required_spent,
            "remaining_spent": remaining_spent,
            "progress_percentage": round(progress_percentage, 2)
        }

    def _cache_member_info(self, member: Member) -> None:
        """
        缓存会员信息
        
        Args:
            member (Member): 会员信息
        """
        try:
            cache_key = f"{self.cache_prefix}member:{member.user_id}"
            member_data = {
                "member_id": member.member_id,
                "user_id": member.user_id,
                "level_id": member.level_id,
                "total_spent": float(member.total_spent),
                "total_orders": member.total_orders,
                "last_cached": datetime.utcnow().isoformat()
            }
            
            self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(member_data, ensure_ascii=False)
            )
            
        except Exception as e:
            logger.warning(f"缓存会员信息失败: member_id={member.member_id}, error={str(e)}")


class PointService:
    """
    积分业务逻辑服务类
    
    功能描述：
        处理会员积分相关的业务逻辑，包括积分获取、使用、过期处理等。
        实现FIFO规则和2年过期策略，支持多种积分事件类型。
        
    主要方法：
        - earn_points(): 积分获取处理
        - use_points(): 积分使用处理（FIFO规则）
        - get_point_transactions(): 获取积分明细
        - process_expired_points(): 处理过期积分
        
    使用方式：
        ```python
        point_service = PointService(db_session, redis_client)
        result = point_service.earn_points(user_id, 100, "PURCHASE", order_id)
        ```
        
    Dependencies:
        - SQLAlchemy Session: 数据库操作
        - Redis Client: 缓存管理
        - SecurityLogger: 安全审计记录
    """

    def __init__(self, db: Session, redis_client: Optional[Redis] = None):
        """
        初始化积分服务
        
        Args:
            db (Session): 数据库会话
            redis_client (Optional[Redis]): Redis客户端
        """
        self.db = db
        self.redis = redis_client or get_redis_client()
        self.cache_prefix = "points:"
        self.cache_ttl = 1800  # 30分钟缓存过期时间
        self.point_expiry_years = 2  # 积分2年过期

    def earn_points(
        self,
        user_id: int,
        points: int,
        event_type: str,
        reference_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> PointTransaction:
        """
        处理积分获取
        
        Args:
            user_id (int): 用户ID
            points (int): 获取积分数量
            event_type (str): 事件类型（PURCHASE, REGISTER, ACTIVITY等）
            reference_id (Optional[str]): 关联订单或活动ID
            description (Optional[str]): 描述信息
            
        Returns:
            PointTransaction: 积分交易记录
            
        Raises:
            HTTPException:
                - 400: 参数错误
                - 404: 会员不存在
                - 500: 处理失败
        """
        if points <= 0:
            raise HTTPException(status_code=400, detail="积分数量必须大于0")
        
        try:
            # ================== 验证会员存在性 ==================
            member_service = MemberService(self.db, self.redis)
            member = member_service.get_member_by_user_id(user_id)
            if not member:
                raise HTTPException(status_code=404, detail="会员信息不存在")
            
            # ================== 计算积分过期时间 ==================
            expiry_date = datetime.utcnow() + timedelta(days=365 * self.point_expiry_years)
            
            # ================== 创建积分交易记录 ==================
            transaction = PointTransaction(
                user_id=user_id,
                transaction_type="EARN",
                event_type=event_type,
                points=points,
                balance_after=0,  # 稍后计算
                reference_id=reference_id,
                description=description or f"{event_type}获得积分",
                expiry_date=expiry_date,
                created_at=datetime.utcnow()
            )
            
            self.db.add(transaction)
            
            # ================== 计算积分余额 ==================
            # 查询当前可用积分总额
            current_balance = self._get_available_points(user_id)
            transaction.balance_after = current_balance + points
            
            self.db.commit()
            self.db.refresh(transaction)
            
            # ================== 清除积分缓存 ==================
            self._clear_point_cache(user_id)
            
            # ================== 记录安全审计日志 ==================
            security_logger.log_point_transaction(user_id, {
                "transaction_id": transaction.transaction_id,
                "type": "EARN",
                "points": points,
                "event_type": event_type,
                "reference_id": reference_id,
                "new_balance": transaction.balance_after
            })
            
            logger.info(f"积分获取成功: user_id={user_id}, points={points}, event={event_type}")
            return transaction
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"积分获取失败: user_id={user_id}, error={str(e)}")
            raise HTTPException(status_code=500, detail="积分获取处理失败")

    def use_points(
        self,
        user_id: int,
        points: int,
        event_type: str = "REDEMPTION",
        reference_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> PointTransaction:
        """
        处理积分使用（FIFO规则）
        
        Args:
            user_id (int): 用户ID
            points (int): 使用积分数量
            event_type (str): 事件类型，默认为REDEMPTION
            reference_id (Optional[str]): 关联订单ID
            description (Optional[str]): 描述信息
            
        Returns:
            PointTransaction: 积分交易记录
            
        Raises:
            HTTPException:
                - 400: 积分不足或参数错误
                - 404: 会员不存在
                - 500: 处理失败
                
        Note:
            使用FIFO（先进先出）规则，优先使用最早获得的积分
        """
        if points <= 0:
            raise HTTPException(status_code=400, detail="积分数量必须大于0")
        
        try:
            # ================== 验证积分余额 ==================
            available_points = self._get_available_points(user_id)
            if available_points < points:
                raise HTTPException(
                    status_code=400,
                    detail=f"积分不足，当前可用积分：{available_points}，需要积分：{points}"
                )
            
            # ================== 创建积分使用记录 ==================
            transaction = PointTransaction(
                user_id=user_id,
                transaction_type="USE",
                event_type=event_type,
                points=-points,  # 使用积分记录为负数
                balance_after=available_points - points,
                reference_id=reference_id,
                description=description or f"{event_type}使用积分",
                created_at=datetime.utcnow()
            )
            
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            
            # ================== 清除积分缓存 ==================
            self._clear_point_cache(user_id)
            
            # ================== 记录安全审计日志 ==================
            security_logger.log_point_transaction(user_id, {
                "transaction_id": transaction.transaction_id,
                "type": "USE",
                "points": -points,
                "event_type": event_type,
                "reference_id": reference_id,
                "new_balance": transaction.balance_after
            })
            
            logger.info(f"积分使用成功: user_id={user_id}, points={points}, event={event_type}")
            return transaction
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"积分使用失败: user_id={user_id}, error={str(e)}")
            raise HTTPException(status_code=500, detail="积分使用处理失败")

    def _get_available_points(self, user_id: int) -> int:
        """
        获取用户当前可用积分
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            int: 可用积分数量
        """
        try:
            # ================== 缓存检查 ==================
            cache_key = f"{self.cache_prefix}available:{user_id}"
            cached_points = self.redis.get(cache_key)
            
            if cached_points:
                return int(cached_points)
            
            # ================== 数据库计算 ==================
            # 计算总获得积分（未过期）
            total_earned = self.db.query(func.coalesce(func.sum(PointTransaction.points), 0)).filter(
                and_(
                    PointTransaction.user_id == user_id,
                    PointTransaction.transaction_type == "EARN",
                    or_(
                        PointTransaction.expiry_date.is_(None),
                        PointTransaction.expiry_date > datetime.utcnow()
                    )
                )
            ).scalar()
            
            # 计算总使用积分
            total_used = self.db.query(func.coalesce(func.sum(func.abs(PointTransaction.points)), 0)).filter(
                and_(
                    PointTransaction.user_id == user_id,
                    PointTransaction.transaction_type == "USE"
                )
            ).scalar()
            
            available_points = int(total_earned - total_used)
            
            # ================== 缓存结果 ==================
            self.redis.setex(cache_key, self.cache_ttl, available_points)
            
            return available_points
            
        except Exception as e:
            logger.error(f"计算可用积分失败: user_id={user_id}, error={str(e)}")
            return 0

    def _clear_point_cache(self, user_id: int) -> None:
        """
        清除积分相关缓存
        
        Args:
            user_id (int): 用户ID
        """
        try:
            cache_keys = [
                f"{self.cache_prefix}available:{user_id}",
                f"{self.cache_prefix}transactions:{user_id}:*"
            ]
            
            for pattern in cache_keys:
                if "*" in pattern:
                    # 模糊匹配删除
                    keys = self.redis.keys(pattern)
                    if keys:
                        self.redis.delete(*keys)
                else:
                    self.redis.delete(pattern)
                    
        except Exception as e:
            logger.warning(f"清除积分缓存失败: user_id={user_id}, error={str(e)}")


class BenefitService:
    """
    会员权益业务逻辑服务类
    
    功能描述：
        处理会员权益相关的业务逻辑，包括权益检查、使用统计、权益变更等。
        支持6种权益类型的完整业务逻辑：免邮、生日礼品、优先服务、专属活动、积分倍数、专属客服。
        
    主要方法：
        - check_benefit_eligibility(): 检查权益资格
        - use_benefit(): 使用权益并记录
        - get_benefit_usage_stats(): 获取权益使用统计
        - update_benefit_settings(): 更新权益配置
        
    使用方式：
        ```python
        benefit_service = BenefitService(db_session, redis_client)
        eligible = benefit_service.check_benefit_eligibility(user_id, "free_shipping")
        ```
        
    Dependencies:
        - SQLAlchemy Session: 数据库操作
        - Redis Client: 缓存管理
        - SecurityLogger: 安全审计记录
    """

    def __init__(self, db: Session, redis_client: Optional[Redis] = None):
        """
        初始化权益服务
        
        Args:
            db (Session): 数据库会话
            redis_client (Optional[Redis]): Redis客户端
        """
        self.db = db
        self.redis = redis_client or get_redis_client()
        self.cache_prefix = "benefits:"
        self.cache_ttl = 3600  # 1小时缓存过期时间
        
        # 权益类型定义
        self.benefit_types = {
            "free_shipping": "免运费",
            "birthday_gift": "生日礼品",
            "priority_service": "优先服务", 
            "exclusive_events": "专属活动",
            "points_multiplier": "积分倍数",
            "custom_service": "专属客服"
        }

    def check_benefit_eligibility(self, user_id: int, benefit_type: str) -> Dict[str, Any]:
        """
        检查用户权益资格
        
        Args:
            user_id (int): 用户ID
            benefit_type (str): 权益类型
            
        Returns:
            Dict[str, Any]: 权益资格信息
            
        Raises:
            HTTPException:
                - 400: 权益类型无效
                - 404: 会员不存在
                - 500: 查询失败
        """
        if benefit_type not in self.benefit_types:
            raise HTTPException(status_code=400, detail=f"无效的权益类型: {benefit_type}")
        
        try:
            # ================== 缓存检查 ==================
            cache_key = f"{self.cache_prefix}eligibility:{user_id}:{benefit_type}"
            cached_result = self.redis.get(cache_key)
            
            if cached_result:
                return json.loads(cached_result)
            
            # ================== 获取会员信息 ==================
            member_service = MemberService(self.db, self.redis)
            member = member_service.get_member_by_user_id(user_id)
            if not member:
                raise HTTPException(status_code=404, detail="会员信息不存在")
            
            # ================== 查询权益配置 ==================
            benefit = self.db.query(MembershipBenefit).filter(
                and_(
                    MembershipBenefit.level_id == member.level_id,
                    MembershipBenefit.benefit_type == benefit_type,
                    MembershipBenefit.is_active == True
                )
            ).first()
            
            # ================== 构建资格信息 ==================
            eligibility_info = {
                "user_id": user_id,
                "benefit_type": benefit_type,
                "benefit_name": self.benefit_types[benefit_type],
                "eligible": False,
                "level_required": False,
                "usage_limit": 0,
                "used_count": 0,
                "remaining_count": 0,
                "reset_cycle": None,
                "next_reset_date": None
            }
            
            if benefit:
                # ================== 计算使用统计 ==================
                usage_stats = self._get_benefit_usage_stats(user_id, benefit_type)
                
                eligibility_info.update({
                    "eligible": True,
                    "level_required": True,
                    "usage_limit": benefit.usage_limit if benefit.usage_limit else 999999,
                    "used_count": usage_stats["used_count"],
                    "remaining_count": max(0, (benefit.usage_limit or 999999) - usage_stats["used_count"]),
                    "reset_cycle": benefit.reset_cycle,
                    "next_reset_date": usage_stats["next_reset_date"]
                })
            
            # ================== 缓存结果 ==================
            self.redis.setex(cache_key, self.cache_ttl, json.dumps(eligibility_info, ensure_ascii=False))
            
            return eligibility_info
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"检查权益资格失败: user_id={user_id}, benefit_type={benefit_type}, error={str(e)}")
            raise HTTPException(status_code=500, detail="检查权益资格失败")

    def use_benefit(
        self,
        user_id: int,
        benefit_type: str,
        reference_id: Optional[str] = None,
        description: Optional[str] = None,
        benefit_value: Optional[Decimal] = None
    ) -> BenefitUsage:
        """
        使用会员权益
        
        Args:
            user_id (int): 用户ID
            benefit_type (str): 权益类型
            reference_id (Optional[str]): 关联订单或活动ID
            description (Optional[str]): 使用描述
            benefit_value (Optional[Decimal]): 权益价值（如优惠金额）
            
        Returns:
            BenefitUsage: 权益使用记录
            
        Raises:
            HTTPException:
                - 400: 权益不可用或已达使用限制
                - 404: 会员不存在
                - 500: 处理失败
        """
        try:
            # ================== 检查权益资格 ==================
            eligibility = self.check_benefit_eligibility(user_id, benefit_type)
            
            if not eligibility["eligible"]:
                raise HTTPException(status_code=400, detail=f"用户不具备{eligibility['benefit_name']}权益")
            
            if eligibility["remaining_count"] <= 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"{eligibility['benefit_name']}使用次数已达上限"
                )
            
            # ================== 创建使用记录 ==================
            usage_record = BenefitUsage(
                user_id=user_id,
                benefit_type=benefit_type,
                reference_id=reference_id,
                description=description or f"使用{eligibility['benefit_name']}",
                benefit_value=benefit_value,
                used_at=datetime.utcnow()
            )
            
            self.db.add(usage_record)
            self.db.commit()
            self.db.refresh(usage_record)
            
            # ================== 清除相关缓存 ==================
            self._clear_benefit_cache(user_id, benefit_type)
            
            # ================== 记录安全审计日志 ==================
            security_logger.log_benefit_usage(user_id, {
                "usage_id": usage_record.usage_id,
                "benefit_type": benefit_type,
                "benefit_name": eligibility["benefit_name"],
                "reference_id": reference_id,
                "benefit_value": float(benefit_value) if benefit_value else None,
                "used_at": usage_record.used_at
            })
            
            logger.info(f"权益使用成功: user_id={user_id}, benefit={benefit_type}, reference={reference_id}")
            return usage_record
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"使用权益失败: user_id={user_id}, benefit_type={benefit_type}, error={str(e)}")
            raise HTTPException(status_code=500, detail="使用权益失败")

    def get_benefit_usage_history(
        self,
        user_id: int,
        benefit_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        获取权益使用历史
        
        Args:
            user_id (int): 用户ID
            benefit_type (Optional[str]): 权益类型过滤
            start_date (Optional[datetime]): 开始日期
            end_date (Optional[datetime]): 结束日期
            page (int): 页码
            limit (int): 每页数量
            
        Returns:
            Dict[str, Any]: 权益使用历史和分页信息
        """
        try:
            # ================== 构建查询条件 ==================
            query = self.db.query(BenefitUsage).filter(BenefitUsage.user_id == user_id)
            
            if benefit_type:
                query = query.filter(BenefitUsage.benefit_type == benefit_type)
            
            if start_date:
                query = query.filter(BenefitUsage.used_at >= start_date)
                
            if end_date:
                query = query.filter(BenefitUsage.used_at <= end_date)
            
            # ================== 计算总数和分页 ==================
            total_count = query.count()
            total_pages = (total_count + limit - 1) // limit
            
            usage_records = query.order_by(desc(BenefitUsage.used_at)).offset(
                (page - 1) * limit
            ).limit(limit).all()
            
            # ================== 构建返回数据 ==================
            usage_list = []
            for record in usage_records:
                usage_list.append({
                    "usage_id": record.usage_id,
                    "benefit_type": record.benefit_type,
                    "benefit_name": self.benefit_types.get(record.benefit_type, record.benefit_type),
                    "reference_id": record.reference_id,
                    "description": record.description,
                    "benefit_value": float(record.benefit_value) if record.benefit_value else None,
                    "used_at": record.used_at.isoformat()
                })
            
            return {
                "usage_history": usage_list,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "total_pages": total_pages
                }
            }
            
        except Exception as e:
            logger.error(f"获取权益使用历史失败: user_id={user_id}, error={str(e)}")
            raise HTTPException(status_code=500, detail="获取权益使用历史失败")

    def _get_benefit_usage_stats(self, user_id: int, benefit_type: str) -> Dict[str, Any]:
        """
        获取权益使用统计
        
        Args:
            user_id (int): 用户ID
            benefit_type (str): 权益类型
            
        Returns:
            Dict[str, Any]: 使用统计信息
        """
        # 获取权益配置
        member_service = MemberService(self.db, self.redis)
        member = member_service.get_member_by_user_id(user_id)
        
        benefit = self.db.query(MembershipBenefit).filter(
            and_(
                MembershipBenefit.level_id == member.level_id,
                MembershipBenefit.benefit_type == benefit_type
            )
        ).first()
        
        if not benefit:
            return {"used_count": 0, "next_reset_date": None}
        
        # 计算统计周期
        now = datetime.utcnow()
        if benefit.reset_cycle == "DAILY":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            next_reset = start_date + timedelta(days=1)
        elif benefit.reset_cycle == "WEEKLY":
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            next_reset = start_date + timedelta(weeks=1)
        elif benefit.reset_cycle == "MONTHLY":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                next_reset = start_date.replace(year=now.year+1, month=1)
            else:
                next_reset = start_date.replace(month=now.month+1)
        else:
            # 无周期限制，统计所有使用记录
            start_date = None
            next_reset = None
        
        # 查询使用次数
        query = self.db.query(func.count(BenefitUsage.usage_id)).filter(
            and_(
                BenefitUsage.user_id == user_id,
                BenefitUsage.benefit_type == benefit_type
            )
        )
        
        if start_date:
            query = query.filter(BenefitUsage.used_at >= start_date)
        
        used_count = query.scalar() or 0
        
        return {
            "used_count": used_count,
            "next_reset_date": next_reset.isoformat() if next_reset else None
        }

    def _clear_benefit_cache(self, user_id: int, benefit_type: str) -> None:
        """
        清除权益相关缓存
        
        Args:
            user_id (int): 用户ID
            benefit_type (str): 权益类型
        """
        try:
            cache_patterns = [
                f"{self.cache_prefix}eligibility:{user_id}:{benefit_type}",
                f"{self.cache_prefix}stats:{user_id}:{benefit_type}",
                f"{self.cache_prefix}history:{user_id}:*"
            ]
            
            for pattern in cache_patterns:
                if "*" in pattern:
                    keys = self.redis.keys(pattern)
                    if keys:
                        self.redis.delete(*keys)
                else:
                    self.redis.delete(pattern)
                    
        except Exception as e:
            logger.warning(f"清除权益缓存失败: user_id={user_id}, benefit_type={benefit_type}, error={str(e)}")


class EventService:
    """
    会员活动业务逻辑服务类
    
    功能描述：
        处理会员活动相关的业务逻辑，包括活动管理、参与记录、奖励发放等。
        按照事件驱动架构设计实现，支持异步消息处理和状态管理。
        
    主要方法：
        - create_activity(): 创建会员活动
        - join_activity(): 参与会员活动
        - get_user_activities(): 获取用户参与的活动
        - process_activity_rewards(): 处理活动奖励
        
    使用方式：
        ```python
        event_service = EventService(db_session, redis_client)
        participation = event_service.join_activity(user_id, activity_id)
        ```
        
    Dependencies:
        - SQLAlchemy Session: 数据库操作
        - Redis Client: 缓存管理和消息队列
        - SecurityLogger: 安全审计记录
    """

    def __init__(self, db: Session, redis_client: Optional[Redis] = None):
        """
        初始化活动服务
        
        Args:
            db (Session): 数据库会话
            redis_client (Optional[Redis]): Redis客户端
        """
        self.db = db
        self.redis = redis_client or get_redis_client()
        self.cache_prefix = "activities:"
        self.cache_ttl = 1800  # 30分钟缓存过期时间

    def create_activity(
        self,
        title: str,
        description: str,
        activity_type: str,
        start_time: datetime,
        end_time: datetime,
        max_participants: Optional[int] = None,
        reward_config: Optional[Dict[str, Any]] = None,
        participation_rules: Optional[Dict[str, Any]] = None
    ) -> MemberActivity:
        """
        创建会员活动
        
        Args:
            title (str): 活动标题
            description (str): 活动描述
            activity_type (str): 活动类型
            start_time (datetime): 开始时间
            end_time (datetime): 结束时间
            max_participants (Optional[int]): 最大参与人数
            reward_config (Optional[Dict]): 奖励配置
            participation_rules (Optional[Dict]): 参与规则
            
        Returns:
            MemberActivity: 创建的活动信息
            
        Raises:
            HTTPException:
                - 400: 参数错误
                - 500: 创建失败
        """
        try:
            # ================== 参数验证 ==================
            if start_time >= end_time:
                raise HTTPException(status_code=400, detail="活动开始时间必须早于结束时间")
            
            if start_time <= datetime.utcnow():
                raise HTTPException(status_code=400, detail="活动开始时间必须晚于当前时间")
            
            # ================== 创建活动记录 ==================
            activity = MemberActivity(
                title=title,
                description=description,
                activity_type=activity_type,
                start_time=start_time,
                end_time=end_time,
                max_participants=max_participants,
                current_participants=0,
                status="PENDING",  # 待开始
                reward_config=reward_config or {},
                participation_rules=participation_rules or {},
                created_at=datetime.utcnow()
            )
            
            self.db.add(activity)
            self.db.commit()
            self.db.refresh(activity)
            
            # ================== 缓存活动信息 ==================
            self._cache_activity_info(activity)
            
            # ================== 记录安全审计日志 ==================
            security_logger.log_activity_creation({
                "activity_id": activity.activity_id,
                "title": title,
                "activity_type": activity_type,
                "start_time": start_time,
                "end_time": end_time,
                "created_by": "admin"  # 实际应从JWT获取创建者信息
            })
            
            logger.info(f"创建会员活动成功: activity_id={activity.activity_id}, title={title}")
            return activity
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建会员活动失败: title={title}, error={str(e)}")
            raise HTTPException(status_code=500, detail="创建会员活动失败")

    def join_activity(self, user_id: int, activity_id: int) -> ActivityParticipation:
        """
        用户参与会员活动
        
        Args:
            user_id (int): 用户ID
            activity_id (int): 活动ID
            
        Returns:
            ActivityParticipation: 参与记录
            
        Raises:
            HTTPException:
                - 400: 活动不可参与
                - 404: 活动不存在或用户不存在
                - 409: 重复参与
                - 500: 处理失败
        """
        try:
            # ================== 验证用户和活动 ==================
            member_service = MemberService(self.db, self.redis)
            member = member_service.get_member_by_user_id(user_id)
            if not member:
                raise HTTPException(status_code=404, detail="会员信息不存在")
            
            activity = self.db.query(MemberActivity).filter(
                MemberActivity.activity_id == activity_id
            ).first()
            if not activity:
                raise HTTPException(status_code=404, detail="活动不存在")
            
            # ================== 检查活动状态 ==================
            now = datetime.utcnow()
            if activity.status != "ACTIVE" and now < activity.start_time:
                raise HTTPException(status_code=400, detail="活动尚未开始")
            
            if now > activity.end_time:
                raise HTTPException(status_code=400, detail="活动已结束")
            
            if activity.max_participants and activity.current_participants >= activity.max_participants:
                raise HTTPException(status_code=400, detail="活动参与人数已达上限")
            
            # ================== 检查重复参与 ==================
            existing_participation = self.db.query(ActivityParticipation).filter(
                and_(
                    ActivityParticipation.user_id == user_id,
                    ActivityParticipation.activity_id == activity_id
                )
            ).first()
            
            if existing_participation:
                raise HTTPException(status_code=409, detail="用户已参与该活动")
            
            # ================== 创建参与记录 ==================
            participation = ActivityParticipation(
                user_id=user_id,
                activity_id=activity_id,
                participation_time=now,
                status="ACTIVE",
                progress_data={}
            )
            
            # 更新活动参与人数
            activity.current_participants += 1
            
            self.db.add(participation)
            self.db.commit()
            self.db.refresh(participation)
            
            # ================== 清除相关缓存 ==================
            self._clear_activity_cache(activity_id)
            
            # ================== 记录安全审计日志 ==================
            security_logger.log_activity_participation(user_id, {
                "participation_id": participation.participation_id,
                "activity_id": activity_id,
                "activity_title": activity.title,
                "participation_time": participation.participation_time
            })
            
            logger.info(f"用户参与活动成功: user_id={user_id}, activity_id={activity_id}")
            return participation
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"用户参与活动失败: user_id={user_id}, activity_id={activity_id}, error={str(e)}")
            raise HTTPException(status_code=500, detail="参与活动失败")

    def get_user_activities(
        self,
        user_id: int,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        获取用户参与的活动列表
        
        Args:
            user_id (int): 用户ID
            status (Optional[str]): 活动状态过滤
            page (int): 页码
            limit (int): 每页数量
            
        Returns:
            Dict[str, Any]: 活动列表和分页信息
        """
        try:
            # ================== 构建查询条件 ==================
            query = self.db.query(ActivityParticipation).filter(
                ActivityParticipation.user_id == user_id
            ).join(MemberActivity)
            
            if status:
                query = query.filter(MemberActivity.status == status)
            
            # ================== 计算总数和分页 ==================
            total_count = query.count()
            total_pages = (total_count + limit - 1) // limit
            
            participations = query.order_by(desc(ActivityParticipation.participation_time)).offset(
                (page - 1) * limit
            ).limit(limit).all()
            
            # ================== 构建返回数据 ==================
            activity_list = []
            for participation in participations:
                activity = participation.activity
                activity_list.append({
                    "participation_id": participation.participation_id,
                    "activity_id": activity.activity_id,
                    "title": activity.title,
                    "description": activity.description,
                    "activity_type": activity.activity_type,
                    "start_time": activity.start_time.isoformat(),
                    "end_time": activity.end_time.isoformat(),
                    "status": activity.status,
                    "participation_time": participation.participation_time.isoformat(),
                    "participation_status": participation.status,
                    "progress_data": participation.progress_data
                })
            
            return {
                "activities": activity_list,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "total_pages": total_pages
                }
            }
            
        except Exception as e:
            logger.error(f"获取用户活动失败: user_id={user_id}, error={str(e)}")
            raise HTTPException(status_code=500, detail="获取用户活动失败")

    def _cache_activity_info(self, activity: MemberActivity) -> None:
        """
        缓存活动信息
        
        Args:
            activity (MemberActivity): 活动信息
        """
        try:
            cache_key = f"{self.cache_prefix}activity:{activity.activity_id}"
            activity_data = {
                "activity_id": activity.activity_id,
                "title": activity.title,
                "activity_type": activity.activity_type,
                "status": activity.status,
                "start_time": activity.start_time.isoformat(),
                "end_time": activity.end_time.isoformat(),
                "max_participants": activity.max_participants,
                "current_participants": activity.current_participants,
                "last_cached": datetime.utcnow().isoformat()
            }
            
            self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(activity_data, ensure_ascii=False)
            )
            
        except Exception as e:
            logger.warning(f"缓存活动信息失败: activity_id={activity.activity_id}, error={str(e)}")

    def _clear_activity_cache(self, activity_id: int) -> None:
        """
        清除活动相关缓存
        
        Args:
            activity_id (int): 活动ID
        """
        try:
            cache_keys = [
                f"{self.cache_prefix}activity:{activity_id}",
                f"{self.cache_prefix}participants:{activity_id}:*",
                f"{self.cache_prefix}user_activities:*"
            ]
            
            for pattern in cache_keys:
                if "*" in pattern:
                    keys = self.redis.keys(pattern)
                    if keys:
                        self.redis.delete(*keys)
                else:
                    self.redis.delete(pattern)
                    
        except Exception as e:
            logger.warning(f"清除活动缓存失败: activity_id={activity_id}, error={str(e)}")


# ================== 服务工厂函数 ==================

def get_member_service(db: Session, redis_client: Optional[Redis] = None) -> MemberService:
    """
    获取会员服务实例
    
    Args:
        db (Session): 数据库会话
        redis_client (Optional[Redis]): Redis客户端
        
    Returns:
        MemberService: 会员服务实例
    """
    return MemberService(db, redis_client)


def get_point_service(db: Session, redis_client: Optional[Redis] = None) -> PointService:
    """
    获取积分服务实例
    
    Args:
        db (Session): 数据库会话
        redis_client (Optional[Redis]): Redis客户端
        
    Returns:
        PointService: 积分服务实例
    """
    return PointService(db, redis_client)


def get_benefit_service(db: Session, redis_client: Optional[Redis] = None) -> BenefitService:
    """
    获取权益服务实例
    
    Args:
        db (Session): 数据库会话
        redis_client (Optional[Redis]): Redis客户端
        
    Returns:
        BenefitService: 权益服务实例
    """
    return BenefitService(db, redis_client)


def get_event_service(db: Session, redis_client: Optional[Redis] = None) -> EventService:
    """
    获取活动服务实例
    
    Args:
        db (Session): 数据库会话
        redis_client (Optional[Redis]): Redis客户端
        
    Returns:
        EventService: 活动服务实例
    """
    return EventService(db, redis_client)
