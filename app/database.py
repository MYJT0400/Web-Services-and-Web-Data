from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite file used by the local demo.
DATABASE_URL = "sqlite:///./books.db"

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
