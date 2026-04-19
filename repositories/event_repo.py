from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db.models import Event
from typing import Optional, List, Dict, Any
from datetime import datetime


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, event_data: Dict[str, Any]) -> Event:
        """Сохранить или обновить событие в БД"""
        # Проверяем, есть ли уже такое событие
        existing = await self.get(event_data["id"])
        
        if existing:
            # Обновляем существующее
            for key, value in event_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            self.session.add(existing)
        else:
            # Создаём новое
            event = Event(**event_data)
            self.session.add(event)
        
        await self.session.commit()
        return existing if existing else event
    
    async def get(self, event_id: str) -> Optional[Event]:
        """Получить событие по ID"""
        result = await self.session.execute(
            select(Event).where(Event.id == event_id)
        )
        return result.scalar_one_or_none()
    
    async def list_with_filters(
        self, 
        date_from: Optional[str] = None, 
        page: int = 1, 
        page_size: int = 20
    ) -> tuple[List[Event], int]:
        """Получить список событий с фильтрацией и пагинацией"""
        query = select(Event)
        
        # Фильтрация по дате (события после указанной даты)
        if date_from:
            date_from_dt = datetime.fromisoformat(date_from)
            query = query.where(Event.event_time >= date_from_dt)
        
        # Сортировка по дате события
        query = query.order_by(Event.event_time)
        
        # Считаем общее количество
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)
        
        # Пагинация
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.session.execute(query)
        events = result.scalars().all()
        
        return events, total or 0 #type: ignore