import pygame
from pygame.math import Vector2

from adventure_game.config import RED_T


class Hitbox:
    """
    Hitbox for a sprite. It takes the parent rectangle of the sprite plus the pixels that can be added or removed t
    to make the hitbox larger or smaller with respect to that sprite
    """

    def __init__(self, parent_rect: pygame.Rect, x_inflation: int = 0, y_inflation: int = 0):
        self.rect = parent_rect.inflate(x_inflation, y_inflation)
        self.offset = Vector2()
        self.image = None
        self._set_offset_with_rect(parent_rect)
        self._set_image(RED_T)

    def has_collided_with_rects(self, *other_rects: pygame.Rect):
        if self.rect.collidelist(other_rects) == -1:
            return False
        else:
            return True

    def has_collided_with(self, *other_hitboxes: 'Hitbox'):
        if self.rect.collidelist([hitbox.rect for hitbox in other_hitboxes]) == -1:
            return False
        else:
            return True

    def _set_offset_with_rect(self, other_rectangle: pygame.Rect):
        offset_tuple = [p1 - p2 for p1, p2 in zip(self.rect.center, other_rectangle.center)]
        self.offset = Vector2(offset_tuple)

    def move_with_respect_to_parent(self, position):
        self.rect.center = position + self.offset

    def _set_image(self, color):
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(color)
        self.image.set_alpha(100)
