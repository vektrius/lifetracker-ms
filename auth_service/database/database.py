from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from core.settings import settings


def create_engine_and_session(url: str):
    engine = create_async_engine(url, echo=True, future=True, pool_pre_ping=True)
    db_session = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return engine, db_session


DATABASE_URL = f'mysql+asyncmy://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.MYSQL_DATABASE}'
async_engine, async_db_session = create_engine_and_session(DATABASE_URL)

def get_session() -> AsyncSession:
    return async_db_session()
