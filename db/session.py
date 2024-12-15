
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from config import settings


DATABASE_URL = settings.get_sqlite_url()

engine = create_async_engine(url=DATABASE_URL)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
