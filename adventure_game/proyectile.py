import pygame
from pygame.math import Vector2
from adventure_game import config as cfg
from adventure_game.hitbox import Hitbox
# TODO: Think about not having to load again and again the arrow image.

class Proyectile(pygame.sprite.Sprite):
    def __init__(self, position: tuple, velocity: Vector2, direction, proyectile_container):
        super().__init__()
        self.position = Vector2(position)
        self.velocity = velocity
        self.image = self.load_image_aligned_with_direction(direction)
        self.rect = self.image.get_rect()
        self.hitbox = Hitbox((16, 16), self.rect.center)
        self.container = proyectile_container
        self.container.add(self)

    @staticmethod
    def load_image_aligned_with_direction(direction):
        image = pygame.image.load('assets/sprites/arrow.png').convert_alpha()
        if direction == 0:
            image =  pygame.transform.rotate(image, 270)
        elif direction == 1:
            image =  pygame.transform.flip(image, True, False)
        elif direction == 2:
            image =  pygame.transform.rotate(image, 90)
        return image


    def update(self, delta, physical_objects):
        self.position.update(self.position + (delta * self.velocity).elementwise()**3)
        self.rect.center = self.position
        self.hitbox.rectangle.center = self.position
        if self.out_ouf_bounds() or self.hitbox.has_collided(physical_objects):
            self.remove(self.container)

    def out_ouf_bounds(self):
        return (
            self.position.x > cfg.DIS_WIDTH
            or self.position.x < 0
            or self.position.y > cfg.DIS_HEIGHT
            or self.position.y < 0
        )
