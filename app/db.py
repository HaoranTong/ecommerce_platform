from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('ALEMBIC_DSN') or 'mysql+pymysql://root:rootpass@localhost:3307/dev_vision'

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_session():
    """Yield a SQLAlchemy session (context manager style)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Re-export Base from models for tests and alembic usage
from app.models import Base  # noqa: E402
