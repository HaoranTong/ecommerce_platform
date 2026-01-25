"""
会员系统模块数据访问层实现

遵循 Repository 模式，封装所有数据库操作，为 Service 层提供面向领域的数据访问接口。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from .models import MemberEventOutbox, MemberLevel, MemberPoint, MemberProfile, PointTransaction

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MemberDomainEvent:
    """会员领域事件数据载荷"""

    event_type: str
    payload: Dict[str, Any]
    available_at: Optional[datetime] = None


class MemberRepository:
    """会员档案数据访问仓储"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_profile_by_user_id(self, user_id: int) -> Optional[MemberProfile]:
        """根据用户ID查询会员档案并加载等级信息"""
        try:
            return (
                self.db.query(MemberProfile)
                .options(joinedload(MemberProfile.level))
                .filter(MemberProfile.user_id == user_id)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"查询会员档案失败: user_id={user_id}, error={e}")
            raise

    def get_profile_by_id(self, profile_id: int) -> Optional[MemberProfile]:
        """根据会员档案ID查询记录"""
        try:
            return (
                self.db.query(MemberProfile)
                .options(joinedload(MemberProfile.level))
                .filter(MemberProfile.id == profile_id)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"查询会员档案失败: profile_id={profile_id}, error={e}")
            raise

    def create_profile(
        self,
        *,
        user_id: int,
        member_code: str,
        level_id: int,
        join_date: date,
        birthday: Optional[date] = None,
        preferences: Optional[dict] = None,
    ) -> MemberProfile:
        """创建会员档案记录"""
        try:
            profile = MemberProfile(
                user_id=user_id,
                member_code=member_code,
                level_id=level_id,
                join_date=join_date,
                birthday=birthday,
                preferences=preferences or {},
            )
            self.db.add(profile)
            self.db.flush()
            self.db.refresh(profile)
            return profile
        except IntegrityError as e:
            logger.error(f"创建会员档案失败，数据冲突: user_id={user_id}, error={e}")
            raise ValueError(f"用户 {user_id} 已是会员或会员编号重复")
        except SQLAlchemyError as e:
            logger.error(f"创建会员档案失败: user_id={user_id}, error={e}")
            raise

    def update_profile(
        self,
        profile: MemberProfile,
        *,
        birthday: Optional[date] = None,
        preferences: Optional[dict] = None,
        last_active_at: Optional[datetime] = None,
        total_spent_delta: Optional[float] = None,
    ) -> MemberProfile:
        """更新会员档案信息"""
        try:
            if birthday is not None:
                profile.birthday = birthday
            if preferences is not None:
                profile.preferences = preferences
            if last_active_at is not None:
                profile.last_active_at = last_active_at
            if total_spent_delta is not None:
                profile.total_spent = (profile.total_spent or 0) + total_spent_delta

            self.db.flush()
            self.db.refresh(profile)
            return profile
        except SQLAlchemyError as e:
            logger.error(f"更新会员档案失败: profile_id={profile.id}, error={e}")
            raise

    def update_profile_level(
        self, profile: MemberProfile, level_id: int
    ) -> MemberProfile:
        """更新会员等级"""
        try:
            profile.level_id = level_id
            self.db.flush()
            self.db.refresh(profile)
            return profile
        except SQLAlchemyError as e:
            logger.error(f"更新会员等级失败: profile_id={profile.id}, error={e}")
            raise


