from enum import Enum

from pygame.math import Vector2


class Direction(Enum):
    DOWN = Vector2(0, 1)
    LEFT = Vector2(-1, 0)
    UP = Vector2(0, -1)
    RIGHT = Vector2(1, 0)

    @classmethod
    def closest_direction(cls, vector: Vector2):
        return max(list(cls), key=lambda x: x.value.dot(vector))

    def opposite(self):
        if self == Direction.UP:
            return Direction.DOWN
        elif self == Direction.DOWN:
            return Direction.UP
        elif self == Direction.LEFT:
            return Direction.RIGHT
        else:
            return Direction.LEFT
