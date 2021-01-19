from typing import Tuple

from pygame import Rect, Surface
from pygame.math import Vector2

from adventure_game.direction import Direction


# TODO: Include in this classes the parent rectangle size (usually a sprite)
# where the hitbox would be positioned relative from it on the constructor.
# The get_offset routine would be also then be part of the constructor.


class Hitbox:
    def __init__(self, size: Tuple[float, float] = (0, 0), position: Vector2 = Vector2()):
        """
        Although the Rect class already has a position attribute, this is
        rounded to an integer. If we want to simulate smooth movement we need
        to update a position vector that takes any real value.
        """
        self.position = position
        self.rect = Rect(self.position, size)
        self.offset = Vector2()
        self.image = None

    def has_collided(self, other_rects):
        if self.rect.collidelist(other_rects) == -1:
            return False
        else:
            return True

    def get_offset(self, other_rectangle_size: Tuple[float, float], size=None):
        """
        Gets the Rect offset between the hitbox rectangle and another
        reference rectangle when they are centered. The coordinates are rounded
        to the closest integer
        """
        if not size:
            size = self.rect.size
        self.offset = Vector2([(p2 - p1) / 2 for p1, p2 in zip(size, other_rectangle_size)])

    def get_offset2(self, other_rectangle: Rect):
        offset_tuple = [p1 - p2 for p1, p2 in zip(self.rect.topleft, other_rectangle.topleft)]
        self.offset = Vector2(offset_tuple)

    def set_position(self, position):
        self.position = position + self.offset
        self.rect.topleft = self.position

    def set_image(self, color):
        self.image = Surface(self.rect.size)
        self.image.fill(color)
        self.image.set_alpha(100)


class SwordHitbox(Hitbox):
    """
    Implements two hitboxes (vertical and horizontal) for the sword attack
    """

    def __init__(
        self, depth, slash_range, extent, parent_size, position: Vector2 = Vector2(0, 0)
    ):
        super().__init__((slash_range, depth), position)
        self.depth = depth
        self.slash_range = slash_range
        self.extent = extent
        self.parent_size = parent_size
        self.horizontal = Rect(self.position, (slash_range, depth))
        self.vertical = Rect(self.position, (depth, slash_range))

    def get_offset(self, other_rectangle_size):
        max_dimension = max(self.slash_range, self.depth)
        super().get_offset(other_rectangle_size, (max_dimension,) * 2)

    def set_position(self, position: Vector2, direction: Direction):
        if direction in (Direction.DOWN, Direction.UP): #(0, 2):
            self.rect = self.horizontal
            relative_position = self.offset.elementwise() * Vector2(1, 0) + self.extent * direction.value
            if direction is Direction.DOWN:
                relative_position += (self.parent_size[1] - self.depth) * Direction.DOWN.value
                # + Vector2(0, self.extent * ((direction == 0) - (direction == 2)))
                # + Vector2(0, (self.parent_size[1] - self.depth) * (direction == 0))
        else:
            self.rect = self.vertical
            relative_position = self.offset.elementwise() * Vector2(0, 1) + self.extent * direction.value
            if direction is Direction.RIGHT:
                relative_position += (self.parent_size[0] - self.depth) * Direction.RIGHT.value
            # + Vector2(self.extent * ((direction == 3) - (direction == 1)), 0)
                # + Vector2((self.parent_size[0] - self.depth) * (direction == 3), 0)
        self.position = position + relative_position
        self.rect.topleft = self.position
