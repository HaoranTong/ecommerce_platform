"""
会员系统模块数据模型

✅ 文档驱动开发 - 严格遵循原计划和设计规范
✅ 架构规范遵循 - docs/standards/database-standards.md
✅ 命名规范遵循 - 表名使用复数形式，严格按照原计划
✅ 主键统一标准 - 所有表主键使用 INTEGER
"""

from datetime import datetime, date
from enum import Enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, Text, JSON
from sqlalchemy import ForeignKey, Index, UniqueConstraint, CheckConstraint, DECIMAL, func
from sqlalchemy.orm import relationship, validates

# 严格遵循规范 - 从技术基础设施层导入
from app.core.database import Base
from app.shared.base_models import TimestampMixin


# ================== 枚举定义 ==================

class MemberStatus(Enum):
    """会员状态枚举 - 对应数据库status字段"""
    ACTIVE = 1      # 正常
    FROZEN = 2      # 冻结  
    CANCELLED = 3   # 注销


# ================== 核心数据模型 ==================

class MemberLevel(Base, TimestampMixin):
    """会员等级表 - 严格按照原计划和database-standards.md实现"""
    __tablename__ = 'member_levels'

    # 主键 - 严格遵循架构规范使用 INTEGER
    id = Column(Integer, primary_key=True, autoincrement=True, comment='等级ID')
    
    # 等级基础信息 - 完全按照原计划字段定义
    level_name = Column(String(50), nullable=False, comment='等级名称')
    min_points = Column(Integer, nullable=False, default=0, comment='达到该等级所需最少积分')
    discount_rate = Column(DECIMAL(4, 3), nullable=False, default=1.000, comment='折扣率，0.9表示9折')
    benefits = Column(JSON, comment='等级权益配置JSON格式')
    
    # 索引定义 - 严格按照database-standards.md规范
    __table_args__ = (
        UniqueConstraint('level_name', name='uk_member_levels_level_name'),
        Index('idx_member_levels_min_points', 'min_points'),
    )

    def __repr__(self):
        return f"<MemberLevel(id={self.id}, name='{self.level_name}')>"


class PointTransaction(Base, TimestampMixin):
    """积分变动记录表 - 严格按照原计划和database-standards.md实现"""
    __tablename__ = 'point_transactions'

    # 主键 - 严格遵循架构规范使用 INTEGER
    id = Column(Integer, primary_key=True, autoincrement=True, comment='交易记录ID')
    
    # 关联关系
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    
    # 交易信息 - 严格按照原计划字段设计
    transaction_type = Column(String(50), nullable=False, comment='交易类型：earn/use/expire/freeze/unfreeze')
    points_change = Column(Integer, nullable=False, comment='积分变动数量（正数为获得，负数为消费）')
    reference_id = Column(String(100), comment='关联业务ID（订单ID、活动ID等）')
    reference_type = Column(String(50), comment='关联业务类型（order/activity/manual等）')
    description = Column(String(500), comment='变动说明')
    
    # 交易状态
    status = Column(String(20), nullable=False, default='completed', comment='交易状态：pending/completed/cancelled')
    
    # 索引定义 - 严格按照database-standards.md规范
    __table_args__ = (
        Index('idx_point_transactions_user_id', 'user_id'),
        Index('idx_point_transactions_transaction_type', 'transaction_type'),
        Index('idx_point_transactions_reference_id', 'reference_id'),
        Index('idx_point_transactions_reference_type', 'reference_type'),
        Index('idx_point_transactions_created_at', 'created_at'),
        Index('fk_point_transactions_user_id', 'user_id'),
    )

    def __repr__(self):
        return f"<PointTransaction(id={self.id}, user_id={self.user_id}, type='{self.transaction_type}', points={self.points_change})"


class MemberProfile(Base, TimestampMixin):
    """会员档案表 - 严格按照原计划，但使用profiles以区分业务含义"""
    __tablename__ = 'member_profiles'

    # 主键 - 严格遵循架构规范使用 INTEGER
    id = Column(Integer, primary_key=True, autoincrement=True, comment='会员ID')
    
    # 会员标识
    member_code = Column(String(20), nullable=False, comment='会员编号，如M202409170001')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='关联用户ID')
    
    # 等级信息
    level_id = Column(Integer, ForeignKey('member_levels.id'), nullable=False, default=1, comment='当前会员等级ID')
    
    # 消费统计
    total_spent = Column(DECIMAL(15, 2), nullable=False, default=0.00, comment='累计消费金额')
    
    # 会员信息
    join_date = Column(Date, nullable=False, default=func.current_date(), comment='入会日期')
    last_active_at = Column(DateTime, comment='最后活跃时间')
    birthday = Column(Date, comment='生日')
    preferences = Column(JSON, comment='偏好设置(通知、营销等)')
    
    # 状态控制
    status = Column(Integer, nullable=False, default=1, comment='状态: 1=正常, 2=冻结, 3=注销')

    # 索引定义 - 严格按照database-standards.md规范
    __table_args__ = (
        UniqueConstraint('member_code', name='uk_member_profiles_member_code'),
        UniqueConstraint('user_id', name='uk_member_profiles_user_id'),
        Index('idx_member_profiles_level_id', 'level_id'),
        Index('idx_member_profiles_total_spent', 'total_spent'),
        Index('idx_member_profiles_join_date', 'join_date'),
        Index('idx_member_profiles_status', 'status'),
        Index('fk_member_profiles_user_id', 'user_id'),
        Index('fk_member_profiles_level_id', 'level_id'),
        CheckConstraint('total_spent >= 0', name='check_total_spent_non_negative'),
    )

    # 关系定义
    level = relationship("MemberLevel")

    @validates('member_code')
    def validate_member_code(self, key, member_code):
        """验证会员编号格式：M+年月日+序号"""
        if not member_code or not member_code.startswith('M') or len(member_code) != 13:
            raise ValueError("会员编号格式错误，应为M+年月日+4位序号")
        return member_code

    def __repr__(self):
        return f"<MemberProfile(id={self.id}, code='{self.member_code}')>"


class MemberPoint(Base, TimestampMixin):
    """会员积分表 - 严格按照原计划和database-standards.md实现"""
    __tablename__ = 'member_points'

    # 主键 - 严格遵循架构规范使用 INTEGER
    id = Column(Integer, primary_key=True, autoincrement=True, comment='积分记录ID')
    
    # 关联关系
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    level_id = Column(Integer, ForeignKey('member_levels.id'), nullable=False, comment='会员等级ID')
    
    # 积分统计 - 严格按照原计划字段设计
    current_points = Column(Integer, nullable=False, default=0, comment='当前可用积分')
    total_earned = Column(Integer, nullable=False, default=0, comment='历史累计获得积分')
    total_used = Column(Integer, nullable=False, default=0, comment='历史累计使用积分')

    # 索引定义 - 严格按照database-standards.md规范
    __table_args__ = (
        UniqueConstraint('user_id', name='uk_member_points_user_id'),
        Index('idx_member_points_level_id', 'level_id'),
        Index('idx_member_points_current_points', 'current_points'),
        Index('fk_member_points_user_id', 'user_id'),
        Index('fk_member_points_level_id', 'level_id'),
        CheckConstraint('current_points >= 0', name='check_current_points_non_negative'),
        CheckConstraint('total_earned >= 0', name='check_total_earned_non_negative'),
        CheckConstraint('total_used >= 0', name='check_total_used_non_negative'),
    )

    # 关系定义
    level = relationship("MemberLevel")

    def __repr__(self):
        return f"<MemberPoint(id={self.id}, user_id={self.user_id}, current={self.current_points})"
