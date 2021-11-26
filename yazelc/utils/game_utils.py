from collections import namedtuple
from enum import Enum, auto
from random import randrange

_direction = namedtuple('Direction', ['x', 'y'])  # Helper type to define directions


class Direction(Enum):
    """ Enum class with values that represent an 2d unit vector for the 8 main directions """

    NORTH = _direction(0, -1)
    WEST = _direction(-1, 0)
    EAST = _direction(1, 0)
    SOUTH = _direction(0, 1)

    NORTH_WEST = _direction(-0.707107, -0.707107)  # Scaled to have constant measure
    NORTH_EAST = _direction(0.707107, -0.707107)
    SOUTH_WEST = _direction(-0.707107, 0.707107)
    SOUTH_EAST = _direction(0.707107, 0.707107)

    @classmethod
    def closest_direction(cls, vec_x: int, vec_y: int) -> 'Direction':
        return max(list(cls),
                   key=lambda direction: direction.value.x * vec_x + direction.value.y * vec_y)

    @classmethod
    def random_direction(cls) -> 'Direction':
        return list(cls)[randrange(4)]


class Status(Enum):
    IDLE = auto()
    MOVING = auto()
    HIT = auto()
    ATTACKING = auto()
    FREEZE = auto()
