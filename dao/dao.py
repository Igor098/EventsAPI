from typing import List

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete, update, and_, or_, select, insert
from datetime import datetime

from dao.base import BaseDAO
from dao.session_maker import session_manager
from db.models import Event, Place, Category, EventsPlaces  # Предполагается, что модели описаны в файле `models.py`


async def parse_date(date_str):
    """Превращает строку с датой в объект datetime."""
    return datetime.strptime(date_str, "%Y-%m-%d") if date_str else None


class EventsDAO(BaseDAO):
    model = Event

    @classmethod
    async def add_or_update_categories(cls, session: AsyncSession, categories: List[BaseModel]):
        for category in categories:
            existing_category = await session.execute(
                select(Category).where(
                    Category.category_id == category.category_id
                )
            )
            existing_category = existing_category.scalar_one_or_none()
            if existing_category:
                existing_category.category_name = category.category_name
            else:
                session.add(Category(category_id=category.category_id, category_name=category.category_name))
        await session.commit()

    @staticmethod
    async def add_or_update_places(session: AsyncSession, places: List[BaseModel]):
        for place in places:
            existing_place = await session.execute(
                select(Place).where(
                    and_(
                        Place.place_name == place.get('name'),
                        Place.place_address == place.get('address')
                    )
                )
            )
            existing_place = existing_place.scalar_one_or_none()
            if existing_place:
                continue  # Предполагаем, что место не изменяется
            new_place = Place(place_name=place.get('name'), place_address=place.get('address'))
            session.add(new_place)
        await session.commit()

    @classmethod
    async def add_or_update_events(cls, session: AsyncSession, events: List[BaseModel]):
        for event in events:
            event_dict = event.model_dump(exclude_unset=True)
            update_data = {k: v for k, v in event_dict.items() if k != "places"}
            event = Event(**update_data)
            print(update_data)
            existing_event = await session.execute(
                select(Event).where(Event.event_id == event.event_id)
            )
            existing_event = existing_event.scalar_one_or_none()

            if existing_event:
                # Обновляем поля события
                for attr, value in vars(event).items():
                    setattr(existing_event, attr, value)
            else:
                session.add(event)

            await EventsDAO.add_or_update_places(session, event_dict.get('places'))

            # Обработка мест
            for place in event_dict.get('places'):
                existing_place = await session.execute(
                    select(Place).where(
                        and_(
                            Place.place_name == place['name'],
                            Place.place_address == place['address']
                        )
                    )
                )

                existing_place = existing_place.scalar_one_or_none()

                if not existing_place:
                    new_place = Place(place_name=place['name'], place_address=place['address'])
                    session.add(new_place)
                else:
                    existing_ep = await session.execute(
                        select(EventsPlaces).where(
                            EventsPlaces.event_id == place['name']
                        )
                    )
                    new_mapping = EventsPlaces(event_id=event.event_id, place_id=existing_place.place_id)

                    session.add(new_mapping)
        await session.commit()

    @classmethod
    async def delete_expired_events(cls, session: AsyncSession):
        today = datetime.now().date().strftime('%Y-%m-%d')
        expired_events = await session.execute(
            select(Event).where(
                Event.date_end < today
            )
        )
        expired_events = expired_events.scalars().all()

        for event in expired_events:
            await session.execute(
                delete(EventsPlaces).where(
                    EventsPlaces.event_id == event.event_id
                )
            )
            await session.delete(event)

        await session.commit()