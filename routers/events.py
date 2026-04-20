from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from repositories.event_repo import EventRepository
from typing import Optional
from services.provider_client import EventsProviderClient
from services.cache import SeatsCache
from pydantic import BaseModel
from datetime import datetime, timezone
from repositories.ticket_repo import TicketRepository

router = APIRouter(prefix="/api/events", tags=["events"])

@router.get("/")
@router.get("")
async def get_events(
    date_from: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    print(f"GET /api/events called with page={page}, date_from={date_from}")
    repo = EventRepository(db)
    events, total = await repo.list_with_filters(
        date_from=date_from,
        page=page,
        page_size=page_size
    )
    
    base_url = "/api/events"
    next_page = page + 1 if (page * page_size) < total else None
    prev_page = page - 1 if page > 1 else None
    
    next_url = f"{base_url}?page={next_page}&page_size={page_size}"
    if date_from:
        next_url += f"&date_from={date_from}"
    
    prev_url = f"{base_url}?page={prev_page}&page_size={page_size}"
    if date_from:
        prev_url += f"&date_from={date_from}"
    
    return {
        "count": total,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": e.id,
                "name": e.name,
                "place": {
                    "id": e.place_id,
                    "name": e.place_name,
                    "city": e.place_city,
                    "address": e.place_address
                },
                "event_time": e.event_time.isoformat() if e.event_time else None, #type: ignore
                "registration_deadline": e.registration_deadline.isoformat() if e.registration_deadline else None, #type: ignore
                "status": e.status,
                "number_of_visitors": e.number_of_visitors
            }
            for e in events
        ]
    }

@router.get("/{event_id}")
async def get_event_detail(event_id: str, db: AsyncSession = Depends(get_db)):
    repo = EventRepository(db)
    event = await repo.get(event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {
        "id": event.id,
        "name": event.name,
        "place": {
            "id": event.place_id,
            "name": event.place_name,
            "city": event.place_city,
            "address": event.place_address,
            "seats_pattern": event.seats_pattern
        },
        "event_time": event.event_time.isoformat() if event.event_time else None, #type: ignore
        "registration_deadline": event.registration_deadline.isoformat() if event.registration_deadline else None, #type: ignore
        "status": event.status,
        "number_of_visitors": event.number_of_visitors
    }   

seats_cache = SeatsCache(ttl_seconds=30)

@router.get("/{event_id}/seats")
async def get_available_seats(
    event_id: str,
    db: AsyncSession = Depends(get_db)
):
    repo = EventRepository(db)
    event = await repo.get(event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event.status != "published": # type: ignore
        raise HTTPException(
            status_code=400,
            detail=f"Event status is '{event.status}', only 'published' events have seats available"
        )
    
    cached = seats_cache.get(event_id)
    if cached is not None:
        return cached

    try:
        client = EventsProviderClient()
        seats_data = await client.get_seats(event_id)
        
        seats_cache.set(event_id, seats_data)
        
        return {
            "event_id": event_id,
            "available_seats": seats_data.get("seats", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch seats: {str(e)}")
    
class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    seat: str

@router.post("/{event_id}/register")
async def register(
    event_id: str,
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    event_repo = EventRepository(db)
    event = await event_repo.get(event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event.status != "published": #type: ignore
        raise HTTPException(status_code=400, detail=f"Event status is '{event.status}', registration closed")
    
    registration_deadline = event.registration_deadline
    if registration_deadline and datetime.now(timezone.utc).replace(tzinfo=None) > registration_deadline: #type: ignore
        raise HTTPException(status_code=400, detail="Registration deadline has passed")
    
    try:
        client = EventsProviderClient()
        result = await client.register(
            event_id=event_id,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            seat=request.seat
        )
        
        ticket_repo = TicketRepository(db)
        ticket_data = {
            "ticket_id": result.get("ticket_id"),
            "event_id": event_id,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "email": request.email,
            "seat": request.seat
        }
        await ticket_repo.create(ticket_data)
        
        from routers.events import seats_cache
        seats_cache.clear(event_id)
        
        return {"ticket_id": result.get("ticket_id")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
    
@router.delete("/tickets/{ticket_id}")
async def cancel_registration(
    ticket_id: str,
    db: AsyncSession = Depends(get_db)
):
    ticket_repo = TicketRepository(db)
    ticket = await ticket_repo.get_by_ticket_id(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    try:
        client = EventsProviderClient()
        result = await client.unregister(ticket.event_id, ticket.ticket_id) #type: ignore
        
        if result.get("success"):
            await ticket_repo.delete(ticket.id) #type: ignore
            
            seats_cache = SeatsCache()
            seats_cache.clear(ticket.event_id) #type: ignore
            
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail="Unregistration failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unregistration failed: {str(e)}")
    
