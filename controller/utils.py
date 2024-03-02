import datetime
import sqlite3
from enums import CommandEnum
import socket
import time
import schemas
import aiosqlite
import asyncio
# from redis import asyncio as aioredis
from datetime import datetime
from app import DATABASE


# async def create_redis_pool():
#     return await aioredis.from_url('redis://redis:6379')

def run_async_process_data():
    asyncio.run(process_sensor_data())

async def process_sensor_data():
    """
    Принимает решение и отправляет сигнал манипулятору.

    Дополнительно подчищает таблицу сообщений от сенсоров, чтобы не перегружать память.
    Также заполняет таблицу сообщений к манипулятору.
    """
    # Примечание: здесь важно то, что в сенсорах и в контроллере один и тот же часовой пояс. Иначе нужно корректировать через timezone
    current_time = time.strftime('%Y-%m-%dT%H:%M:%S')
    five_seconds_ago = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time() - 5))
    outdated = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time() - 20))

    # Подчищаем таблицу сообщений от сенсора данными, которые уже точно не будут нужны
    just_exec_sql(
        'DELETE FROM sensor_messages WHERE datetime < ?',
        outdated,
    )
    # current_time1 = datetime.fromisoformat(current_time)
    # five_seconds_ago1 = datetime.fromisoformat(five_seconds_ago)
    # redis = await create_redis_pool()
    # sensor_messages = await redis.lrange('sensor_messages', 0, -1)  # Получаем все сообщения из кэша
    # sensor_data = []
    # await redis.close()
    # for message in sensor_messages:
    #     message_data = message.decode().split(':')
    #     message_datetime = datetime.fromisoformat(message_data[0])
    #     if five_seconds_ago1 <= message_datetime < current_time1:
    #         sensor_data.append((
    #             1,
    #             message_data[0],
    #             int(message_data[1])
    #         ))
    

    # Выполняем запрос к базе данных, чтобы получить данные за последние 5 секунд
    sensor_data = await async_fetch_sql(
        'SELECT * FROM sensor_messages WHERE datetime >= ? AND datetime < ?',
        five_seconds_ago,
        current_time,
    )

    if sensor_data:
        # Алгоритм принятия решения: если среднее значение payload больше 50, статус "up", иначе "down"
        avg_payload = sum([data[2] for data in sensor_data]) / len(sensor_data)
        status = CommandEnum.up.value if avg_payload > 50 else CommandEnum.down.value

        # Отправка управляющего сигнала манипулятору и сохранение в БД
        control_signal = schemas.ControlSignal(datetime=current_time, status=status)
        await async_just_exec_sql(
            'INSERT INTO to_manipulator_messages (datetime, status) VALUES (?, ?)',
            control_signal.datetime,
            control_signal.status,
        )
        print(f"Добавлено сообщение для манипулятора: {(control_signal.datetime, control_signal.status)}")
        send_to_manipulator(control_signal)


def just_exec_sql(raw_query: str, *args, **kwargs, ):
    """Выполненяет запрос в SQL без возврата данных."""
    with sqlite3.connect(DATABASE) as db:
        cursor = db.cursor()
        cursor.execute(raw_query, args)
        db.commit()


def fetch_sql(raw_query: str, *args, **kwargs, ):
    """Выполненяет запрос в SQL с получением данных."""
    with sqlite3.connect(DATABASE) as db:
        cursor = db.cursor()
        cursor.execute(raw_query, args)
        sensor_data = cursor.fetchall()
        return sensor_data


async def async_just_exec_sql(raw_query: str, *args, **kwargs, ):
    """Асинхронная версия метода just_exec_sql."""
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.cursor()
        await cursor.execute(raw_query, args)
        await db.commit()


async def async_fetch_sql(raw_query: str, *args, **kwargs, ):
    """Асинхронная версия метода fetch_sql."""
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.cursor()
        await cursor.execute(raw_query, args)
        sensor_data = await cursor.fetchall()
        return sensor_data


# Метод для 
def send_to_manipulator(control_signal: schemas.ControlSignal):
    """Отправляет управляющий сигнал манипулятору по TCP соединению."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('manipulator', 8090))
        client_socket.sendall(str(control_signal).encode())
