from fastapi import APIRouter
from db.database import Session as AsyncSessionLocal
from services.provider_client import EventsProviderClient
from services.sync_service import SyncService
import asyncio

router = APIRouter(prefix="/api/sync", tags=["sync"])

async def run_sync_in_background():
    async with AsyncSessionLocal() as db:
        try:
            client = EventsProviderClient()
            sync_service = SyncService(db, client)
            await sync_service.sync()
            print("Background sync completed successfully")
        except Exception as e:
            print(f"Background sync error: {e}")

@router.post("/trigger")
async def trigger_sync():
    asyncio.create_task(run_sync_in_background())
    return {"status": "success", "message": "Sync started in background"}