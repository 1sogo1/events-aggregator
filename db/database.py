from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("POSTGRES_CONNECTION_STRING") or os.getenv("DATABASE_URL")

if not DB_URL:
    raise Exception("No database connection string found!")

if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DB_URL.startswith("postgresql://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

print(f"DB_URL type: {DB_URL[:30]}...")

engine = create_async_engine(DB_URL, echo=False)
Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with Session() as session:
        yield session