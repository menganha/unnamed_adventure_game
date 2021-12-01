from enum import Enum, auto


class EventType(Enum):
    PAUSE = auto()
    COLLISION = auto()
    HUD_UPDATE = auto()
