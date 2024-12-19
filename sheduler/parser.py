import asyncio
import datetime
import io
import random
import aiohttp
from PIL import Image
from api.models import EventSchema, CategorySchema
from config import settings
from loguru import logger


async def _get_total_events(url: str, loc_id: int):
    """
    Функция для получения общего количества мероприятий в городе через API
    :param url: адрес API с мероприятиями
    :param loc_id: ID города, для которого запрашиваются мероприятия
    :return: возвращает общее количество событий
    """
    response = await _get_events(url, loc_id, limit=1, offset=0)
    return int(response.get("total"))


async def _get_events(url: str, loc_id: int, limit: int, offset: int):
    """
    Функция для получения всех мероприятий из определенного города через API
    :param url: адрес API с мероприятиями
    :param loc_id: ID города, для которого запрашиваются мероприятия
    :param limit: запрашиваемое количество мероприятий. Не более 100
    :param offset: номер мероприятия, с которого начинается отсчет количества
    :return: возвращает все мероприятия в определенном городе
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data={'APIKey': settings.AFISHA_KEY, "loc_id": loc_id,
                                           "limit": limit, "offset": offset}) as response:
            return await response.json()


async def _get_categories(url: str):
    """
    Функция для получения всех категорий мероприятий в API
    :param url: адрес API с мероприятиями
    :return: возвращает все категории мероприятий
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data={'APIKey': settings.AFISHA_KEY}) as response:
            return await response.json()


async def _fetch_events(url, loc_id, limit, offset):
    """
    Функция для выполнения параллельных запросов к API
    :param url: адрес API с мероприятиями
    :param loc_id: ID города, для которого запрашиваются мероприятия
    :param limit: запрашиваемое количество мероприятий. Не более 100
    :param offset: номер мероприятия, с которого начинается отсчет количества
    :return: возвращает события из запроса
    """
    events_response = await _get_events(url, loc_id, limit=limit, offset=offset)
    return events_response.get("events")


async def _get_all_events(url: str, loc_id: int):
    """
    Запускает выполнение параллельных запросов к API и объединяет их в один список
    :param url: адрес API с мероприятиями
    :param loc_id: ID города, для которого запрашиваются мероприятия
    :return: возвращает список всех событий в заданном городе
    """
    total = await _get_total_events(url, loc_id)
    offset = 0
    events = []
    count = 1

    while total > 0:
        logger.info(f'Запускаю извлечение данных. Запрос No {count}. Количество записей осталось {total}')
        limit = 100 if total > 100 else total
        logger.info(f'Количество записей за раз: {limit}')
        logger.info(f'Смещение: {offset}')

        if total < limit:
            num_tasks = 1
        else:
            num_tasks = min(5, (total + limit - 1) // limit)

        tasks = []
        for _ in range(num_tasks):
            task = _fetch_events(url, loc_id, limit, offset)
            tasks.append(task)
            offset += limit

        logger.info(f'Количество задач: {len(tasks)}')

        results = await asyncio.gather(*tasks)
        events.extend([event for result in results for event in result])

        total -= num_tasks * limit
        count += num_tasks

        await asyncio.sleep(random.randint(2, 5))

    logger.info(f"Добавлено {len(events)} событий")
    return events


async def _get_str_date(date: str):
    """
    Переводит дату из числового представления в человеческий вид
    :param date: дата в числовом виде
    :return: возвращает дату в виде строки
    """
    correct_date = datetime.datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d')
    return correct_date


async def _get_image_size(url: str, retries=2):
    """
    Извлекает размеры картинки
    :param url: адрес API с мероприятиями
    :param retries: количество попыток
    :return: возвращает кортеж с размером картинки
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                image_bytes = await response.read()
                im = Image.open(io.BytesIO(image_bytes))

                width, height = im.size
                return width, height

    except Exception as e:
        logger.info(f"Картинка недоступна: {e}")
        if retries > 0:
            return await _get_image_size(url, retries - 1)
        else:
            return 0, 0


async def _create_event(event: dict) -> EventSchema:
    """
    Переводит данные из стороннего API в формат для записи в БД
    :param event: мероприятие из внешнего API
    :return: возвращает событие в формате EventSchema для записи в БД
    """
    print("Обрабатываю событие", event.get("name"))
    logo = event.get("logo")
    logo_width, logo_height = await _get_image_size(logo)

    small_logo = event.get("logo_p")
    small_logo_width, small_logo_height = await _get_image_size(small_logo)
    places = event.get("places")

    return EventSchema(**{
        "event_id": int(event.get("id")),
        "category_id": int(event.get("cat_id")),
        "location_id": int(event.get("loc_id")),
        "name": event.get("name"),
        "date_start": await _get_str_date(event.get("date_start")),
        "date_end": await _get_str_date(event.get("date_end")),
        "logo": logo,
        "logo_width": logo_width,
        "logo_height": logo_height,
        "small_logo": small_logo,
        "small_logo_width": small_logo_width,
        "small_logo_height": small_logo_height,
        "event_description": event.get("description"),
        "is_free": True if event.get("is_free") != "0" else False,
        "min_price": event.get("min_price"),
        "max_price": event.get("max_price"),
        "age_restriction": event.get("age"),
        "places": places,
    })


async def _parse_events_data(url: str, loc_id: int):
    events = []
    events_data = await _get_all_events(url, loc_id)

    batch_size = 100
    batches = [events_data[i:i + batch_size] for i in range(0, len(events_data), batch_size)]

    for batch in batches:
        tasks = [_create_event(event) for event in batch]
        results = await asyncio.gather(*tasks)
        events.extend(results)

    print(f"Добавлено {len(events)} событий")
    return events


async def _parse_categories_data(url: str):
    categories = []
    categories_response = await _get_categories(url)
    categories_data = categories_response.get("categories")

    for category in categories_data:
        categories.append(CategorySchema(**{
            "category_id": int(category.get("id")),
            "category_name": category.get("name"),
        }))

    print(f"Добавлено {len(categories)} категорий")
    return categories


async def parse_data():
    categories = await _parse_categories_data("https://api.afisha7.ru/v1.0/categories/")
    events = await _parse_events_data("https://api.afisha7.ru/v1.0/events/", loc_id=1310)
    data = {"categories": categories, "events": events}
    return data
