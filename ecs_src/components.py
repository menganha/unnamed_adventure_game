import pygame
from dataclasses import dataclass as component
from dataclasses import field, InitVar


@component
class Velocity:
    x: float = 0.0
    y: float = 0.0


@component
class Renderable:
    image: pygame.Surface
    depth: int = 0
    w: int = field(init=False)
    h: int = field(init=False)

    def __post_init__(self):
        self.w = self.image.get_width()
        self.h = self.image.get_height()


@component
class Position:
    x: int = 0
    y: int = 0


@component
class Life:
    value: int = 10


@component
class HitBox:
    x_pos: InitVar[int]
    y_pos: InitVar[int]
    width: InitVar[int]
    height: InitVar[int]
    rect: pygame.Rect = field(init=False)

    def __post_init__(self, x_pos: int, y_pos: int, width: int, height: int):
        self.rect = pygame.Rect(x_pos, y_pos, width, height)
