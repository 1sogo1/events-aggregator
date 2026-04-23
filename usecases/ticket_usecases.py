from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.event_repo import EventRepository
from repositories.ticket_repo import TicketRepository
from services.provider_client import EventsProviderClient
from services.cache import SeatsCache
from core.enums import EventStatus
from fastapi import HTTPException

class CreateTicketUsecase:
    def __init__(
        self,
        session: AsyncSession,
        provider_client: EventsProviderClient
    ):
        self.session = session
        self.event_repo = EventRepository(session)
        self.ticket_repo = TicketRepository(session)
        self.provider_client = provider_client
        self.cache = SeatsCache()
    
    async def execute(self, event_id: str, first_name: str, last_name: str, email: str, seat: str) -> str:
        event = await self.event_repo.get(event_id)
        if not event:
            raise HTTPException(status_code=400, detail="Event not found")
        
        if event.status != EventStatus.PUBLISHED.value: #type: ignore
            raise HTTPException(status_code=400, detail="Registration closed")
        
        if event.registration_deadline: #type: ignore
            now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
            if now_naive > event.registration_deadline: #type: ignore
                raise HTTPException(status_code=400, detail="Deadline passed")
        
        result = await self.provider_client.register(
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat
        )
        
        ticket_id = result.get("ticket_id")
        
        ticket_data = {
            "ticket_id": ticket_id,
            "event_id": event_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat
        }
        await self.ticket_repo.create(ticket_data)
        
        # 6. Очищаем кэш мест
        self.cache.clear(event_id)
        
        return ticket_id #type: ignore

class CancelTicketUsecase:
    def __init__(
        self,
        session: AsyncSession,
        provider_client: EventsProviderClient
    ):
        self.session = session
        self.ticket_repo = TicketRepository(session)
        self.provider_client = provider_client
        self.cache = SeatsCache()
    
    async def execute(self, ticket_id: str) -> bool:
        ticket = await self.ticket_repo.get_by_ticket_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        result = await self.provider_client.unregister(ticket.event_id, ticket.ticket_id) #type: ignore
        
        if result.get("success"):
            await self.ticket_repo.delete(ticket.id) #type: ignore
            self.cache.clear(ticket.event_id) #type: ignore
            return True
        else:
            raise HTTPException(status_code=500, detail="Unregistration failed")