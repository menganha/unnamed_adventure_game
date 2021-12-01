from enum import Enum, auto
from pathlib import Path

import esper
import pygame

from yazelc import components as cmp


class ItemType(Enum):
    COIN = auto()
    HEART = auto()
    BOMB = auto()
    ARROW = auto()


IMAGE_PATH = {
    ItemType.HEART: Path('assets', 'sprites', 'full_heart.png')}


def create_entity(item_type: ItemType, pos_x: int, pos_y: int, world: esper.World):
    ent_id = world.create_entity()
    ent_image = pygame.image.load(IMAGE_PATH[item_type]).convert_alpha()
    world.add_component(ent_id, cmp.Position(pos_x, pos_y))
    world.add_component(ent_id, cmp.Renderable(ent_image))
    world.add_component(ent_id, cmp.Pickable(ItemType.HEART))
    world.add_component(ent_id, cmp.HitBox(pos_x, pos_y, ent_image.get_width(), ent_image.get_height()))
