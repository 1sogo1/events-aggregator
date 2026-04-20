from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from services.provider_client import EventsProviderClient
from services.sync_service import SyncService
import asyncio

router = APIRouter(prefix="/api/sync", tags=["sync"])

async def run_sync_in_background(db: AsyncSession):
    try:
        client = EventsProviderClient()
        sync_service = SyncService(db, client)
        await sync_service.sync()
        print("Background sync completed successfully")
    except Exception as e:
        print(f"Background sync error: {e}")

@router.post("/trigger")
async def trigger_sync(db: AsyncSession = Depends(get_db)):
    asyncio.create_task(run_sync_in_background(db))
    return {"status": "success", "message": "Sync started in background"}