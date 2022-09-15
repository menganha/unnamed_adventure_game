from enum import Enum, auto

import pygame

from yazelc import components as cmp
from yazelc import zesper


class CollectableItemType(Enum):
    COIN = auto()
    HEART = auto()
    BOMB = auto()
    ARROW = auto()
    KEY = auto()


def create_entity(item_type: CollectableItemType, image: pygame.Surface, pos_x: int, pos_y: int, world: zesper.World) -> int:
    ent_id = world.create_entity()
    world.add_component(ent_id, cmp.Position(pos_x, pos_y))
    world.add_component(ent_id, cmp.Renderable(image))
    world.add_component(ent_id, cmp.Collectable(item_type))
    world.add_component(ent_id, cmp.HitBox(pos_x, pos_y, image.get_width(), image.get_height()))
    return ent_id
