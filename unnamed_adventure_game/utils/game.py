from collections import namedtuple
from enum import Enum, auto

_direction = namedtuple('Direction', ['x', 'y'])  # Helper type to define directions


class Direction(Enum):
    """ Enum class with values that represent an 2d unit vector for the 4 main directions """
    NORTH = _direction(0, -1)
    WEST = _direction(-1, 0)
    EAST = _direction(1, 0)
    SOUTH = _direction(0, 1)


class Status(Enum):
    IDLE = auto()
    MOVING = auto()
    HIT = auto()
    ATTACKING = auto()
    FREEZE = auto()
