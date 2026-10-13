import asyncio
from typing import Any, Dict, Optional
import httpx
from backend.app.main import app

class SyncTestClient:
    """
    Synchronous test client wrapper utilizing httpx.AsyncClient and ASGITransport.
    Avoids starlette.testclient version deprecation issues with httpx 0.28+.
    """
    def __init__(self, application=app):
        self.app = application
        self.base_url = "http://test"

    def get(self, path: str, **kwargs) -> httpx.Response:
        async def _call():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url=self.base_url) as c:
                return await c.get(path, **kwargs)
        return asyncio.run(_call())

    def post(self, path: str, **kwargs) -> httpx.Response:
        async def _call():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url=self.base_url) as c:
                return await c.post(path, **kwargs)
        return asyncio.run(_call())

    def put(self, path: str, **kwargs) -> httpx.Response:
        async def _call():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url=self.base_url) as c:
                return await c.put(path, **kwargs)
        return asyncio.run(_call())

    def delete(self, path: str, **kwargs) -> httpx.Response:
        async def _call():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url=self.base_url) as c:
                return await c.delete(path, **kwargs)
        return asyncio.run(_call())

test_client = SyncTestClient(app)
