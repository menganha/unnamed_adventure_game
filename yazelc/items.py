from enum import Enum, auto

import pygame

from yazelc import components as cmp
from yazelc import zesper


# noinspection PyArgumentList
class PickableItemType(Enum):
    COIN = auto()
    HEART = auto()
    BOMB = auto()
    ARROW = auto()
    KEY = auto()


def create_entity(item_type: PickableItemType, image: pygame.Surface, pos_x: int, pos_y: int, world: zesper.World) -> int:
    ent_id = world.create_entity()
    world.add_component(ent_id, cmp.Position(pos_x, pos_y))
    world.add_component(ent_id, cmp.Renderable(image))
    world.add_component(ent_id, cmp.Pickable(item_type))
    world.add_component(ent_id, cmp.HitBox(pos_x, pos_y, image.get_width(), image.get_height()))
    return ent_id
