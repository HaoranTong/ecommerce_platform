"""
会员系统模块核心业务逻辑服务层

遵循四层架构设计，实现会员相关的所有业务逻辑。
严格按照 design.md 文档要求，提供会员档案、积分、等级、权益管理功能。
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from redis import Redis

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security_logger import SecurityLogger
from .models import MemberLevel, MemberPoint, MemberProfile, PointTransaction
from .repository import LevelRepository, MemberRepository, PointRepository
from .exceptions import (
    MemberNotFoundException,
    MemberAlreadyExistsException,
    InsufficientPointsException,
    InvalidPointsAmountException,
    DuplicatePointOperationException,
    LevelNotFoundException,
    MemberStatusAbnormalException,
    MemberSystemException,
)

logger = logging.getLogger(__name__)
security_logger = SecurityLogger()


class MemberService:
    """
    会员业务服务层
    
    提供会员档案管理的核心业务逻辑，包括注册、查询、更新等功能。
    严格遵循设计文档中的业务流程和规则。
    """

    def __init__(self, db: Session, redis_client: Optional["Redis"] = None):
        self.db = db
        self.redis = redis_client
        self._member_repo = MemberRepository(db)
        self._point_repo = PointRepository(db)
        self._level_repo = LevelRepository(db)
        self.cache_prefix = "member_system:"

    def get_member_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        获取完整会员档案信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            完整的会员档案信息，包含等级、积分、权益等
            
        Raises:
            MemberSystemException: 系统异常
        """
        try:
            # 1. 尝试从Redis缓存获取
            if self.redis:
                cache_key = f"{self.cache_prefix}profile:{user_id}"
                try:
                    import json
                    cached_data = self.redis.get(cache_key)
                    if cached_data:
                        if isinstance(cached_data, bytes):
                            cached_payload = cached_data.decode("utf-8")
                        elif isinstance(cached_data, str):
                            cached_payload = cached_data
                        else:
                            cached_payload = None

                        if cached_payload:
                            logger.debug(f"从Redis缓存获取会员档案: user_id={user_id}")
                            return json.loads(cached_payload)

                        logger.debug(
                            "Redis缓存返回非字符串数据，忽略此次缓存命中",
                            extra={"user_id": user_id, "type": type(cached_data).__name__},
                        )
                except Exception as e:
                    logger.warning(f"Redis缓存读取失败: user_id={user_id}, error={e}")
            
            # 2. 从数据库获取会员基础信息
            member = self._member_repo.get_profile_by_user_id(user_id)
            if not member:
                return None

            # 3. 获取积分信息
            member_points = self._point_repo.get_member_points(user_id)
            point_summary = self._build_point_summary(member_points)

            # 4. 构建完整档案信息
            profile_data = {
                "member_id": str(member.id),
                "user_id": member.user_id,
                "level": {
                    "level_id": member.level.id,
                    "level_name": member.level.level_name,
                    "min_points": member.level.min_points,
                    "discount_rate": float(member.level.discount_rate),
                },
                "points": point_summary,
                "statistics": {
                    "total_spent": float(member.total_spent or 0),
                    "join_date": member.join_date.isoformat(),
                    "last_active": (
                        member.last_active_at.isoformat()
                        if member.last_active_at
                        else None
                    ),
                },
                "benefits": self._get_member_benefits(member.level),
            }

            # 5. 写入Redis缓存（TTL: 300秒）
            if self.redis:
                try:
                    import json
                    cache_key = f"{self.cache_prefix}profile:{user_id}"
                    self.redis.setex(cache_key, 300, json.dumps(profile_data, ensure_ascii=False))
                    logger.debug(f"会员档案写入Redis缓存: user_id={user_id}")
                except Exception as e:
                    logger.warning(f"Redis缓存写入失败: user_id={user_id}, error={e}")

            # 6. 记录访问日志
            security_logger.log_member_access(
                user_id,
                "profile_view",
                {"member_id": member.id, "level": member.level.level_name},
            )

            return profile_data

        except MemberSystemException:
            raise
        except Exception as e:
            logger.error(f"获取会员档案失败: user_id={user_id}, error={e}")
            raise

    def create_member(
        self, user_id: int, *, nickname: str, birthday: Optional[date] = None
    ) -> MemberProfile:
        """
        创建新会员
        
        Args:
            user_id: 用户ID
            nickname: 会员昵称
            birthday: 生日（可选）
            
        Returns:
            创建的会员档案
            
        Raises:
            MemberAlreadyExistsException: 用户已是会员
            LevelNotFoundException: 系统未配置会员等级
        """
        try:
            # 检查是否已是会员
            existing_member = self._member_repo.get_profile_by_user_id(user_id)
            if existing_member:
                raise MemberAlreadyExistsException(user_id)

            # 获取初始等级
            initial_level = self._level_repo.get_initial_level()
            if not initial_level:
                raise LevelNotFoundException()

            # 生成会员编号
            member_code = self._generate_member_code(user_id)

            # 创建会员档案
            member = self._member_repo.create_profile(
                user_id=user_id,
                member_code=member_code,
                level_id=initial_level.id,
                join_date=date.today(),
                birthday=birthday,
                preferences={"nickname": nickname},
            )

            # 创建积分账户
            self._point_repo.create_member_points(
                user_id=user_id, level_id=initial_level.id
            )

            self.db.commit()

            logger.info(f"创建会员成功: user_id={user_id}, member_code={member_code}")
            return member

        except (MemberAlreadyExistsException, LevelNotFoundException):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建会员失败: user_id={user_id}, error={e}")
            raise

    def update_member_profile(
        self,
        user_id: int,
        *,
        birthday: Optional[date] = None,
        preferences: Optional[dict] = None,
        nickname: Optional[str] = None,
        gender: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> MemberProfile:
        """
        更新会员档案信息
        
        Args:
            user_id: 用户ID
            birthday: 新的生日
            preferences: 偏好设置
            
        Returns:
            更新后的会员档案
            
        Raises:
            MemberNotFoundException: 会员信息不存在
        """
        try:
            member = self._member_repo.get_profile_by_user_id(user_id)
            if not member:
                raise MemberNotFoundException(user_id)

            # 合并偏好、昵称等扩展信息
            merged_preferences = dict(member.preferences or {})
            if preferences:
                merged_preferences.update(preferences)

            extra_fields = {
                "nickname": nickname,
                "gender": gender,
                "phone": phone,
            }
            for key, value in extra_fields.items():
                if value is not None:
                    merged_preferences[key] = value

            # 更新档案信息
            updated_member = self._member_repo.update_profile(
                member,
                birthday=birthday,
                preferences=merged_preferences if merged_preferences else member.preferences,
                last_active_at=datetime.utcnow(),
            )

            self.db.commit()
            
            # 清除Redis缓存
            if self.redis:
                try:
                    cache_key = f"{self.cache_prefix}profile:{user_id}"
                    self.redis.delete(cache_key)
                    logger.debug(f"清除会员档案Redis缓存: user_id={user_id}")
                except Exception as e:
                    logger.warning(f"清除Redis缓存失败: user_id={user_id}, error={e}")
            
            return updated_member

        except MemberNotFoundException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新会员档案失败: user_id={user_id}, error={e}")
            raise

    def _build_point_summary(self, member_points: Optional[MemberPoint]) -> Dict[str, Any]:
        """构建积分汇总信息"""
        if not member_points:
            return {
                "total_earned": 0,
                "current_points": 0,
                "total_used": 0,
                "frozen_points": 0,
            }

        return {
            "total_earned": member_points.total_earned,
            "current_points": member_points.current_points,
            "total_used": member_points.total_used,
            "frozen_points": 0,  # 暂未实现冻结积分功能
        }

    def _get_member_benefits(self, level: MemberLevel) -> Dict[str, Any]:
        """获取会员等级权益"""
        if not level.benefits:
            return {}
        
        return level.benefits

    def _generate_member_code(self, user_id: int) -> str:
        """生成会员编号"""
        today = datetime.utcnow()
        return f"M{today.strftime('%Y%m%d')}{user_id:06d}"


class PointService:
    """
    积分业务服务层
    
    提供积分相关的核心业务逻辑，包括积分获得、使用、查询等功能。
    """

    def __init__(self, db: Session, redis_client: Optional["Redis"] = None):
        self.db = db
        self.redis = redis_client
        self._point_repo = PointRepository(db)
        self._member_repo = MemberRepository(db)
        self._level_repo = LevelRepository(db)

    def earn_points(
        self,
        user_id: int,
        points: int,
        *,
        reference_id: Optional[str] = None,
        reference_type: str = "manual",
        description: str = "积分获得",
    ) -> PointTransaction:
        """
        用户获得积分
        
        Args:
            user_id: 用户ID
            points: 积分数量
            reference_id: 关联业务ID（如订单ID）
            reference_type: 关联业务类型
            description: 描述
            
        Returns:
            积分交易记录
            
        Raises:
            InvalidPointsAmountException: 积分数量无效
            MemberNotFoundException: 用户不是会员
        """
        try:
            if points <= 0:
                raise InvalidPointsAmountException(points, "积分数量必须大于0")

            # 幂等性检查
            if reference_id:
                existing_transaction = self._point_repo.get_transaction_by_reference(
                    user_id=user_id,
                    reference_id=reference_id,
                    transaction_type="earn",
                )
                if existing_transaction:
                    logger.info(f"检测到重复积分操作，返回已有记录: reference_id={reference_id}")
                    return existing_transaction

            # 获取或创建积分账户
            member_points = self._point_repo.get_member_points(user_id)
            if not member_points:
                # 获取用户会员信息
                member = self._member_repo.get_profile_by_user_id(user_id)
                if not member:
                    raise MemberNotFoundException(user_id)
                
                member_points = self._point_repo.create_member_points(
                    user_id=user_id, level_id=member.level_id
                )

            # 创建积分交易记录
            transaction = self._point_repo.create_transaction(
                user_id=user_id,
                transaction_type="earn",
                points_change=points,
                reference_id=reference_id,
                reference_type=reference_type,
                description=description,
            )

            # 更新积分余额
            self._point_repo.update_points_balance(member_points, points)

            # 检查等级升级
            self._check_level_upgrade(user_id, member_points.total_earned)

            self.db.commit()

            logger.info(f"积分获得成功: user_id={user_id}, points={points}")
            return transaction

        except (InvalidPointsAmountException, MemberNotFoundException):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"积分获得失败: user_id={user_id}, error={e}")
            raise

    def use_points(
        self,
        user_id: int,
        points: int,
        *,
        reference_id: Optional[str] = None,
        reference_type: str = "manual",
        description: str = "积分使用",
    ) -> PointTransaction:
        """
        用户使用积分
        
        Args:
            user_id: 用户ID
            points: 积分数量
            reference_id: 关联业务ID
            reference_type: 关联业务类型
            description: 描述
            
        Returns:
            积分交易记录
            
        Raises:
            InvalidPointsAmountException: 积分数量无效
            MemberNotFoundException: 积分账户不存在
            InsufficientPointsException: 积分余额不足
        """
        try:
            if points <= 0:
                raise InvalidPointsAmountException(points, "积分数量必须大于0")

            # 幂等性检查
            if reference_id:
                existing_transaction = self._point_repo.get_transaction_by_reference(
                    user_id=user_id,
                    reference_id=reference_id,
                    transaction_type="use",
                )
                if existing_transaction:
                    logger.info(f"检测到重复积分操作，返回已有记录: reference_id={reference_id}")
                    return existing_transaction

            # 获取积分账户
            member_points = self._point_repo.get_member_points(user_id)
            if not member_points:
                raise MemberNotFoundException(user_id)

            if member_points.current_points < points:
                raise InsufficientPointsException(
                    required=points,
                    available=member_points.current_points
                )

            # 创建积分交易记录
            transaction = self._point_repo.create_transaction(
                user_id=user_id,
                transaction_type="use",
                points_change=-points,
                reference_id=reference_id,
                reference_type=reference_type,
                description=description,
            )

            # 更新积分余额
            self._point_repo.update_points_balance(member_points, -points)

            self.db.commit()

            logger.info(f"积分使用成功: user_id={user_id}, points={points}")
            return transaction

        except (InvalidPointsAmountException, MemberNotFoundException, InsufficientPointsException):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"积分使用失败: user_id={user_id}, error={e}")
            raise

    def get_point_balance(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户积分余额信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            积分余额信息
        """
        try:
            member_points = self._point_repo.get_member_points(user_id)
            if not member_points:
                return {
                    "current_points": 0,
                    "total_earned": 0,
                    "total_used": 0,
                }

            return {
                "current_points": member_points.current_points,
                "total_earned": member_points.total_earned,
                "total_used": member_points.total_used,
            }

        except Exception as e:
            logger.error(f"获取积分余额失败: user_id={user_id}, error={e}")
            raise

    def get_point_transactions(
        self,
        user_id: int,
        *,
        transaction_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[PointTransaction]:
        """
        获取用户积分交易历史
        
        Args:
            user_id: 用户ID
            transaction_type: 交易类型过滤
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            积分交易记录列表
        """
        try:
            return self._point_repo.get_transactions_by_user(
                user_id,
                transaction_type=transaction_type,
                limit=limit,
                offset=offset,
            )

        except Exception as e:
            logger.error(f"获取积分交易历史失败: user_id={user_id}, error={e}")
            raise

    def _check_level_upgrade(self, user_id: int, total_points: int) -> None:
        """检查并处理等级升级"""
        try:
            # 获取当前会员信息
            member = self._member_repo.get_profile_by_user_id(user_id)
            if not member:
                return

            # 查找符合条件的最高等级
            new_level = self._level_repo.find_eligible_level_by_points(total_points)
            if not new_level or new_level.id <= member.level_id:
                return

            # 升级等级
            self._member_repo.update_profile_level(member, new_level.id)

            logger.info(
                f"等级升级: user_id={user_id}, old_level={member.level_id}, "
                f"new_level={new_level.id}"
            )

        except Exception as e:
            logger.error(f"检查等级升级失败: user_id={user_id}, error={e}")


class LevelService:
    """
    等级业务服务层
    
    提供会员等级相关的业务逻辑。
    """

    def __init__(self, db: Session, redis_client: Optional["Redis"] = None):
        self.db = db
        self.redis = redis_client
        self._level_repo = LevelRepository(db)

    def get_all_levels(self) -> List[MemberLevel]:
        """获取所有会员等级
        
        Returns:
            会员等级列表
        """
        try:
            return self._level_repo.list_levels()
        except Exception as e:
            logger.error(f"获取会员等级列表失败: error={e}")
            raise

    def get_level_by_id(self, level_id: int) -> Optional[MemberLevel]:
        """根据ID获取等级信息
        
        Args:
            level_id: 等级ID
            
        Returns:
            等级信息，不存在返回None
        """
        try:
            return self._level_repo.get_level_by_id(level_id)
        except Exception as e:
            logger.error(f"获取会员等级失败: level_id={level_id}, error={e}")
            raise


class BenefitService:
    """
    权益业务服务层
    
    提供会员权益相关的业务逻辑，包括权益查询、资格检查、使用记录等。
    """

    def __init__(self, db: Session, redis_client: Optional["Redis"] = None):
        self.db = db
        self.redis = redis_client
        self._member_repo = MemberRepository(db)
        self._level_repo = LevelRepository(db)

    def get_member_benefits(self, user_id: int) -> Dict[str, Any]:
        """
        获取会员的所有可用权益
        
        Args:
            user_id: 用户ID
            
        Returns:
            权益列表及详细信息
            
        Raises:
            MemberNotFoundException: 会员不存在
        """
        try:
            member = self._member_repo.get_profile_by_user_id(user_id)
            if not member:
                raise MemberNotFoundException(user_id)

            # 获取等级权益配置
            level = member.level
            benefits_config = level.benefits or {}

            # 构建权益列表
            benefits = {
                "level_id": level.id,
                "level_name": level.level_name,
                "discount_rate": float(level.discount_rate),
                "benefits": self._parse_benefits_config(benefits_config),
                "special_privileges": self._get_special_privileges(level.id),
            }

            return benefits

        except MemberNotFoundException:
            raise
        except Exception as e:
            logger.error(f"获取会员权益失败: user_id={user_id}, error={e}")
            raise

    def get_level_benefits(self, level_id: int) -> Dict[str, Any]:
        """
        获取指定等级的权益信息
        
        Args:
            level_id: 等级ID
            
        Returns:
            等级权益详情
            
        Raises:
            LevelNotFoundException: 等级不存在
        """
        try:
            level = self._level_repo.get_level_by_id(level_id)
            if not level:
                raise LevelNotFoundException()

            benefits_config = level.benefits or {}

            return {
                "level_id": level.id,
                "level_name": level.level_name,
                "discount_rate": float(level.discount_rate),
                "min_points": level.min_points,
                "benefits": self._parse_benefits_config(benefits_config),
            }

        except LevelNotFoundException:
            raise
        except Exception as e:
            logger.error(f"获取等级权益失败: level_id={level_id}, error={e}")
            raise

    def check_benefit_eligibility(
        self, user_id: int, benefit_type: str
    ) -> Dict[str, Any]:
        """
        检查会员是否有资格使用某项权益
        
        Args:
            user_id: 用户ID
            benefit_type: 权益类型（如'free_shipping', 'birthday_gift'等）
            
        Returns:
            资格检查结果
        """
        try:
            member = self._member_repo.get_profile_by_user_id(user_id)
            if not member:
                raise MemberNotFoundException(user_id)

            # 检查会员状态
            if member.status != 1:  # MemberStatus.ACTIVE
                return {
                    "eligible": False,
                    "reason": "会员状态异常",
                    "benefit_type": benefit_type,
                }

            # 获取等级权益配置
            benefits_config = member.level.benefits or {}
            
            # 检查权益是否存在
            if benefit_type not in benefits_config:
                return {
                    "eligible": False,
                    "reason": "该等级不包含此权益",
                    "benefit_type": benefit_type,
                }

            # 检查权益的具体规则
            benefit_info = benefits_config[benefit_type]
            
            return {
                "eligible": True,
                "benefit_type": benefit_type,
                "benefit_info": benefit_info,
                "level_name": member.level.level_name,
            }

        except MemberNotFoundException:
            raise
        except Exception as e:
            logger.error(f"检查权益资格失败: user_id={user_id}, benefit_type={benefit_type}, error={e}")
            raise

    def _parse_benefits_config(self, benefits_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析权益配置JSON为结构化列表"""
        benefits_list = []
        
        for benefit_type, benefit_data in benefits_config.items():
            if isinstance(benefit_data, dict):
                benefits_list.append({
                    "type": benefit_type,
                    "name": benefit_data.get("name", benefit_type),
                    "description": benefit_data.get("description", ""),
                    "enabled": benefit_data.get("enabled", True),
                    "config": benefit_data.get("config", {}),
                })
            else:
                # 简单的值类型
                benefits_list.append({
                    "type": benefit_type,
                    "name": benefit_type,
                    "value": benefit_data,
                    "enabled": True,
                })
        
        return benefits_list

    def _get_special_privileges(self, level_id: int) -> List[str]:
        """获取等级特殊特权列表"""
        # 这里可以根据等级ID返回特殊特权
        # 示例实现
        privileges_map = {
            1: ["基础客服支持"],
            2: ["优先客服支持", "生日礼物"],
            3: ["专属客服", "生日礼物", "优先发货"],
            4: ["VIP专线", "生日礼物", "优先发货", "专属优惠"],
        }
        
        return privileges_map.get(level_id, [])


# ================== 服务工厂函数 ==================


def get_member_service(
    db: Session, redis_client: Optional["Redis"] = None
) -> MemberService:
    """获取会员服务实例"""
    return MemberService(db, redis_client)


def get_point_service(
    db: Session, redis_client: Optional["Redis"] = None
) -> PointService:
    """获取积分服务实例"""
    return PointService(db, redis_client)


def get_level_service(
    db: Session, redis_client: Optional["Redis"] = None
) -> LevelService:
    """获取等级服务实例"""
    return LevelService(db, redis_client)


def get_benefit_service(
    db: Session, redis_client: Optional["Redis"] = None
) -> BenefitService:
    """获取权益服务实例"""
    return BenefitService(db, redis_client)
