"""
数据库连接配置
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 从环境变量读取数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:rootpass@localhost:3307/ecommerce_platform"
)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    echo=False,  # 设置为True可以看到SQL语句
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db():
    """获取数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """创建所有表"""
    # Import all model modules to register them with Base
    from app.modules.user_auth import models as user_models
    from app.modules.product_catalog import models as product_models
    # Import other modules as they are implemented
    
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """删除所有表（仅用于开发测试）"""
    # Import all model modules to register them with Base
    from app.modules.user_auth import models as user_models
    from app.modules.product_catalog import models as product_models
    # Import other modules as they are implemented
    
    Base.metadata.drop_all(bind=engine)
