"""
会员系统模块核心业务逻辑服务层
严格遵循文档驱动开发原则，只实现当前models.py支持的核心功能
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

# Redis类型导入 - 用于类型注解
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from redis import Redis

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException

# 本地应用导入
from app.modules.member_system.models import (
    MemberProfile, MemberLevel, MemberPoint, PointTransaction
)
from app.core.security_logger import SecurityLogger

logger = logging.getLogger(__name__)
security_logger = SecurityLogger()


class MemberService:
    """
    会员业务服务 - 核心功能实现
    严格遵循models.py中已定义的数据结构
    """

    def __init__(self, db: Session, redis_client=None):
        self.db = db
        self.redis = redis_client
        self.cache_prefix = "member_system:"

    def get_member_by_user_id(self, user_id: int) -> Optional[MemberProfile]:
        """
        根据用户ID获取会员信息
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            Optional[MemberProfile]: 会员信息，如果不存在则返回None
        """
        try:
            # 查询会员信息，包含关联的等级信息
            member = self.db.query(MemberProfile).options(
                joinedload(MemberProfile.level)
            ).filter(MemberProfile.user_id == user_id).first()
            
            return member
            
        except SQLAlchemyError as e:
            logger.error(f"查询会员信息失败: user_id={user_id}, error={e}")
            raise HTTPException(status_code=500, detail="查询会员信息失败")

    def get_member_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        获取完整会员档案信息
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            Optional[Dict[str, Any]]: 完整的会员档案信息
        """
        try:
            # 获取会员基础信息
            member = self.get_member_by_user_id(user_id)
            if not member:
                return None
            
            # 获取等级信息
            level_info = self.db.query(MemberLevel).filter(
                MemberLevel.id == member.level_id
            ).first()
            
            if not level_info:
                logger.warning(f"会员等级信息缺失: member_id={member.id}")
                raise HTTPException(status_code=500, detail="会员等级信息异常")
            
            # 获取积分统计
            point_summary = self._get_point_summary(user_id)
            
            # 构建完整档案
            profile_data = {
                "member_id": member.id,
                "member_code": member.member_code,
                "user_id": member.user_id,
                "level": {
                    "level_id": level_info.id,
                    "level_name": level_info.level_name,
                    "min_points": level_info.min_points,
                    "discount_rate": float(level_info.discount_rate)
                },
                "points": point_summary,
                "profile": {
                    "total_spent": float(member.total_spent),
                    "join_date": member.join_date.isoformat(),
                    "last_active": member.last_active_at.isoformat() if member.last_active_at else None,
                    "birthday": member.birthday.isoformat() if member.birthday else None,
                    "preferences": member.preferences,
                    "status": member.status
                }
            }
            
            # 记录安全审计日志
            security_logger.log_member_access(user_id, "profile_view", {
                "member_id": member.id,
                "level": level_info.level_name,
                "timestamp": datetime.utcnow()
            })
            
            return profile_data
            
        except Exception as e:
            logger.error(f"获取会员档案失败: user_id={user_id}, error={e}")
            raise HTTPException(status_code=500, detail="获取会员档案失败")

    def create_member(self, user_id: int, member_data: dict) -> MemberProfile:
        """
        创建新会员
        
        Args:
            user_id (int): 用户ID
            member_data (dict): 会员数据
            
        Returns:
            MemberProfile: 创建的会员对象
        """
        try:
            # 检查是否已是会员
            existing_member = self.get_member_by_user_id(user_id)
            if existing_member:
                raise HTTPException(status_code=400, detail="用户已是会员")
            
            # 获取初始会员等级（默认为ID=1的等级）
            initial_level = self.db.query(MemberLevel).filter(
                MemberLevel.id == 1
            ).first()
            
            if not initial_level:
                logger.error("系统未配置基础会员等级")
                raise HTTPException(status_code=500, detail="会员系统配置异常")
            
            # 生成会员编号
            member_code = f"M{datetime.utcnow().strftime('%Y%m%d')}{user_id:04d}"
            
            # 创建会员记录
            new_member = MemberProfile(
                user_id=user_id,
                member_code=member_code,
                level_id=initial_level.id,
                join_date=datetime.utcnow().date(),
                birthday=member_data.get('birthday'),
                preferences=member_data.get('preferences') or {},
                status=1  # 默认为正常状态
            )
            
            self.db.add(new_member)
            self.db.commit()
            self.db.refresh(new_member)
            
            # 初始化积分账户
            self._create_member_points(user_id, initial_level.id)
            
            logger.info(f"创建会员成功: user_id={user_id}, member_code={member_code}")
            return new_member
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建会员失败: user_id={user_id}, error={e}")
            raise

    def _get_point_summary(self, user_id: int) -> Dict[str, Any]:
        """获取积分统计摘要"""
        try:
            # 获取积分账户信息
            member_points = self.db.query(MemberPoint).filter(
                MemberPoint.user_id == user_id
            ).first()
            
            if not member_points:
                return {
                    "current_points": 0,
                    "total_earned": 0,
                    "total_used": 0
                }
            
            return {
                "current_points": member_points.current_points,
                "total_earned": member_points.total_earned,
                "total_used": member_points.total_used
            }
            
        except Exception as e:
            logger.error(f"获取积分统计失败: user_id={user_id}, error={e}")
            return {"current_points": 0, "total_earned": 0, "total_used": 0}

    def _create_member_points(self, user_id: int, level_id: int):
        """创建积分账户"""
        try:
            member_points = MemberPoint(
                user_id=user_id,
                level_id=level_id,
                current_points=0,
                total_earned=0,
                total_used=0
            )
            
            self.db.add(member_points)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"创建积分账户失败: user_id={user_id}, error={e}")
            raise


