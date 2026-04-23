from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.event_repo import EventRepository
from db.models import Event


class GetEventsUsecase:
    def __init__(self, session: AsyncSession):
        self.repo = EventRepository(session)
    
    async def execute(
        self,
        date_from: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Event], int]:
        return await self.repo.list_with_filters(
            date_from=date_from,
            page=page,
            page_size=page_size
        )

class GetEventDetailUsecase:
    def __init__(self, session: AsyncSession):
        self.repo = EventRepository(session)
    
    async def execute(self, event_id: str) -> Optional[Event]:
        return await self.repo.get(event_id)