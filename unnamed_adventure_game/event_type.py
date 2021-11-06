from enum import Enum, auto


class EventType(Enum):
    COLLISION = auto()
    WEAPON_COLLISION = auto()
    INTERACTIVE_COLLISION = auto()
