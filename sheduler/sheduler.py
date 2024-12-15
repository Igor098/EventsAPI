from dao.session_maker import session_manager
from parser import parse_data


@session_manager.connection(commit=True)
async def add_events_to_db(session):
    categories, events = await parse_data()
