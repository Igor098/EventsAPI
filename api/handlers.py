from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.models import EventSchema, CategorySchema
from dao.dao import EventsDAO
from dao.session_maker import session_manager
from loguru import logger

events_router = APIRouter()


async def _get_categories(session: AsyncSession = Depends(session_manager)) -> List[CategorySchema]:
    pass


async def _get_events_from_params(
        session: AsyncSession,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = None,
):
    """
    Данная функция отвечает за доступ к данным в базе данных
    :param session: Сессия для доступа к БД
    :param limit: Ограничение количества записей (1-100)
    :param offset: Смещение
    :param sort_by: Поля для сортировки
    :param order: Порядок сортировки
    :return: возвращает список событий в формате EventSchema
    """
    return await EventsDAO.get_events(
        session,
        limit,
        offset,
        sort_by,
        order
    )


async def _get_events_by_category(
        session: AsyncSession,
        category: str = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = None,
):
    """
    Данная функция отвечает за доступ к данным в базе данных по определенной категории
    :param session: Сессия для доступа к БД
    :param category: категория для выборки данных
    :param limit: Ограничение количества записей (1-100)
    :param offset: Смещение
    :param sort_by: Поля для сортировки
    :param order: Порядок сортировки
    :return: возвращает список событий в формате EventSchema
    """
    return await EventsDAO.get_events_by_category(
        session,
        category,
        limit,
        offset,
        sort_by,
        order
    )


async def _get_categories(session):
    return await EventsDAO.get_categories(session)


@events_router.get("/", response_model=List[EventSchema])
async def get_events(
        session: AsyncSession = Depends(session_manager.get_transaction_session),
        limit: int = Query(20, ge=1, le=100),  # Ограничение количества записей (1-100)
        offset: int = Query(0, ge=0),  # Смещение
        sort_by: str = Query("date_start", regex="^(date_start|name)$"),  # Поля для сортировки
        order: str = Query("asc", regex="^(asc|desc)$"),  # Порядок сортировки
):
    """
    Получение событий с поддержкой limit, offset и сортировки.
    """
    try:
        events = await _get_events_from_params(session, limit, offset, sort_by, order)
        if not events:
            logger.error("События не найдены.")
            raise HTTPException(status_code=404, detail="События не найдены.")

        return events

    except AttributeError:
        logger.error("Неверное поле для сортировки.")
        raise HTTPException(status_code=400, detail="Неверное поле для сортировки.")
    except Exception as e:
        logger.error(f"Ошибка сервера: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@events_router.get("/category", response_model=List[EventSchema])
async def get_events_by_category(
        session: AsyncSession = Depends(session_manager.get_transaction_session),
        category: str = Query(None),
        limit: int = Query(20, ge=1, le=100),  # Ограничение количества записей (1-100)
        offset: int = Query(0, ge=0),  # Смещение
        sort_by: str = Query("date_start", regex="^(date_start|name)$"),  # Поля для сортировки
        order: str = Query("asc", regex="^(asc|desc)$"),  # Порядок сортировки
):
    """
    Получение событий по категории с поддержкой limit, offset и сортировки.
    """
    try:
        events = await _get_events_by_category(session, category, limit, offset, sort_by, order)
        if not events:
            logger.error("События не найдены")
            raise HTTPException(status_code=404, detail="События не найдены.")

        return events
    except AttributeError:
        logger.error("Неверное поле для сортировки.")
        raise HTTPException(status_code=400, detail="Неверное поле для сортировки.")
    except Exception as e:
        logger.error(f"Ошибка сервера: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@events_router.get("/categories", response_model=List[CategorySchema])
async def get_categories(
    session: AsyncSession = Depends(session_manager.get_transaction_session),
):
    """
        Получение всех категорий
    """
    try:
        categories = await _get_categories(session)
        if not categories:
            logger.error("Категории не найдены")
            raise HTTPException(status_code=404, detail="Категории не найдены.")\

        return categories

    except Exception as e:
        logger.error(f"Ошибка сервера: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")