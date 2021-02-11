from typing import List, Tuple

import pygame
from pygame.math import Vector2

from adventure_game import config as cfg
from adventure_game.direction import Direction
from adventure_game.enemy import Enemy
from adventure_game.hitbox import Hitbox


class Arrow(pygame.sprite.Sprite):
    PROYECTILE_VELOCITY = 100

    def __init__(self, position: Tuple[int, int], direction: Direction, raw_image: pygame.Surface):
        super().__init__()
        self.position = Vector2(position)
        self.velocity = self.PROYECTILE_VELOCITY * direction.value
        self.direction = direction
        self.image = self._align_image_with_direction(direction, raw_image)
        self.rect = self.image.get_rect()
        self.hitbox = Hitbox(self.rect)

    def update(self, delta: float, physical_obstacles: List[pygame.Rect]):
        self.position.update(self.position + (delta * self.velocity).elementwise() ** 3)
        self.rect.center = self.position
        self.hitbox.rect.center = self.position
        if self.is_out_ouf_bounds() or self.hitbox.has_collided_with_rects(*physical_obstacles):
            self.kill()

    def has_hit(self, enemy: Enemy):
        if self.hitbox.has_collided_with(enemy.hitbox):
            return True

    def is_out_ouf_bounds(self) -> bool:
        return (self.position.x > cfg.DIS_WIDTH
                or self.position.x < 0
                or self.position.y > cfg.DIS_HEIGHT
                or self.position.y < 0)

    @staticmethod
    def _align_image_with_direction(direction: Direction, raw_image: pygame.Surface) -> pygame.Surface:
        """
        Considers the the direction of the raw projectile image is to the right
        """
        if direction == Direction.DOWN:
            image = pygame.transform.rotate(raw_image, 270)
        elif direction == Direction.LEFT:
            image = pygame.transform.flip(raw_image, True, False)
        elif direction == Direction.UP:
            image = pygame.transform.rotate(raw_image, 90)
        else:
            image = raw_image
        return image
