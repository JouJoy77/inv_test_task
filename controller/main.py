from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
import uvicorn
from utils import run_async_process_data
from routes import router


@asynccontextmanager
async def lifespan(app:FastAPI):
    """
    Задает первичные настройки и фоновые задачи для сервера FastAPI.

    :param app: Клиент FastAPI
    :type app: FastAPI
    """
    scheduler = BackgroundScheduler({'apscheduler.job_defaults.max_instances': 3})
    scheduler.add_job(run_async_process_data, "interval", seconds = 5)
    scheduler.start()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix='/controller', tags=['Контроллер'])


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)