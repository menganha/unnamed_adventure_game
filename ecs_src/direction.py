from enum import Enum
from typing import NamedTuple


class DirectionVector(NamedTuple):
    x: int
    y: int


class Direction(Enum):
    """ Enum class with values that represent an 2d unit vector for the 4 main directions """
    NORTH = DirectionVector(0, -1)
    WEST = DirectionVector(-1, 0)
    EAST = DirectionVector(1, 0)
    SOUTH = DirectionVector(0, 1)
