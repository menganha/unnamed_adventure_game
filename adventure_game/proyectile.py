import pygame
from pygame.math import Vector2

from adventure_game import config as cfg
from adventure_game.hitbox import Hitbox
from adventure_game.proyectile_container import ProyectileContainer
from adventure_game.direction import Direction


class Proyectile(pygame.sprite.Sprite):

    def __init__(self, position: tuple, direction: Direction, abs_velocity: int, container: ProyectileContainer):
        super().__init__()
        self.position = Vector2(position)
        self.velocity = abs_velocity * direction.value
        self.image = self._align_image_with_direction(direction, container.proyectile_image)
        self.rect = self.image.get_rect()
        self.hitbox = Hitbox((16, 16), self.rect.center)
        container.add(self)

    def update(self, delta: float, physical_objects):
        self.position.update(self.position + (delta * self.velocity).elementwise() ** 3)
        self.rect.center = self.position
        self.hitbox.rect.center = self.position
        if self.is_out_ouf_bounds() or self.hitbox.has_collided(physical_objects):
            self.kill()

    def is_out_ouf_bounds(self) -> bool:
        return (self.position.x > cfg.DIS_WIDTH
                or self.position.x < 0
                or self.position.y > cfg.DIS_HEIGHT
                or self.position.y < 0)

    @staticmethod
    def _align_image_with_direction(direction: Direction, raw_image: pygame.Surface) -> pygame.Surface:
        if direction == Direction.DOWN:
            image = pygame.transform.rotate(raw_image, 270)
        elif direction == Direction.LEFT:
            image = pygame.transform.flip(raw_image, True, False)
        elif direction == Direction.UP:
            image = pygame.transform.rotate(raw_image, 90)
        else:
            image = raw_image
        return image
