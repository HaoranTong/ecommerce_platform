"""
会员系统模块数据模型

✅ 文档驱动开发 - 严格遵循修正后的设计文档
✅ 架构规范遵循 - docs/standards/database-standards.md
✅ 主键统一标准 - 所有表主键使用 INTEGER (修正后)
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

class MembershipLevel(Base, TimestampMixin):
    """会员等级表 - 严格按照修正后的database-design.md实现"""
    __tablename__ = 'membership_levels'

    # 主键 - 严格遵循架构规范使用 INTEGER
    id = Column(Integer, primary_key=True, autoincrement=True, comment='等级ID')
    
    # 等级基础信息 - 完全按照设计文档字段定义
    level_name = Column(String(50), nullable=False, comment='等级名称')
    level_code = Column(String(20), nullable=False, comment='等级代码')
    required_spent = Column(DECIMAL(15, 2), nullable=False, default=0.00, comment='达到该等级所需累计消费')
    discount_rate = Column(DECIMAL(4, 3), nullable=False, default=1.000, comment='折扣率，0.9表示9折')
    point_multiplier = Column(DECIMAL(4, 2), nullable=False, default=1.00, comment='积分倍率')
    level_order = Column(Integer, nullable=False, comment='等级排序，数字越大等级越高')
    
    # 等级详情
    description = Column(Text, comment='等级描述')
    benefits = Column(JSON, comment='等级基础权益配置')
    
    # 状态控制
    is_active = Column(Boolean, nullable=False, default=True, comment='是否激活: 1=是, 0=否')

    # 索引定义 - 严格按照设计文档
    __table_args__ = (
        Index('idx_level_order', 'level_order'),
        Index('idx_required_spent', 'required_spent'),
    )

    def __repr__(self):
        return f"<MembershipLevel(id={self.id}, name='{self.level_name}')>"


class Member(Base, TimestampMixin):
    """会员基础信息表 - 严格按照修正后的database-design.md实现"""
    __tablename__ = 'members'

    # 主键 - 严格遵循架构规范使用 INTEGER (修正后的设计文档)
    id = Column(Integer, primary_key=True, autoincrement=True, comment='会员ID')
    
    # 会员标识
    member_code = Column(String(20), nullable=False, comment='会员编号，如M202409170001')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='关联用户ID')
    
    # 等级信息
    level_id = Column(Integer, ForeignKey('membership_levels.id'), nullable=False, default=1, comment='当前会员等级ID')
    
    # 消费和积分统计 - 按修正后文档使用 INTEGER
    total_spent = Column(DECIMAL(15, 2), nullable=False, default=0.00, comment='累计消费金额')
    total_points = Column(Integer, nullable=False, default=0, comment='历史累计获得积分')
    available_points = Column(Integer, nullable=False, default=0, comment='当前可用积分')
    frozen_points = Column(Integer, nullable=False, default=0, comment='冻结积分')
    
    # 会员信息
    join_date = Column(Date, nullable=False, default=func.current_date(), comment='入会日期')
    last_active_at = Column(DateTime, comment='最后活跃时间')
    birthday = Column(Date, comment='生日')
    preferences = Column(JSON, comment='偏好设置(通知、营销等)')
    
    # 状态控制
    status = Column(Integer, nullable=False, default=1, comment='状态: 1=正常, 2=冻结, 3=注销')

    # 索引定义 - 严格按照设计文档
    __table_args__ = (
        UniqueConstraint('member_code', name='uk_member_code'),
        UniqueConstraint('user_id', name='uk_user_id'),
        Index('idx_level_id', 'level_id'),
        Index('idx_total_spent', 'total_spent'),
        Index('idx_join_date', 'join_date'),
        Index('idx_status', 'status'),
        CheckConstraint('available_points >= 0', name='check_available_points_non_negative'),
        CheckConstraint('total_spent >= 0', name='check_total_spent_non_negative'),
    )

    # 关系定义
    level = relationship("MembershipLevel")

    @validates('member_code')
    def validate_member_code(self, key, member_code):
        """验证会员编号格式：M+年月日+序号"""
        if not member_code or not member_code.startswith('M') or len(member_code) != 13:
            raise ValueError("会员编号格式错误，应为M+年月日+4位序号")
        return member_code

    def __repr__(self):
        return f"<Member(id={self.id}, code='{self.member_code}')>"
