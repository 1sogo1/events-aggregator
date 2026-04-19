from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import Ticket
from typing import Optional, Dict, Any

class TicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, ticket_data: Dict[str, Any]) -> Ticket:
        ticket = Ticket(**ticket_data)
        self.session.add(ticket)
        await self.session.commit()
        await self.session.refresh(ticket)
        return ticket
    
    async def get(self, ticket_id: str) -> Optional[Ticket]:
        result = await self.session.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_ticket_id(self, ticket_id: str) -> Optional[Ticket]:
        result = await self.session.execute(
            select(Ticket).where(Ticket.ticket_id == ticket_id)
        )
        return result.scalar_one_or_none()
    
    async def delete(self, ticket_id: str) -> bool:
        ticket = await self.get(ticket_id)
        if ticket:
            await self.session.delete(ticket)
            await self.session.commit()
            return True
        return False