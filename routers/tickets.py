from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from db.database import get_db
from config import settings
from services.provider_client import EventsProviderClient
from usecases.ticket_usecases import CreateTicketUsecase, CancelTicketUsecase

router = APIRouter(prefix="/api", tags=["tickets"])

class TicketRegisterRequest(BaseModel):
    event_id: str
    first_name: str
    last_name: str
    email: str
    seat: str

def get_provider_client():
    return EventsProviderClient(settings.PROVIDER_BASE_URL, settings.PROVIDER_API_KEY)

@router.post("/tickets", status_code=201)
async def register_ticket(
    request: TicketRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    client = get_provider_client()
    usecase = CreateTicketUsecase(db, client)
    ticket_id = await usecase.execute(
        event_id=request.event_id,
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        seat=request.seat
    )
    return {"ticket_id": ticket_id}
@router.delete("/tickets/{ticket_id}")
@router.delete("/tickets/{ticket_id}/")
async def cancel_ticket(
    ticket_id: str,
    db: AsyncSession = Depends(get_db)
):
    client = get_provider_client()
    usecase = CancelTicketUsecase(db, client)
    result = await usecase.execute(ticket_id)
    return {"success": result}