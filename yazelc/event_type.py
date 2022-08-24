from enum import Enum, auto


# noinspection PyArgumentList
class EventType(Enum):
    DEATH = auto()
    PAUSE = auto()
    COLLISION = auto()
    HUD_UPDATE = auto()
    RESTART = auto()
