"""
VELOX-N8N Database Configuration
Database connection and session management
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from typing import Generator

from app.core.config import db_settings

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    db_settings.URL,
    poolclass=StaticPool,
    pool_size=db_settings.POOL_SIZE,
    max_overflow=db_settings.MAX_OVERFLOW,
    pool_timeout=db_settings.POOL_TIMEOUT,
    pool_recycle=db_settings.POOL_RECYCLE,
    echo=db_settings.ECHO,
    future=True
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

# Create base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def get_async_db() -> Generator[Session, None, None]:
    """
    Async dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Async database session error: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()


def create_tables():
    """
    Create all database tables
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """
    Drop all database tables (use with caution)
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


def check_db_connection():
    """
    Check database connection health
    """
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            if result:
                logger.info("Database connection check: OK")
                return True
            else:
                logger.error("Database connection check: FAILED")
                return False
    except Exception as e:
        logger.error(f"Database connection check error: {e}")
        return False


async def check_async_db_connection():
    """
    Check async database connection health
    """
    try:
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            if result:
                logger.info("Async database connection check: OK")
                return True
            else:
                logger.error("Async database connection check: FAILED")
                return False
    except Exception as e:
        logger.error(f"Async database connection check error: {e}")
        return False


def get_db_info():
    """
    Get database information
    """
    try:
        with engine.connect() as connection:
            # Get PostgreSQL version
            version_result = connection.execute("SELECT version()")
            version = version_result.fetchone()[0] if version_result else "Unknown"
            
            # Get database size
            size_result = connection.execute(
                "SELECT pg_size_pretty(pg_database(current_database()))"
            )
            size = size_result.fetchone()[0] if size_result else "Unknown"
            
            # Get connection count
            conn_result = connection.execute(
                "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
            )
            connections = conn_result.fetchone()[0] if conn_result else 0
            
            return {
                "version": version,
                "size": size,
                "active_connections": connections,
                "pool_size": db_settings.POOL_SIZE,
                "max_overflow": db_settings.MAX_OVERFLOW
            }
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {
            "version": "Unknown",
            "size": "Unknown",
            "active_connections": 0,
            "pool_size": db_settings.POOL_SIZE,
            "max_overflow": db_settings.MAX_OVERFLOW
        }


async def close_db_connections():
    """
    Close all database connections
    """
    try:
        await engine.dispose()
        logger.info("All database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


# Database health check for monitoring
async def db_health_check():
    """
    Comprehensive database health check
    """
    health_info = {
        "status": "healthy",
        "timestamp": None,
        "details": {}
    }
    
    try:
        # Basic connection test
        connection_ok = await check_async_db_connection()
        health_info["details"]["connection"] = "ok" if connection_ok else "failed"
        
        # Get database info
        db_info = get_db_info()
        health_info["details"]["info"] = db_info
        
        # Check if we can query a table
        async with engine.begin() as conn:
            await conn.execute("SELECT COUNT(*) FROM information_schema.tables")
            health_info["details"]["query_test"] = "ok"
        
        # Set overall status
        if connection_ok:
            health_info["status"] = "healthy"
        else:
            health_info["status"] = "unhealthy"
            
    except Exception as e:
        logger.error(f"Database health check error: {e}")
        health_info["status"] = "unhealthy"
        health_info["details"]["error"] = str(e)
    
    import time
    health_info["timestamp"] = time.time()
    
    return health_info


# Database initialization for startup
async def init_database():
    """
    Initialize database on application startup
    """
    try:
        # Check connection
        if not await check_async_db_connection():
            logger.error("Cannot connect to database")
            return False
        
        # Create tables if they don't exist
        create_tables()
        
        # Run any migrations
        # TODO: Add Alembic migration support
        
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


# Database cleanup for shutdown
async def cleanup_database():
    """
    Cleanup database connections on application shutdown
    """
    try:
        await close_db_connections()
        logger.info("Database cleanup completed")
    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")