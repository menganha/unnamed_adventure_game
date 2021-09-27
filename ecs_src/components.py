import pygame
from dataclasses import dataclass as component
from dataclasses import field


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
class HitBox:
    rect: pygame.Rect
