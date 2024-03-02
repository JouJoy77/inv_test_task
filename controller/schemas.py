from typing import List
from pydantic import BaseModel


class SensorData(BaseModel):
    """Модель сообщения от сенсоров."""
    datetime: str
    payload: int


class ControlSignal(BaseModel):
    """Модель управляющего сигнала."""
    datetime: str
    status: str


class ResponseSchema(BaseModel):
    """Базовая схема ответа."""
    status: int = 200
    message: str = 'success'


class ManipulatorMessages(BaseModel):
    """Модель сообщения манипулятору."""
    id: int
    datetime: str
    status: str


class ManipulatorMessagesResponse(BaseModel):
    """Схема ответа со списком сообщений манипулятору."""
    data: List[ManipulatorMessages]
