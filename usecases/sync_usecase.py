from sqlalchemy.ext.asyncio import AsyncSession
from services.provider_client import EventsProviderClient
from services.paginator import EventsPaginator
from repositories.event_repo import EventRepository
from repositories.sync_repo import SyncRepository
from datetime import datetime

class SyncUsecase:
    def __init__(
        self,
        session: AsyncSession,
        provider_client: EventsProviderClient
    ):
        self.session = session
        self.event_repo = EventRepository(session)
        self.sync_repo = SyncRepository(session)
        self.provider_client = provider_client
    
    async def execute(self, force_full: bool = False) -> int:
        metadata = await self.sync_repo.get_metadata()
        
        if force_full or not metadata.last_changed_at: #type: ignore
            changed_at = "2000-01-01"
        else:
            changed_at = metadata.last_changed_at.strftime("%Y-%m-%d")
        
        paginator = EventsPaginator(self.provider_client, changed_at)
        
        count = 0
        async for event_data in paginator:
            await self._save_event(event_data)
            count += 1
            if count >= 50:  # временный лимит
                break
        
        await self.sync_repo.update_sync_info(
            last_changed_at=datetime.utcnow(),
            status="success"
        )
        
        return count
    
    async def _save_event(self, event_data: dict):
        place = event_data.get("place", {})
        
        def parse_date(date_str: str) -> datetime:
            if not date_str:
                return None #type: ignore
            if 'Z' in date_str:
                date_str = date_str.replace('Z', '+00:00')
            dt = datetime.fromisoformat(date_str)
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            return dt
        
        event_in_db = {
            "id": event_data.get("id"),
            "name": event_data.get("name"),
            "event_time": parse_date(event_data.get("event_time")), #type: ignore
            "registration_deadline": parse_date(event_data.get("registration_deadline")), #type: ignore
            "status": event_data.get("status"),
            "number_of_visitors": event_data.get("number_of_visitors", 0),
            "place_id": place.get("id"),
            "place_name": place.get("name"),
            "place_city": place.get("city"),
            "place_address": place.get("address"),
            "seats_pattern": place.get("seats_pattern"),
            "changed_at": parse_date(event_data.get("changed_at")), #type: ignore
            "created_at": parse_date(event_data.get("created_at")), #type: ignore
            "status_changed_at": parse_date(event_data.get("status_changed_at")), #type: ignore
        }
        
        await self.event_repo.save(event_in_db)