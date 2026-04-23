from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs
from services.provider_client import EventsProviderClient


class EventsPaginator:
    def __init__(self, client: EventsProviderClient, changed_at: str):
        self.client = client
        self.changed_at = changed_at
        self._next_cursor: Optional[str] = None
        self._current_page: list = []
        self._index: int = 0
        self._finished: bool = False
    
    def __aiter__(self):
        return self
    
    async def __anext__(self) -> Dict[str, Any]:
        if self._finished:
            raise StopAsyncIteration
        
        if self._index >= len(self._current_page):
            await self._load_next_page()
            self._index = 0
        
        if not self._current_page:
            self._finished = True
            raise StopAsyncIteration
        
        event = self._current_page[self._index]
        self._index += 1
        return event
    
    async def _load_next_page(self):
        response = await self.client.get_events(
            changed_at=self.changed_at,
            cursor=self._next_cursor
        )
        
        self._current_page = response.get("results", [])
        
        next_url = response.get("next")
        if next_url and "cursor=" in next_url:
            parsed = urlparse(next_url)
            query_params = parse_qs(parsed.query)
            self._next_cursor = query_params.get("cursor", [None])[0]
        else:
            self._next_cursor = None