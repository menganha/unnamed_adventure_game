from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass as component
from dataclasses import field
from typing import TYPE_CHECKING

import pygame

from yazelc.font import Font
from yazelc.items import CollectableItemType
from yazelc.utils.game_utils import Direction

if TYPE_CHECKING:
    from yazelc.systems.input_system import InputMessage

Vector = pygame.Vector2
Velocity = pygame.Vector2


class Position(pygame.Vector2):
    """
    Absolute position of the entity, i.e., not the one relative to the window unless the absolute
    flag is on. This one is used for entities that should be on the screen no matter where the
    camera is positioned
    """

    def __init__(self, x: float, y: float, absolute: bool = False):
        super().__init__(x, y)
        self.absolute = absolute
        self.prev_x: float = x
        self.prev_y: float = y


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
    """ Tag entity with Hitbox to signal the player interacting with colliding object """
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


# @component
class HitBox(pygame.Rect):
    """
    Pygame is made such that hitboxes contain also a position. Therefore, is difficult to separate the components, i.e.,
    Position and a "Hitbox" component in a "clean way".
    We have opted for the approach where the Hitbox has a position embedded in the component but does not count as a
    real Position component. Nevertheless, this internal position of the Hitbox also represent the absolute position of
    it.
    """

    def __init__(self, x_pos: int, y_pos: int, width: int, height: int, impenetrable: bool = False):
        super().__init__(x_pos, y_pos, width, height)
        self.impenetrable = impenetrable

    def move(self, x: int, y: int) -> 'HitBox':
        new_hitbox = super().move(x, y)
        print(type(new_hitbox))
        new_hitbox.impenetrable = self.impenetrable
        return new_hitbox


@component
class Brain:
    """ Brain given to an NPC character / Enemy AI"""
    # direction: Direction = Direction.DOWN
    think_frames: int = 0  # amount of frames it takes to take a new decision
    think_counter: int = field(init=False, default=0)


@component
class Collectable:
    """ Collectable items tag """
    item_type: CollectableItemType
    value: int = 1
    in_chest: bool = False


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
class Input:
    handle_input_function: Callable[[InputMessage]]
    block_counter: int = 0
    is_paused: bool = False


@component
class Door:
    target_map: str
    target_x: int
    target_y: int


@component
class State:
    """ Helper component for general state of objects """

    status: State
    direction: Direction
    prev_status: State = field(init=False)
    prev_direction: Direction = field(init=False)

    def __post_init__(self):
        self.refresh()

    def refresh(self):
        self.prev_status = self.status
        self.prev_direction = self.direction

    def has_changed(self) -> bool:
        return self.prev_direction != self.direction or self.prev_status != self.status


@component
class Animation:
    strip: list[pygame.Surface]
    delay: int
    frame_sequence: list[int] = None
    index: int = 0
    frame_counter: int = 0
    one_loop: bool = False

    def __post_init__(self):
        if self.frame_sequence is None:
            self.frame_sequence = [idx for idx in range(len(self.strip)) for _ in range(self.delay)]
