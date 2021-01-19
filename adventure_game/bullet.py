import pygame
from pygame.math import Vector2
from adventure_game import config as cfg


class Bullet:
    def __init__(self, position: tuple, velocity: Vector2, size, bullet_container):
        self.position = Vector2(position)
        self.velocity = velocity
        self.size = size
        self.bullet_container = bullet_container
        self.bullet_container.add(self)

    def update(self, delta):
        self.position.update(self.position + (delta * self.velocity).elementwise()**2)

    def draw(self, display):
        pygame.draw.circle(display, cfg.WHITE, self.position, self.size)

    def out_ouf_bounds(self):
        return (
            self.position.x > cfg.DIS_WIDTH
            or self.position.x < 0
            or self.position.y > cfg.DIS_HEIGHT
            or self.position.y < 0
        )


class BulletContainer:
    def __init__(self):
        self.group = {}

    def add(self, bullet: Bullet):
        self.group.update({id(bullet): bullet})

    def kill(self, bullet: Bullet):
        del self.group[id(bullet)]

    def update(self, delta):
        self.group = {identity: bullet for identity, bullet in self.group.items() if not bullet.out_ouf_bounds()}
        for bullet in self.group.values():
            bullet.update(delta)

    def draw(self, display):
        for bullet in self.group.values():
            bullet.draw(display)

    def __iter__(self):
        return iter(list(self.group))
