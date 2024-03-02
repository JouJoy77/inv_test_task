from enum import Enum


class CommandEnum(str, Enum):
    """Команда манипулятору."""
    up = 'up'
    down = 'down'