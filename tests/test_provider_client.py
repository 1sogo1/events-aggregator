import pytest
from unittest.mock import AsyncMock, patch
from services.provider_client import EventsProviderClient


@pytest.mark.asyncio
async def test_get_events():
    client = EventsProviderClient("https://fake-api.com", "fake-key")
    
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"results": [{"id": "123"}], "next": None})
    mock_response.raise_for_status = AsyncMock()
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await client.get_events(changed_at="2000-01-01")
        
        assert result["results"][0]["id"] == "123"


@pytest.mark.asyncio
async def test_get_seats():
    client = EventsProviderClient("https://fake-api.com", "fake-key")
    
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"seats": ["A1", "A2"]})
    mock_response.raise_for_status = AsyncMock()
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await client.get_seats("event-123")
        
        assert len(result["seats"]) == 2


@pytest.mark.asyncio
async def test_register():
    client = EventsProviderClient("https://fake-api.com", "fake-key")
    
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"ticket_id": "ticket-456"})
    mock_response.raise_for_status = AsyncMock()
    
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        result = await client.register(
            event_id="event-123",
            first_name="Иван",
            last_name="Иванов",
            email="ivan@example.com",
            seat="A1"
        )
        
        assert result["ticket_id"] == "ticket-456"