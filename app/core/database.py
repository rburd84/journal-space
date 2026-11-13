import os

from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.database_url import normalize_database_url

DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./journal.db"))

connect_args = {"check_same_thread": False} if make_url(DATABASE_URL).get_backend_name() == "sqlite" else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

if engine.dialect.name == "sqlite":
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