class PointRepository:
    """积分数据访问仓储"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_member_points(self, user_id: int) -> Optional[MemberPoint]:
        """获取用户积分账户"""
        try:
            return (
                self.db.query(MemberPoint)
                .filter(MemberPoint.user_id == user_id)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"查询积分账户失败: user_id={user_id}, error={e}")
            raise

    def create_member_points(self, *, user_id: int, level_id: int) -> MemberPoint:
        """创建积分账户"""
        try:
            points = MemberPoint(user_id=user_id, level_id=level_id)
            self.db.add(points)
            self.db.flush()
            self.db.refresh(points)
            return points
        except IntegrityError as e:
            logger.error(f"创建积分账户失败，数据冲突: user_id={user_id}, error={e}")
            raise ValueError(f"用户 {user_id} 的积分账户已存在")
        except SQLAlchemyError as e:
            logger.error(f"创建积分账户失败: user_id={user_id}, error={e}")
            raise

    def get_transaction_by_reference(
        self,
        *,
        user_id: int,
        reference_id: Optional[str],
        transaction_type: str,
    ) -> Optional[PointTransaction]:
        """根据关联ID查询积分交易记录（幂等性检查）"""
        try:
            query = self.db.query(PointTransaction).filter(
                PointTransaction.user_id == user_id,
                PointTransaction.transaction_type == transaction_type,
            )
            if reference_id:
                query = query.filter(PointTransaction.reference_id == reference_id)
            return query.first()
        except SQLAlchemyError as e:
            logger.error(f"查询积分交易记录失败: user_id={user_id}, error={e}")
            raise

    def create_transaction(
        self,
        *,
        user_id: int,
        transaction_type: str,
        points_change: int,
        reference_id: Optional[str] = None,
        reference_type: Optional[str] = None,
        description: Optional[str] = None,
        status: str = "completed",
    ) -> PointTransaction:
        """创建积分交易记录"""
        try:
            transaction = PointTransaction(
                user_id=user_id,
                transaction_type=transaction_type,
                points_change=points_change,
                reference_id=reference_id,
                reference_type=reference_type,
                description=description,
                status=status,
            )
            self.db.add(transaction)
            self.db.flush()
            self.db.refresh(transaction)
            return transaction
        except IntegrityError as e:
            logger.error(f"创建积分交易记录失败，数据冲突: user_id={user_id}, error={e}")
            raise ValueError("积分交易记录重复")
        except SQLAlchemyError as e:
            logger.error(f"创建积分交易记录失败: user_id={user_id}, error={e}")
            raise

    def update_points_balance(
        self, points: MemberPoint, delta: int
    ) -> MemberPoint:
        """更新积分余额并维护累计统计"""
        try:
            new_balance = points.current_points + delta
            if new_balance < 0:
                raise ValueError("积分余额不足")

            points.current_points = new_balance
            if delta >= 0:
                points.total_earned += delta
            else:
                points.total_used += abs(delta)

            self.db.flush()
            self.db.refresh(points)
            return points
        except SQLAlchemyError as e:
            logger.error(f"更新积分余额失败: user_id={points.user_id}, error={e}")
            raise

    def get_transactions_by_user(
        self,
        user_id: int,
        *,
        transaction_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[PointTransaction]:
        """获取用户积分交易历史"""
        try:
            query = self.db.query(PointTransaction).filter(
                PointTransaction.user_id == user_id
            )
            if transaction_type:
                query = query.filter(PointTransaction.transaction_type == transaction_type)
            
            return (
                query.order_by(PointTransaction.created_at.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"查询积分交易历史失败: user_id={user_id}, error={e}")
            raise


class LevelRepository:
    """会员等级数据访问仓储"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_levels(self) -> List[MemberLevel]:
        """获取所有会员等级，按积分要求排序"""
        try:
            return (
                self.db.query(MemberLevel)
                .order_by(MemberLevel.min_points.asc())
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"查询会员等级列表失败: error={e}")
            raise

    def get_level_by_id(self, level_id: int) -> Optional[MemberLevel]:
        """根据等级ID查询等级信息"""
        try:
            return (
                self.db.query(MemberLevel)
                .filter(MemberLevel.id == level_id)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"查询会员等级失败: level_id={level_id}, error={e}")
            raise

    def get_initial_level(self) -> Optional[MemberLevel]:
        """获取初始会员等级（积分要求最低的等级）"""
        try:
            return (
                self.db.query(MemberLevel)
                .order_by(MemberLevel.min_points.asc())
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"查询初始会员等级失败: error={e}")
            raise

    def find_eligible_level_by_points(self, total_points: int) -> Optional[MemberLevel]:
        """根据总积分查找符合条件的最高等级"""
        try:
            return (
                self.db.query(MemberLevel)
                .filter(MemberLevel.min_points <= total_points)
                .order_by(MemberLevel.min_points.desc())
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"查询符合条件的会员等级失败: total_points={total_points}, error={e}")
            raise


class EventRepository:
    """会员系统事件外发数据访问仓储"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def enqueue_event(
        self, event: MemberDomainEvent, *, member_id: Optional[int] = None
    ) -> MemberEventOutbox:
        """将领域事件写入Outbox表以进行异步发送"""
        try:
            record = MemberEventOutbox(
                member_id=member_id,
                event_type=event.event_type,
                payload=event.payload,
                status="pending",
                available_at=event.available_at or datetime.utcnow(),
            )
            self.db.add(record)
            self.db.flush()
            return record
        except SQLAlchemyError as e:
            logger.error(f"写入事件失败: event_type={event.event_type}, error={e}")
            raise

    def fetch_pending_outbox(self, *, limit: int = 100) -> List[MemberEventOutbox]:
        """检索待发送且可用的Outbox事件列表"""
        try:
            return (
                self.db.query(MemberEventOutbox)
                .filter(
                    MemberEventOutbox.status == "pending",
                    MemberEventOutbox.available_at <= datetime.utcnow(),
                )
                .order_by(MemberEventOutbox.available_at.asc())
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"查询待发送事件失败: error={e}")
            raise

    def mark_outbox_sending(self, event: MemberEventOutbox) -> MemberEventOutbox:
        """标记事件正在发送"""
        event.status = "sending"
        event.last_error = None
        self.db.add(event)
        return event

    def mark_outbox_sent(
        self,
        event: MemberEventOutbox,
        *,
        delivered_at: Optional[datetime] = None,
    ) -> MemberEventOutbox:
        """标记事件已成功发送"""
        event.status = "sent"
        event.delivered_at = delivered_at or datetime.utcnow()
        event.last_error = None
        self.db.add(event)
        return event

    def mark_outbox_retry(
        self,
        event: MemberEventOutbox,
        *,
        error: str,
        max_retries: int = 5,
    ) -> MemberEventOutbox:
        """增加重试计数并决定失败事件的下一状态"""
        event.retry_count += 1
        event.last_error = error
        event.status = "failed" if event.retry_count >= max_retries else "pending"
        self.db.add(event)
        return event
