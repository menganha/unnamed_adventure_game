from enum import Enum, auto


class State(Enum):
    ATTACK = auto()
    WALK = auto()
    IDLE = auto()
    HIT = auto()
