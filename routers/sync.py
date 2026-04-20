from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from services.provider_client import EventsProviderClient
from services.sync_service import SyncService

router = APIRouter(prefix="/api/sync", tags=["sync"])

@router.post("/trigger")
async def trigger_sync(db: AsyncSession = Depends(get_db)):
    print("TRIGGER: /api/sync/trigger called")
    try:
        client = EventsProviderClient()
        print("TRIGGER: Client created")
        sync_service = SyncService(db, client)
        print("TRIGGER: SyncService created")
        await sync_service.sync()
        print("TRIGGER: Sync completed successfully")
        return {"status": "success", "message": "Sync completed"}
    except Exception as e:
        print(f"TRIGGER ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}