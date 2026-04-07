from sqlalchemy import create_engine as createEngine
from sqlalchemy.orm import declarative_base as declarativeBase, sessionmaker
from dotenv import load_dotenv as loadDotenv
import os

loadDotenv()

databaseUrl = os.getenv("DATABASE_URL")
if not databaseUrl:
    raise ValueError("DATABASE_URL is not set in .env")

engine = createEngine(databaseUrl)

sessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

base = declarativeBase()

def getDb():
    dbSession = sessionLocal()
    try:
        yield dbSession
    except Exception:
        dbSession.rollback()
        raise
    finally:
        dbSession.close()