from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime, timezone
from db.database import get_db
from repositories.event_repo import EventRepository
from repositories.ticket_repo import TicketRepository
from services.provider_client import EventsProviderClient
from services.cache import SeatsCache

router = APIRouter(prefix="/api", tags=["tickets"])

class TicketRegisterRequest(BaseModel):
    event_id: str
    first_name: str
    last_name: str
    email: str
    seat: str

@router.post("/tickets", status_code=201)
async def register_ticket(
    request: TicketRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    event_repo = EventRepository(db)
    event = await event_repo.get(request.event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event.status != "published": #type: ignore
        raise HTTPException(status_code=400, detail="Registration closed")
    
    if event.registration_deadline: #type: ignore
        now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        if now_naive > event.registration_deadline: #type: ignore
            raise HTTPException(status_code=400, detail="Deadline passed")
    
    try:
        client = EventsProviderClient()
        result = await client.register(
            event_id=request.event_id,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            seat=request.seat
        )
        
        ticket_repo = TicketRepository(db)
        ticket_data = {
            "ticket_id": result.get("ticket_id"),
            "event_id": request.event_id,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "email": request.email,
            "seat": request.seat
        }
        await ticket_repo.create(ticket_data)
        
        seats_cache = SeatsCache()
        seats_cache.clear(request.event_id)
        
        return {"ticket_id": result.get("ticket_id")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")