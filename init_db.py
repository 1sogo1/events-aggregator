import asyncio
from db.database import engine
from db.models import Base

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Tables recreated!")

if __name__ == "__main__":
    asyncio.run(init())