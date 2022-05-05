from enum import Enum, auto


class EventType(Enum):
    DEATH = auto()
    PAUSE = auto()
    COLLISION = auto()
    HUD_UPDATE = auto()
    RESTART = auto()
