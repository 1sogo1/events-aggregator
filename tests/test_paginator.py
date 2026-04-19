import pytest
from services.paginator import EventsPaginator


@pytest.mark.asyncio
async def test_paginator_returns_all_events():
    class MockClient:
        def __init__(self):
            self.responses = [
                {"results": [{"id": "1"}, {"id": "2"}], "next": "cursor123"},
                {"results": [{"id": "3"}], "next": None}
            ]
            self.index = 0
        
        async def get_events(self, changed_at, cursor=None):
            if self.index >= len(self.responses):
                return {"results": [], "next": None}
            response = self.responses[self.index]
            self.index += 1
            return response
    
    client = MockClient()
    paginator = EventsPaginator(client, changed_at="2000-01-01") #type: ignore
    
    events = []
    async for event in paginator:
        events.append(event)
    
    assert len(events) == 3
    assert events[0]["id"] == "1"
    assert events[1]["id"] == "2"
    assert events[2]["id"] == "3"


@pytest.mark.asyncio
async def test_paginator_empty():
    class MockClient:
        async def get_events(self, changed_at, cursor=None):
            return {"results": [], "next": None}
    
    client = MockClient()
    paginator = EventsPaginator(client, changed_at="2000-01-01") #type: ignore
    
    events = []
    async for event in paginator:
        events.append(event)
    
    assert len(events) == 0