import uvicorn
from fastapi import FastAPI, APIRouter

from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from starlette.middleware.cors import CORSMiddleware

from sheduler.sheduler import update_events_from_db
from api.handlers import events_router
from loguru import logger

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом планировщика приложения.

    Args:
        app (FastAPI): Экземпляр приложения FastAPI.
    """
    try:
        # Настройка и запуск планировщика
        scheduler.add_job(
            update_events_from_db,
            trigger=IntervalTrigger(minutes=60),
            id='events_update_job',
            replace_existing=True
        )
        scheduler.start()
        logger.info("Планировщик обновления событий в Нижнем Новгороде запущен")
        yield
    except Exception as e:
        logger.error(f"Ошибка инициализации планировщика: {e}")
    finally:
        # Завершение работы планировщика
        scheduler.shutdown()
        logger.info("Планировщик обновления событий в Нижнем Новгороде остановлен")


origins = [
    "http://localhost",
    "http://localhost:3000",
]

app = FastAPI(title="Events API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_api_router = APIRouter()

main_api_router.include_router(events_router, prefix="/events", tags=["events"])
app.include_router(main_api_router)


@app.get("/")
async def root():
    return {"Hello": "World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
