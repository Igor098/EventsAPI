from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import delete, and_, select, asc, desc
from datetime import datetime
from api.models import EventSchema, PlaceSchema
from dao.base import BaseDAO
from db.models import Event, Place, Category, EventsPlaces
from loguru import logger


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
                logger.info(f'Добавлена новая категория: {category.category_name}')
        logger.info('Категории обновлены')
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
            logger.info(f'Добавлено новое место: {new_place.place_name}')
        logger.info('Места обновлены')
        await session.commit()

    @classmethod
    async def delete_event_places(cls, session: AsyncSession):
        await session.execute(delete(EventsPlaces))
        await session.commit()
        logger.info('Таблица event_places обновлена')

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
                    new_mapping = EventsPlaces(event_id=event.event_id, place_id=existing_place.place_id)
                    session.add(new_mapping)
        logger.info('События обновлены')
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
        logger.info(f'Удалены события с прошедшей датой: {expired_events}')
        await session.commit()

    @classmethod
    async def get_events(
            cls,
            session: AsyncSession,
            limit: int = 20,
            offset: int = 0,
            sort_by: Optional[str] = "date_start",  # Параметр сортировки (по умолчанию — дата)
            order: Optional[str] = "asc",  # Порядок сортировки (по умолчанию — возрастание)
    ) -> List[EventSchema]:
        # Определяем поле сортировки
        sort_column = {
            "date_start": Event.date_start,
            "name": Event.name,
        }.get(sort_by, Event.date_start)  # По умолчанию сортируем по дате начала

        # Определяем порядок сортировки
        order_method = asc if order == "asc" else desc

        # Запрос для получения событий с учетом сортировки, offset и limit
        result = await session.execute(
            select(Event)
            .options(selectinload(Event.places))  # Загрузить связанные места
            .order_by(order_method(sort_column))  # Применить сортировку
            .offset(offset)  # Применить смещение
            .limit(limit)  # Применить ограничение
        )
        events = result.scalars().all()

        events_data = []

        for event in events:
            print(f"Retrieved event: {event.name}")
            # Формируем словарь данных для EventSchema
            event_data = {
                "event_id": event.event_id,
                "category_id": event.category_id,
                "location_id": event.location_id,
                "name": event.name,
                "date_start": event.date_start,
                "date_end": event.date_end,
                "logo": event.logo,
                "logo_width": event.logo_width,
                "logo_height": event.logo_height,
                "small_logo": event.small_logo,
                "small_logo_width": event.small_logo_width,
                "small_logo_height": event.small_logo_height,
                "event_description": event.event_description,
                "is_free": event.is_free,
                "min_price": event.min_price,
                "max_price": event.max_price,
                "age_restriction": event.age_restriction,
                "places": [PlaceSchema(name=place.place_name, address=place.place_address) for place in event.places
                           if place is not None],
            }
            # Создаём объект EventSchema, передавая словарь через распаковку
            events_data.append(EventSchema(**event_data))

        return events_data
