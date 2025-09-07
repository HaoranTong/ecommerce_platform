"""One-off helper to create SQL tables from SQLAlchemy models in dev.
Usage: python scripts/create_tables.py
This calls Base.metadata.create_all(bind=engine).
"""
from app.db import engine, Base

if __name__ == '__main__':
    print('Creating tables using engine:', engine)
    Base.metadata.create_all(bind=engine)
    print('Tables created (if not existed).')
