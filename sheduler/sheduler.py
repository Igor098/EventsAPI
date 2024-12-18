import asyncio

from dao.dao import EventsDAO
from dao.session_maker import session_manager
from sheduler.parser import parse_data


@session_manager.connection(commit=True)
async def update_events_from_db(session):
    data = await parse_data()
    categories = data.get("categories")
    events = data.get("events")

    await EventsDAO.add_or_update_categories(session, categories)
    await EventsDAO.delete_expired_events(session)
    await EventsDAO.delete_event_places(session)
    await EventsDAO.add_or_update_events(session, events)
