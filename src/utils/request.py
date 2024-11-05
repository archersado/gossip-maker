# ... existing code ...
import aiohttp
import asyncio
import uuid

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client_id = str(uuid.uuid4())

    async def request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()

    async def get(self, endpoint: str, **kwargs):
        return await self.request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, data: dict, **kwargs):
        return await self.request("POST", endpoint, json=data, **kwargs)
        