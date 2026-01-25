"""
member_system 仓储层测试

遵循 testing-standards.md，聚焦仓储接口的核心行为校验。
"""

from __future__ import annotations

import random
from datetime import date, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.modules.member_system.models import (
    MemberEventOutbox,
    MemberLevel,
    MemberPoint,
    MemberProfile,
    PointTransaction,
)
from app.modules.member_system.repository import (
    EventRepository,
    LevelRepository,
    MemberDomainEvent,
    MemberRepository,
    PointRepository,
)
from tests.factories.member_system_factories import (
    MemberLevelFactory,
    MemberPointFactory,
    MemberProfileFactory,
    MemberSystemFactoryManager,
    PointTransactionFactory,
)
from tests.factories.user_auth_factories import (
    UserAuthFactoryManager,
    UserFactory,
)


def _generate_member_code() -> str:
    """生成符合格式的会员编号 MYYYYMMDDNNNN。"""
    return f"M{datetime.utcnow().strftime('%Y%m%d')}{random.randint(0, 9999):04d}"


def _prepare_user_and_level(db: Session):
    """创建仓储测试所需的用户和会员等级。"""
    UserAuthFactoryManager.setup_factories(db)
    MemberSystemFactoryManager.setup_factories(db)
    user = UserFactory.create()
    level = MemberLevelFactory.create()
    return user, level


@pytest.mark.unit
@pytest.mark.repositories
class TestMemberRepository:
    def test_get_profile_by_user_id_found(self, unit_test_db: Session) -> None:
        user, level = _prepare_user_and_level(unit_test_db)
        profile = MemberProfileFactory.create(user_id=user.id, level=level)

        result = MemberRepository(unit_test_db).get_profile_by_user_id(user.id)

        assert result is not None
        assert result.id == profile.id
        assert result.level.id == level.id

    def test_get_profile_by_user_id_not_found(self, unit_test_db: Session) -> None:
        assert MemberRepository(unit_test_db).get_profile_by_user_id(999999) is None

    def test_get_profile_by_id_found(self, unit_test_db: Session) -> None:
        user, level = _prepare_user_and_level(unit_test_db)
        profile = MemberProfileFactory.create(user_id=user.id, level=level)

        result = MemberRepository(unit_test_db).get_profile_by_id(profile.id)

        assert result is not None
        assert result.member_code == profile.member_code

    def test_get_profile_by_id_not_found(self, unit_test_db: Session) -> None:
        assert MemberRepository(unit_test_db).get_profile_by_id(999999) is None

    def test_create_profile_minimal_fields(self, unit_test_db: Session) -> None:
        user, level = _prepare_user_and_level(unit_test_db)
        member_code = _generate_member_code()
        join_date = date.today()

        result = MemberRepository(unit_test_db).create_profile(
            user_id=user.id,
            member_code=member_code,
            level_id=level.id,
            join_date=join_date,
        )

        assert result.id is not None
        assert result.member_code == member_code
        assert result.join_date == join_date
        assert result.preferences == {}

        persisted = unit_test_db.query(MemberProfile).filter_by(id=result.id).one()
        assert persisted.total_spent == 0

    def test_create_profile_full_fields(self, unit_test_db: Session) -> None:
        user, level = _prepare_user_and_level(unit_test_db)
        member_code = _generate_member_code()
        birthday = date(1995, 1, 1)
        preferences = {"newsletter": True, "language": "zh-CN"}

        result = MemberRepository(unit_test_db).create_profile(
            user_id=user.id,
            member_code=member_code,
            level_id=level.id,
            join_date=date.today(),
            birthday=birthday,
            preferences=preferences,
        )

        assert result.birthday == birthday
        assert result.preferences == preferences

    def test_create_profile_transaction_commit(self, unit_test_db: Session) -> None:
        user, level = _prepare_user_and_level(unit_test_db)
        result = MemberRepository(unit_test_db).create_profile(
            user_id=user.id,
            member_code=_generate_member_code(),
            level_id=level.id,
            join_date=date.today(),
        )

        unit_test_db.expire_all()
        assert (
            unit_test_db.query(MemberProfile)
            .filter(MemberProfile.id == result.id)
            .one()
        )


