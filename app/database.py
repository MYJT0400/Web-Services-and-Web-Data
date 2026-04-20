from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "books.db"

# SQLite file used by the local demo and deployment.
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    # Required for SQLite when connections are shared across threads.
    connect_args={"check_same_thread": False},
)
# Session factory used by FastAPI dependency injection.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    # Yield one DB session per request and always close it afterwards.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
