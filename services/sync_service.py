from services.provider_client import EventsProviderClient
from services.paginator import EventsPaginator
from repositories.event_repo import EventRepository
from repositories.sync_repo import SyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional


class SyncService:
    def __init__(
        self, 
        db_session: AsyncSession,
        provider_client: EventsProviderClient
    ):
        self.db_session = db_session
        self.provider_client = provider_client
        self.event_repo = EventRepository(db_session)
        self.sync_repo = SyncRepository(db_session)
    
    async def sync(self, force_full: bool = False):
        """Запустить синхронизацию событий"""
        # 1. Получаем метаданные последней синхронизации
        metadata = await self.sync_repo.get_metadata()
        
        # 2. Определяем дату changed_at для запроса
        if force_full or not metadata.last_changed_at: #type: ignore
            changed_at = "2000-01-01"  # Полная синхронизация
        else:
            changed_at = metadata.last_changed_at.strftime("%Y-%m-%d")
        
        # 3. Обходим все события через пагинатор
        paginator = EventsPaginator(self.provider_client, changed_at)
        
        max_changed_at = metadata.last_changed_at
        
        async for event_data in paginator:
            # Сохраняем событие в БД
            await self._save_event(event_data)
            
            # Отслеживаем максимальный changed_at
            event_changed_at = event_data.get("changed_at")
            if event_changed_at:
                # Преобразуем строку в datetime
                if 'Z' in event_changed_at:
                    event_changed_at = event_changed_at.replace('Z', '+00:00')
                event_dt = datetime.fromisoformat(event_changed_at)
                if not max_changed_at or event_dt > max_changed_at: #type: ignore
                    max_changed_at = event_dt
        
        # 4. Обновляем метаданные синхронизации
        await self.sync_repo.update_sync_info(
            last_changed_at=max_changed_at, #type: ignore
            status="success"
        )
    
    async def _save_event(self, event_data: dict):
        """Сохраняет событие в БД, преобразуя данные из API"""
        place = event_data.get("place", {})
        
        def parse_date(date_str: Optional[str]) -> Optional[datetime]:
            if not date_str:
                return None
            if 'Z' in date_str:
                date_str = date_str.replace('Z', '+00:00')
            dt = datetime.fromisoformat(date_str)
            # Убираем часовой пояс для PostgreSQL TIMESTAMP WITHOUT TIME ZONE
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            return dt
        
        event_in_db = {
            "id": event_data.get("id"),
            "name": event_data.get("name"),
            "event_time": parse_date(event_data.get("event_time")),
            "registration_deadline": parse_date(event_data.get("registration_deadline")),
            "status": event_data.get("status"),
            "number_of_visitors": event_data.get("number_of_visitors", 0),
            "place_id": place.get("id"),
            "place_name": place.get("name"),
            "place_city": place.get("city"),
            "place_address": place.get("address"),
            "seats_pattern": place.get("seats_pattern"),
            "changed_at": parse_date(event_data.get("changed_at")),
            "created_at": parse_date(event_data.get("created_at")),
            "status_changed_at": parse_date(event_data.get("status_changed_at")),
        }
        
        await self.event_repo.save(event_in_db)