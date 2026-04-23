import httpx
from typing import Optional, Dict, Any
from urllib.parse import urljoin
import logging


logger = logging.getLogger(__name__)

class EventsProviderClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
    
    async def get_events(self, changed_at: str, cursor: Optional[str] = None) -> Dict[str, Any]:
        url = urljoin(self.base_url + '/', '/api/events/')
        params: Dict[str, str] = {"changed_at": changed_at}
        if cursor:
            params["cursor"] = cursor
        
        logger.debug(f"API REQUEST: {url}")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                url,
                params=params,
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_seats(self, event_id: str) -> Dict[str, Any]:
        url = urljoin(self.base_url + '/', f'/api/events/{event_id}/seats/')
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                url,
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            return response.json()
    
    async def register(self, event_id: str, first_name: str, last_name: str, email: str, seat: str) -> Dict[str, Any]:
        url = urljoin(self.base_url + '/', f'/api/events/{event_id}/register/')
        body = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat
        }
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                url,
                json=body,
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            return response.json()
    
    async def unregister(self, event_id: str, ticket_id: str) -> Dict[str, Any]:
        url = urljoin(self.base_url + '/', f'/api/events/{event_id}/unregister/')
        body = {"ticket_id": ticket_id}
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.request(
                method="DELETE",
                url=url,
                json=body,
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            return response.json()