@pytest.mark.unit
@pytest.mark.repositories
class TestPointRepository:
    def test_get_member_points_found(self, unit_test_db: Session) -> None:
        user, level = _prepare_user_and_level(unit_test_db)
        MemberPointFactory.create(user_id=user.id, level=level)

        result = PointRepository(unit_test_db).get_member_points(user.id)

        assert result is not None
        assert result.user_id == user.id

    def test_get_member_points_not_found(self, unit_test_db: Session) -> None:
        assert PointRepository(unit_test_db).get_member_points(999999) is None

    def test_create_member_points_success(self, unit_test_db: Session) -> None:
        user, level = _prepare_user_and_level(unit_test_db)

        result = PointRepository(unit_test_db).create_member_points(
            user_id=user.id,
            level_id=level.id,
        )

        assert result.id is not None
        assert result.current_points == 0

        stored = (
            unit_test_db.query(MemberPoint)
            .filter(MemberPoint.user_id == user.id)
            .one()
        )
        assert stored.level_id == level.id

    def test_create_member_points_duplicate(self, unit_test_db: Session) -> None:
        user, level = _prepare_user_and_level(unit_test_db)
        PointRepository(unit_test_db).create_member_points(
            user_id=user.id,
            level_id=level.id,
        )

        with pytest.raises(ValueError):
            PointRepository(unit_test_db).create_member_points(
                user_id=user.id,
                level_id=level.id,
            )

    def test_get_transaction_by_reference_found(self, unit_test_db: Session) -> None:
        user, _ = _prepare_user_and_level(unit_test_db)
        reference_id = "ref-transaction-001"
        transaction = PointTransaction(
            user_id=user.id,
            transaction_type="earn",
            points_change=50,
            reference_id=reference_id,
            status="completed",
        )
        unit_test_db.add(transaction)
        unit_test_db.commit()

        result = PointRepository(unit_test_db).get_transaction_by_reference(
            user_id=user.id,
            reference_id=reference_id,
            transaction_type="earn",
        )

        assert result is not None
        assert result.id == transaction.id

    def test_get_transaction_by_reference_not_found(self, unit_test_db: Session) -> None:
        result = PointRepository(unit_test_db).get_transaction_by_reference(
            user_id=999999,
            reference_id="missing",
            transaction_type="earn",
        )

        assert result is None

    def test_create_transaction_minimal_fields(self, unit_test_db: Session) -> None:
        user, _ = _prepare_user_and_level(unit_test_db)

        result = PointRepository(unit_test_db).create_transaction(
            user_id=user.id,
            transaction_type="earn",
            points_change=25,
        )

        assert result.id is not None
        assert result.points_change == 25

        stored = (
            unit_test_db.query(PointTransaction)
            .filter(PointTransaction.id == result.id)
            .one()
        )
        assert stored.status == "completed"

    def test_create_transaction_full_fields(self, unit_test_db: Session) -> None:
        user, _ = _prepare_user_and_level(unit_test_db)

        description = "order reward"
        result = PointRepository(unit_test_db).create_transaction(
            user_id=user.id,
            transaction_type="earn",
            points_change=100,
            reference_id="order-1001",
            reference_type="order",
            description=description,
            status="pending",
        )

        assert result.description == description
        assert result.status == "pending"

    def test_create_transaction_transaction_commit(self, unit_test_db: Session) -> None:
        user, _ = _prepare_user_and_level(unit_test_db)

        result = PointRepository(unit_test_db).create_transaction(
            user_id=user.id,
            transaction_type="earn",
            points_change=30,
        )

        unit_test_db.expire_all()
        assert (
            unit_test_db.query(PointTransaction)
            .filter(PointTransaction.id == result.id)
            .one()
        )

    def test_get_transactions_by_user_found(self, unit_test_db: Session) -> None:
        user, _ = _prepare_user_and_level(unit_test_db)
        PointTransactionFactory._meta.sqlalchemy_session = unit_test_db
        PointTransactionFactory.create(user_id=user.id, transaction_type="earn")
        PointTransactionFactory.create(user_id=user.id, transaction_type="use")

        results = PointRepository(unit_test_db).get_transactions_by_user(user.id)

        assert isinstance(results, list)
        assert {t.transaction_type for t in results} >= {"earn", "use"}

    def test_get_transactions_by_user_filtered(self, unit_test_db: Session) -> None:
        user, _ = _prepare_user_and_level(unit_test_db)
        PointTransactionFactory._meta.sqlalchemy_session = unit_test_db
        PointTransactionFactory.create(user_id=user.id, transaction_type="earn")
        PointTransactionFactory.create(user_id=user.id, transaction_type="use")

        results = PointRepository(unit_test_db).get_transactions_by_user(
            user.id,
            transaction_type="earn",
        )

        assert all(t.transaction_type == "earn" for t in results)

    def test_get_transactions_by_user_not_found(self, unit_test_db: Session) -> None:
        results = PointRepository(unit_test_db).get_transactions_by_user(999999)
        assert results == []


