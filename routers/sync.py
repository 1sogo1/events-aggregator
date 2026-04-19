from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from services.provider_client import EventsProviderClient
from services.sync_service import SyncService

router = APIRouter(prefix="/api/sync", tags=["sync"])

@router.post("/trigger")
async def trigger_sync(db: AsyncSession = Depends(get_db)):
    try:
        client = EventsProviderClient()
        sync_service = SyncService(db, client)
        await sync_service.sync()
        return {"status": "success", "message": "Sync completed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}