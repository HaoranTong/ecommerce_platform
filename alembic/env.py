import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 导入所有模型以确保metadata包含所有表定义
from app.core.database import Base

# 导入所有模块的模型
from app.modules.user_auth.models import User, Role, Permission, UserRole, RolePermission, Session  # 用户认证模型
from app.modules.product_catalog.models import (
    Category, Product, Brand, SKU, ProductAttribute, ProductImage, ProductTag, SKUAttribute
)  # 产品目录模型
from app.modules.inventory_management.models import (
    InventoryStock, InventoryReservation, InventoryTransaction
)  # 库存管理模型
from app.modules.order_management.models import (
    Order, OrderItem, OrderStatusHistory
)  # 订单管理模型
from app.modules.member_system.models import (
    MembershipLevel, Member, MembershipBenefit, PointTransaction, 
    MemberActivity, ActivityParticipation, BenefitUsage, SystemConfig
)  # 会员系统模型

# 设置target_metadata为Base的metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # 优先使用环境变量中的数据库URL
    url = os.getenv("ALEMBIC_DSN") or os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # 获取配置section
    configuration = config.get_section(config.config_ini_section, {})
    
    # 如果环境变量中有数据库URL，使用环境变量覆盖配置文件
    database_url = os.getenv("ALEMBIC_DSN") or os.getenv("DATABASE_URL")
    if database_url:
        configuration["sqlalchemy.url"] = database_url
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
