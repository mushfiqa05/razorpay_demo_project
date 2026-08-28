from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# SQLite requires check_same_thread=False; PostgreSQL does not require connect_args.
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create SQLAlchemy Database Engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False  # Set to True if you want to inspect raw SQL queries in console
)

# Session factory for DB operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

def get_db():
    """
    Dependency generator for database sessions in FastAPI routes.
    Ensures database connection is cleanly opened and closed per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
