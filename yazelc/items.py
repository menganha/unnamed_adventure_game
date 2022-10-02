from enum import Enum

import pygame

from yazelc import components as cmp
from yazelc import zesper

COIN_TILE_SIZE = 16
COIN_ANIMATION_FRAME_DELAY = 4


class CollectableItemType(Enum):
    COIN = 0
    HEART = 1
    BOMB = 2
    ARROW = 3
    KEY = 4


def create_entity(item_type: CollectableItemType, pos_x: int, pos_y: int, world: zesper.World) -> int:
    ent_id = world.create_entity()
    images = get_images(world, item_type)
    if len(images) > 1:
        world.add_component(ent_id, cmp.Animation(images, COIN_ANIMATION_FRAME_DELAY))  # TODO: only works for coins now
    world.add_component(ent_id, cmp.Renderable(images[0]))
    world.add_component(ent_id, cmp.Position(pos_x, pos_y))
    world.add_component(ent_id, cmp.Collectable(item_type))
    world.add_component(ent_id, cmp.HitBox(pos_x, pos_y, images[0].get_width(), images[0].get_height()))
    return ent_id


def get_images(world: zesper.World, item_type: CollectableItemType) -> list[pygame.Surface]:
    if item_type == CollectableItemType.COIN:
        images = world.resource_manager.get_animation_strip(CollectableItemType.COIN.name)
    else:
        image = world.resource_manager.get_texture(item_type.name)
        images = [image]
    return images
