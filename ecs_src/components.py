from dataclasses import dataclass as component
from dataclasses import field, InitVar
from typing import Callable

import pygame


@component
class Velocity:
    x: float = 0.0
    y: float = 0.0


@component
class Renderable:
    image: pygame.Surface
    depth: int = 0
    rect: pygame.Rect = field(init=False)

    def __post_init__(self):
        self.rect = self.image.get_rect()


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


@component
class Input:
    process: Callable[[int], None]  # Function on entity
