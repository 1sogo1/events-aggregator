from sqlalchemy.ext.asyncio import AsyncSession
from repositories.event_repo import EventRepository
from services.provider_client import EventsProviderClient
from services.cache import SeatsCache
from core.enums import EventStatus
from fastapi import HTTPException

class GetSeatsUsecase:
    def __init__(
        self,
        session: AsyncSession,
        provider_client: EventsProviderClient
    ):
        self.event_repo = EventRepository(session)
        self.provider_client = provider_client
        self.cache = SeatsCache()
    
    async def execute(self, event_id: str) -> dict:
        event = await self.event_repo.get(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        if event.status != EventStatus.PUBLISHED.value: #type: ignore
            raise HTTPException(
                status_code=400,
                detail=f"Event status is '{event.status}', only 'published' events have seats available"
            )
        
        cached = self.cache.get(event_id)
        if cached is not None:
            return cached
        
        seats_data = await self.provider_client.get_seats(event_id)
        
        result = {
            "event_id": event_id,
            "available_seats": seats_data.get("seats", [])
        }
        
        self.cache.set(event_id, result)
        
        return result