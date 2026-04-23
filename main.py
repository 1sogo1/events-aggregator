from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from routers import health, events, sync, tickets
from db.database import Session
from config import settings
from services.provider_client import EventsProviderClient
from usecases.sync_usecase import SyncUsecase

async def sync_scheduler():
    while True:
        try:
            await asyncio.sleep(24 * 60 * 60) 
            
            async with Session() as db:
                client = EventsProviderClient(settings.PROVIDER_BASE_URL, settings.PROVIDER_API_KEY)
                usecase = SyncUsecase(db, client)
                await usecase.execute()
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
app.include_router(tickets.router)

@app.get("/")
async def root():
    return {"message": "Events Aggregator running"}