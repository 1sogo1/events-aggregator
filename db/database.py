from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv('DATABASE_URL')

engine = create_async_engine(str(DB_URL), echo=False)

Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with Session() as session:
        yield session