class PointService:
    """
    积分业务服务 - 核心功能实现
    严格遵循models.py中已定义的数据结构
    """

    def __init__(self, db: Session, redis_client=None):
        self.db = db
        self.redis = redis_client

    def earn_points(self, user_id: int, points: int, reference_type: str, 
                   reference_id: str, description: str = "") -> PointTransaction:
        """
        积分发放
        
        Args:
            user_id (int): 用户ID
            points (int): 积分数量
            reference_type (str): 关联业务类型
            reference_id (str): 关联业务ID
            description (str): 描述
            
        Returns:
            PointTransaction: 积分交易记录
        """
        try:
            # 创建积分交易记录
            transaction = PointTransaction(
                user_id=user_id,
                transaction_type='earn',
                points_change=points,
                reference_type=reference_type,
                reference_id=reference_id,
                description=description or f"{reference_type}获得积分",
                status='completed'
            )
            
            self.db.add(transaction)
            
            # 更新积分账户
            member_points = self.db.query(MemberPoint).filter(
                MemberPoint.user_id == user_id
            ).first()
            
            if member_points:
                member_points.current_points += points
                member_points.total_earned += points
            else:
                # 如果积分账户不存在，创建一个
                member_points = MemberPoint(
                    user_id=user_id,
                    level_id=1,  # 默认等级
                    current_points=points,
                    total_earned=points,
                    total_used=0
                )
                self.db.add(member_points)
            
            self.db.commit()
            self.db.refresh(transaction)
            
            logger.info(f"积分发放成功: user_id={user_id}, points={points}")
            return transaction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"积分发放失败: user_id={user_id}, error={e}")
            raise

    def use_points(self, user_id: int, points: int, reference_type: str,
                  reference_id: str, description: str = "") -> PointTransaction:
        """
        积分使用
        
        Args:
            user_id (int): 用户ID  
            points (int): 积分数量
            reference_type (str): 关联业务类型
            reference_id (str): 关联业务ID
            description (str): 描述
            
        Returns:
            PointTransaction: 积分交易记录
        """
        try:
            # 检查积分余额
            member_points = self.db.query(MemberPoint).filter(
                MemberPoint.user_id == user_id
            ).first()
            
            if not member_points or member_points.current_points < points:
                raise HTTPException(status_code=400, detail="积分余额不足")
            
            # 创建积分交易记录
            transaction = PointTransaction(
                user_id=user_id,
                transaction_type='use',
                points_change=-points,
                reference_type=reference_type,
                reference_id=reference_id,
                description=description or f"{reference_type}使用积分",
                status='completed'
            )
            
            self.db.add(transaction)
            
            # 更新积分账户
            member_points.current_points -= points
            member_points.total_used += points
            
            self.db.commit()
            self.db.refresh(transaction)
            
            logger.info(f"积分使用成功: user_id={user_id}, points={points}")
            return transaction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"积分使用失败: user_id={user_id}, error={e}")
            raise


