from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import SyncMetadata
from datetime import datetime, timezone
from typing import Optional


class SyncRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_metadata(self) -> SyncMetadata:
        result = await self.session.execute(
            select(SyncMetadata).where(SyncMetadata.id == "singleton")
        )
        metadata = result.scalar_one_or_none()
        
        if not metadata:
            metadata = SyncMetadata(id="singleton")
            self.session.add(metadata)
            await self.session.commit()
            await self.session.refresh(metadata)
        
        return metadata
    
    async def update_sync_info(
        self, 
        last_changed_at: Optional[datetime] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ):
        metadata = await self.get_metadata()
        
        metadata.last_sync_at = datetime.now(timezone.utc).replace(tzinfo=None) #type: ignore
        metadata.sync_status = status #type: ignore
        metadata.error_message = error_message #type: ignore
         
        if last_changed_at:
            metadata.last_changed_at = last_changed_at #type: ignore
        
        await self.session.commit()