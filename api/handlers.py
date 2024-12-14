from typing import Optional

from fastapi import APIRouter
import aiohttp

from config import settings


events_router = APIRouter()


async def _get_events_from_another_source(url: str, loc_id: int, limit: int, offset: int):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data={'APIKey': settings.AFISHA_KEY, "loc_id": loc_id,
                                           'limit': limit, 'offset': offset}) as response:
            return await response.json()


async def _get_events_from_category(url: str, category: str, loc_id: int, limit: int, offset: int):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data={'APIKey': settings.AFISHA_KEY, "cat_id": category, "loc_id": loc_id,
                                           'limit': limit, 'offset': offset}) as response:
            return await response.json()


@events_router.get("/")
async def get_orders(loc_id: int, limit: Optional[int] = 20, offset: Optional[int] = 0):
    return await _get_events_from_another_source("https://api.afisha7.ru/v1.0/events/", loc_id=loc_id, limit=limit,
                                                 offset=offset)


@events_router.get("/{category}")
async def get_orders(category: str, loc_id: int, limit: Optional[int] = 20, offset: Optional[int] = 0):
    return await _get_events_from_category("https://api.afisha7.ru/v1.0/events/", category=category, loc_id=loc_id,
                                           limit=limit,
                                           offset=offset)
