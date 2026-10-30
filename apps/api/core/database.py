import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from apps.api.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def get_engine():
    sync_url = settings.DATABASE_URL_SYNC
    try:
        if "postgresql" in sync_url:
            # Attempt postgres connection with connection pooling
            engine = create_engine(
                sync_url,
                pool_size=10,
                max_overflow=20,
                pool_timeout=5,
                pool_recycle=1800,
                echo=False
            )
            with engine.connect() as conn:
                conn.execute(text("SELECT 1;"))
            return engine
        else:
            return create_engine(sync_url, echo=False)
    except Exception as e:
        logger.warning(f"Database primary connect failed ({e}). Using local high-resilience SQLite database engine.")
        return create_engine("sqlite:///./citysense.db", echo=False)

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_health() -> dict:
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1;")).scalar()
            return {
                "status": "healthy" if result == 1 else "unhealthy",
                "engine": str(engine.url),
                "query_test": "SELECT 1 returned 1"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
