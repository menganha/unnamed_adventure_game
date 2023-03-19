from enum import Enum, auto
from random import randrange
from typing import NamedTuple


class IVec(NamedTuple):
    """ Immutable vector helper class """
    x: int | float
    y: int | float

    @property
    def length(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

    @classmethod
    def add(cls, *ivectors: 'IVec') -> 'IVec':
        x_compounded = 0
        y_compounded = 0
        for ivec in ivectors:
            x_compounded += ivec.x
            y_compounded += ivec.y
        return cls(x_compounded, y_compounded)

    @classmethod
    def sub(cls, ivec_l: 'IVec', ivec_r: 'IVec') -> 'IVec':
        return cls(ivec_l.x - ivec_r.x, ivec_l.y - ivec_r.y)


class Status(Enum):
    IDLE = auto()
    WALKING = auto()
    HIT = auto()
    ATTACKING = auto()
    FREEZE = auto()


class Direction(Enum):
    """ Enum class with values that represent a 2d unit vector for the 8 main directions """

    UP = IVec(0, -1)
    LEFT = IVec(-1, 0)
    RIGHT = IVec(1, 0)
    DOWN = IVec(0, 1)

    NORTH_WEST = IVec(-0.707107, -0.707107)  # Scaled to have constant measure
    NORTH_EAST = IVec(0.707107, -0.707107)
    SOUTH_WEST = IVec(-0.707107, 0.707107)
    SOUTH_EAST = IVec(0.707107, 0.707107)

    @classmethod
    def closest_direction(cls, vec: IVec) -> 'Direction':
        return max(list(cls), key=lambda direction: direction.value.x * vec.x + direction.value.y * vec.y)

    @classmethod
    def closest_diagonal_direction(cls, vec: IVec) -> 'Direction':
        return max(list(cls)[4:], key=lambda direction: direction.value.x * vec.x + direction.value.y * vec.y)

    @classmethod
    def random_direction(cls) -> 'Direction':
        return list(cls)[randrange(4)]

    def to_ivec(self, length: float) -> IVec:
        return IVec(self.value.x * length, self.value.y * length)
