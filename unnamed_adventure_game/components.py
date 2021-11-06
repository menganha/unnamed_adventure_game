from dataclasses import dataclass as component
from dataclasses import field, InitVar
from typing import Dict

import pygame

from unnamed_adventure_game.animation_stripe import AnimationStripe
from unnamed_adventure_game.utils.game import Direction, Status


@component
class Position:
    x: int = 0
    y: int = 0


@component
class Velocity:
    x: float = 0.0
    y: float = 0.0


@component
class State:
    """ State of being (usually a "moving" entity) used in different systems """
    direction: Direction = Direction.SOUTH
    status: Status = Status.IDLE


@component
class Renderable:
    image: pygame.Surface
    depth: int = 100
    width: int = field(init=False)
    height: int = field(init=False)

    def __post_init__(self):
        self.width = self.image.get_width()
        self.height = self.image.get_height()


@component
class WallTag:
    """ Tag to keep track of collidable walls"""
    pass


@component
class Health:
    points: int = 10
    cool_down_frames: int = 20  # frame of invincibility
    cool_down_counter: int = field(init=False, default=0)


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
    block_counter: int = field(init=False, default=0)


@component
class EnemyTag:
    """ Tags enemies and represent the value when colliding with them """
    pass


@component
class Weapon:
    damage: int = 5
    active_frames: int = 20  # -1 means is infinite
    freeze_frames: int = 0  # frames of input blocked when hit
    recoil_velocity: int = 0  # frames of input blocked when hit


@component
class Animation:
    """
    Needs at least to get one animation stripe (idle_down) to instantiate this component.
    No need of "left" animation stripe as we just flip the "right" one
    """
    strips: Dict[Status, Dict[Direction, AnimationStripe]] = field(init=False)

    idle_down: InitVar[AnimationStripe]
    idle_up: InitVar[AnimationStripe] = None
    idle_left: InitVar[AnimationStripe] = None

    move_down: InitVar[AnimationStripe] = None
    move_up: InitVar[AnimationStripe] = None
    move_left: InitVar[AnimationStripe] = None

    attack_down: InitVar[AnimationStripe] = None
    attack_up: InitVar[AnimationStripe] = None
    attack_left: InitVar[AnimationStripe] = None

    def __post_init__(self,
                      idle_down: AnimationStripe, idle_up: AnimationStripe, idle_left: AnimationStripe,
                      move_down: AnimationStripe, move_up: AnimationStripe, move_left: AnimationStripe,
                      attack_down: AnimationStripe, attack_up: AnimationStripe, attack_left: AnimationStripe):

        idle_right = move_right = attack_right = None
        if idle_left:
            idle_right = AnimationStripe.get_flipped_stripe(idle_left, flip_x=True, flip_y=False)
        if move_left:
            move_right = AnimationStripe.get_flipped_stripe(move_left, flip_x=True, flip_y=False)
        if attack_left:
            attack_right = AnimationStripe.get_flipped_stripe(attack_left, flip_x=True, flip_y=False)

        self.strips = {
            Status.IDLE: {Direction.NORTH: idle_up, Direction.WEST: idle_left,
                          Direction.SOUTH: idle_down, Direction.EAST: idle_right},
            Status.MOVING: {Direction.NORTH: move_up, Direction.WEST: move_left,
                            Direction.SOUTH: move_down, Direction.EAST: move_right},
            Status.ATTACKING: {Direction.NORTH: attack_up, Direction.WEST: attack_left,
                               Direction.SOUTH: attack_down, Direction.EAST: attack_right}
        }


@component
class Door:
    dest_scene: str
    dest_x: int
    dest_y: int
