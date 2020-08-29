from pygame import Rect
from pygame.math import Vector2


class Hitbox:
    def __init__(self, size: tuple, position: Vector2 = Vector2(0, 0)):
        """
        Although the Rect class already has a position attribute, this is
        rounded to an integer. If we want to simulate smooth movement we need
        to update a position vector that takes any real value.
        """
        self.position = position
        self.rectangle = Rect(self.position, size)
        self.offset = Vector2(0, 0)
        self.image = None

    def has_collided(self, other_rects):
        if self.rectangle.collidelist(other_rects) == -1:
            return False
        else:
            return True

    def get_offset(self, other_rect):
        """
        Gets the Rect offset between the hitbox rectangle and another
        reference rectangle when they are centered. The coordinates are rounded
        to the closest integer
        """
        self.offset = Vector2(
            tuple(
                (p2 - p1) // 2 for p1, p2 in zip(self.rectangle.size, other_rect.size)
            )
        )

    def set_position(self, position):
        self.position = position
        self.rectangle.topleft = self.position + self.offset


class SwordHitbox:
    """
    Implements two hitboxes (vertical and horizontal) for the sword attack
    """
    def __init__(self, depth, slash_range, position: Vector2 = Vector2(0, 0)):
        self.depth = depth
        self.range = slash_range
        self.position = 0
        self.horizontal = Rect(self.position, (slash_range, depth))
        self.vertical = Rect(self.position, (depth, slash_range))
        self.offset = Vector2(0, 0)
        self.image = None

