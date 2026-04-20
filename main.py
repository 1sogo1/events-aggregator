from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from routers import health, events, sync

async def sync_scheduler():
    while True:
        try:
            await asyncio.sleep(60)
            
            from db.database import Session
            from services.provider_client import EventsProviderClient
            from services.sync_service import SyncService
            
            async with Session() as db:
                client = EventsProviderClient()
                sync_service = SyncService(db, client)
                await sync_service.sync()
                print("Auto-sync completed successfully")
        except Exception as e:
            print(f"Auto-sync error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting background sync scheduler...")
    task = asyncio.create_task(sync_scheduler())
    yield
    print("Shutting down...")
    task.cancel()

app = FastAPI(title="Events Aggregator", lifespan=lifespan)


app.include_router(health.router)
app.include_router(events.router)
app.include_router(sync.router)

@app.get("/")
async def root():
    return {"message": "Events Aggregator running"}