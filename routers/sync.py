from fastapi import APIRouter
from db.database import Session as AsyncSessionLocal
from config import settings
from services.provider_client import EventsProviderClient
from usecases.sync_usecase import SyncUsecase
import asyncio

router = APIRouter(prefix="/api/sync", tags=["sync"])

async def run_sync_in_background():
    async with AsyncSessionLocal() as db:
        try:
            client = EventsProviderClient(
                base_url=settings.PROVIDER_BASE_URL,
                api_key=settings.PROVIDER_API_KEY
            )
            usecase = SyncUsecase(db, client)
            count = await usecase.execute()
            print(f"Background sync completed: {count} events saved")
        except Exception as e:
            print(f"Background sync error: {e}")
            import traceback
            traceback.print_exc()

@router.post("/trigger")
async def trigger_sync():
    asyncio.create_task(run_sync_in_background())
    return {"status": "success", "message": "Sync started in background"}