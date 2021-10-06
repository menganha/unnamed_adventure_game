from dataclasses import dataclass as component
from dataclasses import field, InitVar
from animation_stripe import AnimationStripe
from typing import Callable
from direction import Direction

import pygame


@component
class Velocity:
    x: float = 0.0
    y: float = 0.0


@component
class Renderable:
    image: pygame.Surface
    depth: int = 0
    width: int = field(init=False)
    height: int = field(init=False)
    direction: Direction = Direction.SOUTH

    def __post_init__(self):
        self.width = self.image.get_width()
        self.height = self.image.get_height()


@component
class Position:
    x: int = 0
    y: int = 0


@component
class Health:
    points: int = 10


@component
class HitBox:
    x_pos: InitVar[int]
    y_pos: InitVar[int]
    width: InitVar[int]
    height: InitVar[int]
    scale_offset: int = 0
    rect: pygame.Rect = field(init=False)

    def __post_init__(self, x_pos: int, y_pos: int, width: int, height: int):
        self.rect = pygame.Rect(x_pos, y_pos, width, height)
        self.rect.inflate_ip(self.scale_offset, self.scale_offset)


@component
class Input:
    process: Callable[[int], None]  # Function on entity


@component
class MeleeWeapon:
    range_front: InitVar[int] = 16
    range_side: InitVar[int] = 16
    power: int = 5
    active_frames: int = 20
    offset: int = 0
    rect_h: pygame.Rect = field(init=False)  # Horizontal direction hitbox
    rect_v: pygame.Rect = field(init=False)  # Vertical direction hitbox
    frame_counter: int = field(init=False)  # If frame_counter == active_frames, the weapon is on idle

    def __post_init__(self, range_front: int, range_side: int):
        self.rect_h = pygame.Rect(0, 0, range_front, range_side)
        self.rect_v = pygame.Rect(0, 0, range_side, range_front)
        self.frame_counter = self.active_frames


@component
class Animation:
    """
    Needs at least to get one animation stripe (idle_down) to instantiate this component.
    No need of "left" animation stripe as we just flip the "right" one
    """
    idle_down: AnimationStripe
    idle_up: AnimationStripe = None
    idle_left: AnimationStripe = None
    idle_right: AnimationStripe = field(init=False)

    move_down: AnimationStripe = None
    move_up: AnimationStripe = None
    move_left: AnimationStripe = None
    move_right: AnimationStripe = field(init=False)

    attack_down: AnimationStripe = None
    attack_up: AnimationStripe = None
    attack_left: AnimationStripe = None
    attack_right: AnimationStripe = field(init=False)

    def __post_init__(self):
        if self.idle_left:
            self.idle_right = AnimationStripe.get_flipped_stripe(self.idle_left, flip_x=True, flip_y=False)
        if self.move_left:
            self.move_right = AnimationStripe.get_flipped_stripe(self.move_left, flip_x=True, flip_y=False)
        if self.attack_left:
            self.attack_right = AnimationStripe.get_flipped_stripe(self.attack_left, flip_x=True, flip_y=False)
