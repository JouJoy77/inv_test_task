from fastapi import FastAPI
from pydantic import BaseModel
import time
import random
from threading import Thread
from multiprocessing import Process
import aiohttp
import requests
import asyncio


app = FastAPI()


class SensorData(BaseModel):
    """Модель данных для сообщения от сенсора к контроллеру."""
    datetime: str
    payload: int


async def generate_sensor_data(sensor_id: int):
    """Генерирует данные для отправки в контроллер."""
    messages_per_second = 3
    time_for_msg = 1/messages_per_second

    while True:
        t = 0
        more_time_than_need = 0  # Если положительное - нужно замедлиться, в ином случае ускориться

        for i in range(messages_per_second):
            start_time = time.time()
            current_time = time.strftime('%Y-%m-%dT%H:%M:%S')
            payload = random.randint(1, 100)
            message = SensorData(datetime=current_time, payload=payload)

            await send_to_controller(message, sensor_id)

            end_time = time.time()
            elapsed_time = end_time - start_time
            remaining_time = time_for_msg - elapsed_time
            
            if remaining_time > 0 and more_time_than_need>=0:
                t+=time_for_msg
                time.sleep(remaining_time)
            else:
                more_time_than_need+=remaining_time
                t+=elapsed_time
                print("Warning: Message generation took longer than expected.")
        print(f"Потраченное время на генерацию и отправку, t = {t}")

async def send_to_controller(message: SensorData, sensor_id: int):
    """Отправляет сообщение в контроллер."""
    url = "http://controller:8000/controller/receive_sensor_data/"
    try:
        async with aiohttp.ClientSession() as session:
            # Здесь мы не ждем ответ, просто потоком отправляем данные
            async with session.post(url, json=message.dict(), timeout=0.002) as response:
                await response.content.read()
        print(f"Sensor {sensor_id} -> Controller: {message.dict()}")
    except requests.exceptions.ReadTimeout:
        pass
    except Exception:
        print("Контроллер недоступен или соединение не установлено.")


def run_async_processing_data(process: int):
    """Запускает асинхронную генерацию сообщений."""
    asyncio.run(generate_sensor_data(process))


@app.on_event("startup")
async def start_sensor_threads():
    """Запускает потоки для генерации данных каждого сенсора."""
    for i in range(1, 9):
        process = Process(target=run_async_processing_data, args=(i,))
        process.daemon = True
        process.start()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
