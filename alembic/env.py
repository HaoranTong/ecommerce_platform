from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Load .env file if it exists
from pathlib import Path
import sys

# Get the project root directory (parent of alembic directory)
alembic_dir = Path(__file__).resolve().parent
proj_root = alembic_dir.parent
env_file = proj_root / '.env'

if env_file.exists():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

# ensure project root is on sys.path so 'app' package can be imported
sys.path.insert(0, str(proj_root))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
try:
    # alembic.ini may include a [loggers]/[handlers]/[formatters] section
    # but some environments omit it; guard to avoid KeyError on missing sections.
    fileConfig(config.config_file_name)
except Exception:
    # fall back to default logging configuration
    import logging
    logging.basicConfig()

# import your models' MetaData object here
import app.data_models as models
target_metadata = models.Base.metadata

# set sqlalchemy.url from env if present
alembic_dsn = os.environ.get('ALEMBIC_DSN') or os.environ.get('DATABASE_URL')
if alembic_dsn:
    config.set_main_option('sqlalchemy.url', alembic_dsn)


def run_migrations_offline():
    url = config.get_main_option('sqlalchemy.url')
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
