from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from db.database import get_db
from config import settings
from services.provider_client import EventsProviderClient
from usecases.event_usecases import GetEventsUsecase, GetEventDetailUsecase
from usecases.seats_usecase import GetSeatsUsecase

router = APIRouter(prefix="/api/events", tags=["events"])

def get_provider_client():
    return EventsProviderClient(settings.PROVIDER_BASE_URL, settings.PROVIDER_API_KEY)

@router.get("/")
async def get_events(
    request: Request,
    date_from: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    usecase = GetEventsUsecase(db)
    events, total = await usecase.execute(date_from, page, page_size)
    
    base_url = str(request.base_url).rstrip('/')
    next_page = page + 1 if (page * page_size) < total else None
    prev_page = page - 1 if page > 1 else None
    
    next_url = f"{base_url}/api/events?page={next_page}&page_size={page_size}" if next_page else None
    prev_url = f"{base_url}/api/events?page={prev_page}&page_size={page_size}" if prev_page else None
    
    if date_from:
        if next_url:
            next_url += f"&date_from={date_from}"
        if prev_url:
            prev_url += f"&date_from={date_from}"
    
    return {
        "count": total,
        "next": next_url,
        "previous": prev_url,
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
                "registration_deadline": e.registration_deadline.isoformat() if e.registration_deadline else None,#type: ignore
                "status": e.status,
                "number_of_visitors": e.number_of_visitors
            }
            for e in events
        ]
    }

@router.get("/{event_id}")
async def get_event_detail(
    event_id: str,
    db: AsyncSession = Depends(get_db)
):
    usecase = GetEventDetailUsecase(db)
    event = await usecase.execute(event_id)
    
    if not event:
        return {"error": "Event not found"}, 404
    
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

@router.get("/{event_id}/seats")
async def get_available_seats(
    event_id: str,
    db: AsyncSession = Depends(get_db)
):
    client = get_provider_client()
    usecase = GetSeatsUsecase(db, client)
    return await usecase.execute(event_id)