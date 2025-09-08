from sqlalchemy import create_engine, text
import os
dsn = os.environ.get('ALEMBIC_DSN') or os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:rootpass@127.0.0.1:3307/dev_vision'
print("using DSN:", dsn)
e = create_engine(dsn)
with e.begin() as conn:
    conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)"))
    cnt = conn.execute(text("SELECT COUNT(*) AS c FROM alembic_version")).mappings().first()['c']
    if cnt == 0:
        conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('0002_product')"))
        print('inserted 0002_product into alembic_version')
    else:
        conn.execute(text("UPDATE alembic_version SET version_num = ''0002_product''"))
        print('updated alembic_version to 0002_product')
    print('alembic_version now:', conn.execute(text("SELECT * FROM alembic_version")).mappings().all())
