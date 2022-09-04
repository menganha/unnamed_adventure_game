from dataclasses import dataclass as component
from dataclasses import field, InitVar
from typing import Dict, Callable, List, Optional, Tuple, Any

import pygame

from yazelc.animation import AnimationStrip, flip_strip_sprites
from yazelc.font import Font
from yazelc.items import ItemType
from yazelc.utils.game_utils import Direction, Status


@component
class Vector:
    x: float = 0.0
    y: float = 0.0


@component
class Position(Vector):
    prev_x: float = field(init=False)
    prev_y: float = field(init=False)

    def __post_init__(self):
        self.prev_x = self.x
        self.prev_y = self.y


@component
class Velocity(Vector):
    pass


@component
class Dialog:
    """ Used for dialogs or signs in game """
    text: str
    font: Font
    index: int = 0  # Index of the char at which the rendered text is actually in
    index_start: int = 0
    x_pos: int = 0
    y_pos: int = 0
    idle: bool = True  # If the text has not been displayed fully yet is waiting to be printed
    frame_tick: int = 0  # Tick integer that count the amount of frames between printing a char
    frame_delay: int = 1  # How many frames to wait until the next letter printing

    def next_char(self) -> str:
        return self.text[self.index]

    def is_at_end(self) -> bool:
        return self.index >= len(self.text)

    def current_sentence(self) -> str:
        """ Gives the sentence until the word (including it) at which the index is """
        sentence = self.text[self.index_start:self.index + 1]
        n_words = len(sentence.rstrip().split(' '))
        words = self.text[self.index_start:].split(' ')[:n_words]
        return ' '.join(words)


@component
class InteractorTag:
    """ Tag single entity with Hitbox to signal the player interacting with colliding object """
    pass


@component
class Renderable:
    image: pygame.Surface
    depth: int = 100  # Depth is just over the background, i.e., background = 0, foreground, 1000, foreforeground = 2000
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
class Menu:
    title: str
    items: list[str]
    font: Font
    item_idx_x: int = 0
    item_idx_y: int = 0

    def __len__(self):
        return len(self.items)


@component
class VisualEffect:
    color: pygame.Color


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
class Brain:
    """ Brain given to an NPC character / Enemy AI"""
    direction: Direction = Direction.SOUTH
    think_frames: int = 0  # amount of frames it takes to take a new decision
    think_counter: int = field(init=False, default=0)


@component
class Pickable:
    """ Pickable items tag """
    item_type: ItemType


@component
class Input:
    handle_input_function: Callable
    block_counter: int = 0
    is_paused: bool = False


@component
class EnemyTag:
    """ Tags enemies and represent the value when colliding with them """
    pass


@component
class Weapon:
    damage: int = 5
    active_frames: int = 20  # -1 means is infinite
    freeze_frames: int = 0  # frames of input blocked when hit
    recoil_velocity: int = 0


@component
class Script:
    """ Calls a function with the parent entity ID passed as an argument """
    function: Callable[..., None]
    args: Tuple[Any, ...]
    delay: int


# @component
# class Action:
#     function: Callable[..., None]
#     args: Tuple[Any, ...]
#
#
# @component
# class Script:
#     """ Calls a function with the parent entity ID passed as an argument """
#     action_list: List[Action]
#     delay: int = 0


@component
class Door:
    target_map: str
    target_x: int
    target_y: int


@component
class Animation:
    """
    Needs at least to get one animation stripe (idle_down) to instantiate this component. No need of "left" animation
    stripe as we can just "flip" the right one
    """
    idle_down: InitVar[AnimationStrip]
    idle_up: InitVar[Optional[AnimationStrip]] = None
    idle_right: InitVar[Optional[AnimationStrip]] = None

    move_down: InitVar[Optional[AnimationStrip]] = None
    move_up: InitVar[Optional[AnimationStrip]] = None
    move_right: InitVar[Optional[AnimationStrip]] = None

    attack_down: InitVar[Optional[AnimationStrip]] = None
    attack_up: InitVar[Optional[AnimationStrip]] = None
    attack_right: InitVar[Optional[AnimationStrip]] = None

    direction: Direction = Direction.SOUTH
    status: Status = Status.IDLE

    index: int = field(init=False, default=0)
    frame_counter: int = field(init=False, default=0)
    strips: Dict[Status, Dict[Direction, List[AnimationStrip]]] = field(init=False)

    previous_direction: Direction = field(init=False)
    previous_status: Status = field(init=False)

    def __post_init__(self, idle_down, idle_up, idle_right, move_down, move_up, move_right, attack_down, attack_up, attack_right):
        """
        Creates a dictionary with the as values images surfaces and the states as keys
        """
        self.previous_direction = self.direction
        self.previous_status = self.status

        idle_left = move_left = attack_left = None
        if idle_right:
            idle_left = flip_strip_sprites(idle_right)
        if move_right:
            move_left = flip_strip_sprites(move_right)
        if attack_right:
            attack_left = flip_strip_sprites(attack_right, reverse_order=False)  # May not be in general the situation

        self.strips = {
            Status.IDLE: {Direction.NORTH: idle_up, Direction.WEST: idle_left,
                          Direction.SOUTH: idle_down, Direction.EAST: idle_right},
            Status.MOVING: {Direction.NORTH: move_up, Direction.WEST: move_left,
                            Direction.SOUTH: move_down, Direction.EAST: move_right},
            Status.ATTACKING: {Direction.NORTH: attack_up, Direction.WEST: attack_left,
                               Direction.SOUTH: attack_down, Direction.EAST: attack_right}
        }

        # Remove the empty strips from the dict
        for status in (Status.IDLE, Status.MOVING, Status.ATTACKING):
            for direction in (Direction.NORTH, Direction.SOUTH, Direction.WEST, Direction.EAST):
                if self.strips[status][direction] is None:
                    del self.strips[status][direction]