@pytest.mark.unit
@pytest.mark.repositories
class TestLevelRepository:
    def test_list_levels_sorted(self, unit_test_db: Session) -> None:
        fast = MemberLevel(level_name="Fast", min_points=50, discount_rate=1)
        slow = MemberLevel(level_name="Slow", min_points=10, discount_rate=1)
        unit_test_db.add_all([fast, slow])
        unit_test_db.commit()

        results = LevelRepository(unit_test_db).list_levels()

        assert len(results) == 2
        assert results[0].min_points == 10

    def test_get_level_by_id_found(self, unit_test_db: Session) -> None:
        level = MemberLevel(level_name="Gold", min_points=200, discount_rate=1)
        unit_test_db.add(level)
        unit_test_db.commit()

        result = LevelRepository(unit_test_db).get_level_by_id(level.id)

        assert result is not None
        assert result.level_name == "Gold"

    def test_get_level_by_id_not_found(self, unit_test_db: Session) -> None:
        assert LevelRepository(unit_test_db).get_level_by_id(999999) is None

    def test_get_initial_level_found(self, unit_test_db: Session) -> None:
        MemberLevelFactory._meta.sqlalchemy_session = unit_test_db
        low = MemberLevelFactory.create(min_points=0)
        MemberLevelFactory.create(min_points=500)

        result = LevelRepository(unit_test_db).get_initial_level()

        assert result.id == low.id

    def test_get_initial_level_not_found(self, unit_test_db: Session) -> None:
        assert LevelRepository(unit_test_db).get_initial_level() is None

    def test_find_eligible_level_by_points_found(self, unit_test_db: Session) -> None:
        MemberLevelFactory._meta.sqlalchemy_session = unit_test_db
        MemberLevelFactory.create(min_points=0)
        high = MemberLevelFactory.create(min_points=300)

        result = LevelRepository(unit_test_db).find_eligible_level_by_points(350)

        assert result.id == high.id

    def test_find_eligible_level_by_points_not_found(self, unit_test_db: Session) -> None:
        assert (
            LevelRepository(unit_test_db).find_eligible_level_by_points(100)
            is None
        )


@pytest.mark.unit
@pytest.mark.repositories
class TestEventRepository:
    def test_enqueue_event_minimal_fields(self, unit_test_db: Session) -> None:
        repo = EventRepository(unit_test_db)
        event = MemberDomainEvent(event_type="member.created", payload={"id": 1})

        result = repo.enqueue_event(event)

        assert result.id is not None
        assert result.status == "pending"

        stored = (
            unit_test_db.query(MemberEventOutbox)
            .filter(MemberEventOutbox.id == result.id)
            .one()
        )
        assert stored.payload == {"id": 1}

    def test_enqueue_event_full_fields(self, unit_test_db: Session) -> None:
        repo = EventRepository(unit_test_db)
        future = datetime.utcnow() + timedelta(minutes=5)
        event = MemberDomainEvent(
            event_type="member.updated",
            payload={"id": 2},
            available_at=future,
        )

        user, level = _prepare_user_and_level(unit_test_db)
        profile = MemberProfileFactory.create(user_id=user.id, level=level)

        result = repo.enqueue_event(event, member_id=profile.id)

        assert result.member_id == profile.id
        assert result.available_at == future

    def test_fetch_pending_outbox_found(self, unit_test_db: Session) -> None:
        repo = EventRepository(unit_test_db)
        repo.enqueue_event(
            MemberDomainEvent(
                event_type="member.created",
                payload={"id": 3},
                available_at=datetime.utcnow() - timedelta(minutes=1),
            )
        )

        results = repo.fetch_pending_outbox(limit=10)

        assert len(results) == 1
        assert results[0].status == "pending"

    def test_fetch_pending_outbox_not_found(self, unit_test_db: Session) -> None:
        results = EventRepository(unit_test_db).fetch_pending_outbox(limit=5)
        assert results == []

    def test_mark_outbox_sending(self, unit_test_db: Session) -> None:
        repo = EventRepository(unit_test_db)
        event = repo.enqueue_event(
            MemberDomainEvent(event_type="member.created", payload={"id": 4})
        )

        updated = repo.mark_outbox_sending(event)
        unit_test_db.flush()

        assert updated.status == "sending"
        unit_test_db.expire_all()
        stored = (
            unit_test_db.query(MemberEventOutbox)
            .filter(MemberEventOutbox.id == event.id)
            .one()
        )
        assert stored.status == "sending"

    def test_mark_outbox_sent(self, unit_test_db: Session) -> None:
        repo = EventRepository(unit_test_db)
        event = repo.enqueue_event(
            MemberDomainEvent(event_type="member.created", payload={"id": 5})
        )

        updated = repo.mark_outbox_sent(event, delivered_at=datetime.utcnow())
        unit_test_db.flush()

        assert updated.status == "sent"
        unit_test_db.expire_all()
        stored = (
            unit_test_db.query(MemberEventOutbox)
            .filter(MemberEventOutbox.id == event.id)
            .one()
        )
        assert stored.status == "sent"
        assert stored.delivered_at is not None

    def test_mark_outbox_retry(self, unit_test_db: Session) -> None:
        repo = EventRepository(unit_test_db)
        event = repo.enqueue_event(
            MemberDomainEvent(event_type="member.created", payload={"id": 6})
        )

        updated = repo.mark_outbox_retry(event, error="temporary failure")
        unit_test_db.flush()

        assert updated.retry_count == 1
        assert updated.status == "pending"
        assert updated.last_error == "temporary failure"

    def test_mark_outbox_retry_max_retries(self, unit_test_db: Session) -> None:
        repo = EventRepository(unit_test_db)
        event = repo.enqueue_event(
            MemberDomainEvent(event_type="member.created", payload={"id": 7})
        )
        event.retry_count = 4
        unit_test_db.flush()

        repo.mark_outbox_retry(event, error="retry fail", max_retries=5)
        unit_test_db.flush()

        assert event.status == "failed"
        assert event.retry_count == 5
        assert event.last_error == "retry fail"