class BenefitService:
    """
    权益服务 - 处理会员权益相关业务逻辑
    严格遵循架构文档设计，支持等级权益管理
    """

    def __init__(self, db: Session, redis_client=None):
        self.db = db
        self.redis = redis_client
        self.cache_prefix = "benefits:"

    def get_available_benefits(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户可用权益
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            Dict[str, Any]: 可用权益信息
        """
        try:
            # 获取会员信息
            member = self.db.query(MemberProfile).filter(
                MemberProfile.user_id == user_id
            ).first()
            
            if not member:
                return {"benefits": [], "level": None}
            
            # 获取等级信息
            level = self.db.query(MemberLevel).filter(
                MemberLevel.id == member.level_id
            ).first()
            
            if not level or not level.benefits:
                return {"benefits": [], "level": level.level_name if level else None}
            
            return {
                "benefits": level.benefits,
                "level": level.level_name,
                "discount_rate": float(level.discount_rate)
            }
            
        except Exception as e:
            logger.error(f"获取权益失败: user_id={user_id}, error={e}")
            raise

    def calculate_discount(self, user_id: int, order_amount: Decimal) -> Decimal:
        """
        计算会员折扣
        
        Args:
            user_id (int): 用户ID
            order_amount (Decimal): 订单金额
            
        Returns:
            Decimal: 折扣后金额
        """
        try:
            member = self.db.query(MemberProfile).filter(
                MemberProfile.user_id == user_id
            ).first()
            
            if not member:
                return order_amount
            
            level = self.db.query(MemberLevel).filter(
                MemberLevel.id == member.level_id
            ).first()
            
            if not level:
                return order_amount
            
            # 计算折扣后金额
            discounted_amount = order_amount * level.discount_rate
            logger.info(f"计算折扣: user_id={user_id}, 原价={order_amount}, 折后={discounted_amount}")
            
            return discounted_amount
            
        except Exception as e:
            logger.error(f"计算折扣失败: user_id={user_id}, error={e}")
            return order_amount


class EventService:
    """
    活动服务 - 处理会员活动相关业务逻辑
    严格遵循架构文档设计，支持活动管理和参与记录
    """

    def __init__(self, db: Session, redis_client=None):
        self.db = db
        self.redis = redis_client
        self.cache_prefix = "events:"

    def get_available_events(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户可参与的活动
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            Dict[str, Any]: 可参与活动列表
        """
        try:
            # 获取会员信息
            member = self.db.query(MemberProfile).filter(
                MemberProfile.user_id == user_id
            ).first()
            
            if not member:
                return {"events": [], "member_level": None}
            
            level = self.db.query(MemberLevel).filter(
                MemberLevel.id == member.level_id
            ).first()
            
            # 基础活动框架 - 根据等级返回可参与活动
            events = []
            if level and level.level_name:
                events = [
                    {
                        "id": 1,
                        "title": f"{level.level_name}专属活动",
                        "type": "level_exclusive",
                        "description": "专为您的会员等级设计的特别活动"
                    }
                ]
            
            return {
                "events": events,
                "member_level": level.level_name if level else None
            }
            
        except Exception as e:
            logger.error(f"获取活动失败: user_id={user_id}, error={e}")
            return {"events": [], "member_level": None}

    def join_event(self, user_id: int, event_id: int, data: dict = None) -> Dict[str, Any]:
        """
        参与活动
        
        Args:
            user_id (int): 用户ID
            event_id (int): 活动ID
            data (dict): 参与数据
            
        Returns:
            Dict[str, Any]: 参与结果
        """
        try:
            # 基础实现 - 记录参与状态
            logger.info(f"用户参与活动: user_id={user_id}, event_id={event_id}")
            
            return {
                "success": True,
                "participation_id": f"{user_id}_{event_id}",
                "message": "成功参与活动"
            }
            
        except Exception as e:
            logger.error(f"参与活动失败: user_id={user_id}, event_id={event_id}, error={e}")
            return {
                "success": False,
                "message": "参与活动失败"
            }


# ================== 工厂函数 - 严格按照架构文档要求 ==================

def get_member_service(db: Session, redis_client: Optional["Redis"] = None) -> MemberService:
    """
    获取会员服务实例
    
    Args:
        db (Session): 数据库会话
        redis_client (Optional[Redis]): Redis客户端
        
    Returns:
        MemberService: 会员服务实例
    """
    return MemberService(db, redis_client)


def get_point_service(db: Session, redis_client: Optional["Redis"] = None) -> PointService:
    """
    获取积分服务实例
    
    Args:
        db (Session): 数据库会话
        redis_client (Optional[Redis]): Redis客户端
        
    Returns:
        PointService: 积分服务实例
    """
    return PointService(db, redis_client)


def get_benefit_service(db: Session, redis_client: Optional["Redis"] = None) -> BenefitService:
    """
    获取权益服务实例
    
    Args:
        db (Session): 数据库会话
        redis_client (Optional[Redis]): Redis客户端
        
    Returns:
        BenefitService: 权益服务实例
    """
    return BenefitService(db, redis_client)


def get_event_service(db: Session, redis_client: Optional["Redis"] = None) -> EventService:
    """
    获取活动服务实例
    
    Args:
        db (Session): 数据库会话
        redis_client (Optional[Redis]): Redis客户端
        
    Returns:
        EventService: 活动服务实例
    """
    return EventService(db, redis_client)