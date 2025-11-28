"""
FastAPI Database Connection and Session Management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import sys
import logging

# Add parent directory to path to import existing models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import Base, Event, Alert, AuditLog

# Database configuration from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:securepass123@localhost:5432/cyber_fraud_platform")

# SQLAlchemy setup with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db() -> Session:
    """
    FastAPI dependency to get database session.
    Automatically handles session cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """
    Context manager for database sessions.
    Use for non-FastAPI contexts.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def test_db_connection() -> bool:
    """
    Test database connectivity.
    Returns True if connection successful, False otherwise.
    """
    try:
        with get_db_session() as db:
            # Simple query to test connection
            db.execute("SELECT 1")
            logger.info("Database connection successful")
            return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database test: {e}")
        return False


def init_db():
    """
    Create database tables if they don't exist.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise