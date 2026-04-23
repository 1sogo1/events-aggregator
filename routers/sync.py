from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from config import settings
from services.provider_client import EventsProviderClient
from usecases.sync_usecase import SyncUsecase
import asyncio

router = APIRouter(prefix="/api/sync", tags=["sync"])

def get_provider_client():
    return EventsProviderClient(settings.PROVIDER_BASE_URL, settings.PROVIDER_API_KEY)

async def run_sync_in_background(db: AsyncSession):
    try:
        client = get_provider_client()
        usecase = SyncUsecase(db, client)
        count = await usecase.execute()
        print(f"Background sync completed: {count} events saved")
    except Exception as e:
        print(f"Background sync error: {e}")

@router.post("/trigger")
async def trigger_sync(db: AsyncSession = Depends(get_db)):
    asyncio.create_task(run_sync_in_background(db))
    return {"status": "success", "message": "Sync started in background"}