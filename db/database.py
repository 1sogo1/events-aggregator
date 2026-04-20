from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()



DB_URL = os.getenv('POSTGRES_CONNECTION_STRING')

engine = create_async_engine(str(DB_URL), echo=False)

Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

print(f"POSTGRES_CONNECTION_STRING: {os.getenv('POSTGRES_CONNECTION_STRING', 'NOT SET')}")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')}")

async def get_db():
    async with Session() as session:
        yield session

    