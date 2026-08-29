import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

db_url = settings.DATABASE_URL.strip()

# Normalize postgres:// to postgresql+psycopg:// for SQLAlchemy 2.0 and Psycopg 3
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+psycopg"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

# Configure engine parameters depending on database dialect
engine_kwargs = {
    "echo": False,
}

if db_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Production PostgreSQL (Supabase Transaction Pooler / PgBouncer / Render)
    # CRITICAL: prepare_threshold=None disables Psycopg 3 prepared statements,
    # preventing "DuplicatePreparedStatement: prepared statement '_pg3_0' already exists"
    # when connecting through PgBouncer transaction-mode poolers (port 6543).
    engine_kwargs["connect_args"] = {
        "prepare_threshold": None,
    }
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(db_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
