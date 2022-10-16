from collections import namedtuple
from enum import Enum, auto
from random import randrange

ImmutableVec = namedtuple('ImmutableVec', ['x', 'y'])


class Status(Enum):
    IDLE = auto()
    MOVING = auto()
    HIT = auto()
    ATTACKING = auto()
    FREEZE = auto()


class Direction(Enum):
    """ Enum class with values that represent a 2d unit vector for the 8 main directions """

    UP = ImmutableVec(0, -1)
    LEFT = ImmutableVec(-1, 0)
    RIGHT = ImmutableVec(1, 0)
    DOWN = ImmutableVec(0, 1)

    NORTH_WEST = ImmutableVec(-0.707107, -0.707107)  # Scaled to have constant measure
    NORTH_EAST = ImmutableVec(0.707107, -0.707107)
    SOUTH_WEST = ImmutableVec(-0.707107, 0.707107)
    SOUTH_EAST = ImmutableVec(0.707107, 0.707107)

    @classmethod
    def closest_direction(cls, vec_x: int, vec_y: int) -> 'Direction':
        return max(list(cls), key=lambda direction: direction.value.x * vec_x + direction.value.y * vec_y)

    @classmethod
    def closest_diagonal_direction(cls, vec_x: int, vec_y: int) -> 'Direction':
        return max(list(cls)[4:], key=lambda direction: direction.value.x * vec_x + direction.value.y * vec_y)

    @classmethod
    def random_direction(cls) -> 'Direction':
        return list(cls)[randrange(4)]
