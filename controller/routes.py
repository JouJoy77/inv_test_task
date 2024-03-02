from datetime import timedelta
from fastapi import HTTPException, Query, APIRouter
import schemas
import utils
# from redis import asyncio as aioredis

router = APIRouter()


# async def create_redis_pool(): # Попытки использовать redis, но программа замедлилась
#     return await aioredis.from_url('redis://redis:6379')


@router.post("/receive_sensor_data/", response_model=schemas.ResponseSchema)
async def receive_sensor_data(data: schemas.SensorData):
    """Получает данные от сенсоров."""
    try:
        # redis = await create_redis_pool()
        # await redis.lpush('sensor_messages', f"{data.datetime}:{data.payload}")
        # await redis.expire('sensor_messages', timedelta(seconds=20))
        # await redis.close()
        await utils.async_just_exec_sql('INSERT INTO sensor_messages (datetime, payload) VALUES (?, ?)', data.datetime, data.payload)
        print(f"Добавлено сообщение от сенсора: {data}")

    except Exception as e:
        print(f"Ошибка обработки сообщения: {e}")
        raise HTTPException(status_code=502, detail=f"Ошибка обработки сообщения: {e}")
    return dict()


@router.get("/get_manipulator_messages/", response_model=schemas.ManipulatorMessagesResponse)
async def get_manipulator_messages(start_time: str = Query(...), end_time: str = Query(...)):
    """Выполняет запрос к базе данных, чтобы получить управляющие сигналы за указанный интервал времени."""
    manipulator_data = await utils.async_fetch_sql(
        'SELECT * FROM to_manipulator_messages WHERE datetime >= ? AND datetime <= ?',
        start_time,
        end_time,
    )
    response = []
    for item in manipulator_data:
        response.append(schemas.ManipulatorMessages(id=item[0], datetime=item[1], status=item[2]))
    return dict(data=response)
