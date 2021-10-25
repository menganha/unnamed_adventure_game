from dataclasses import dataclass as component
from dataclasses import field, InitVar

import pygame

from animation_stripe import AnimationStripe
from direction import Direction


@component
class Position:
    x: int = 0
    y: int = 0


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
class Health:
    points: int = 10
    cool_down_frames: int = 20
    frame_counter: int = field(init=False, default=0)


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

    def position_of_unscaled_rect(self) -> (int, int):
        x_pos = self.rect.x + int(self.scale_offset / 2)
        y_pos = self.rect.y + int(self.scale_offset / 2)
        return x_pos, y_pos


@component
class Input:
    # if != 0 it will block any input from being registered
    block_counter: int = field(init=False, default=0)


@component
class Enemy:
    """ Tags enemies an represent the value when hitting them """
    damage: int = 5


@component
class Weapon:
    range_front: int
    range_side: int
    offset: int
    damage: int = 5
    life_time: int = 20  # In frames. -1 means is infinite


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


@component
class Door:
    dest_scene: str
    dest_x: int
    dest_y: int
