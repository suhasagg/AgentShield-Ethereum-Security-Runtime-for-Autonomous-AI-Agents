from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .config import settings
from .models import Base

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
Session = async_sessionmaker(engine, expire_on_commit=False)

async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
