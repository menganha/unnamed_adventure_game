from typing import Dict

import pygame

from yazelc import config as cfg
from yazelc import resource_manager
from yazelc import zesper
from yazelc.components import Vector, Renderable, Position, Health
from yazelc.player import player

WHOLE_HEART_HEALTH_POINTS = 2
HUD_DEPTH = 1001
HUD_WIDTH = cfg.RESOLUTION.x
HUD_HEIGHT = 40
FULL_HEART_RESOURCE_NAME = 'full_heart'
HALF_HEART_RESOURCE_NAME = 'half_heart'
EMPTY_HEART_RESOURCE_NAME = 'empty_heart'

HEART_OFFSET = Vector(2, 2)


def create_hud_entity(world: zesper.World):
    hud_entity_id = world.create_entity()
    world.hud_entity_id = hud_entity_id
    hud_surface = pygame.surface.Surface((HUD_WIDTH, HUD_HEIGHT), flags=pygame.SRCALPHA)
    world.add_component(hud_entity_id, Position(0, 0))
    world.add_component(hud_entity_id, Renderable(hud_surface, depth=HUD_DEPTH))
    dictionary = get_hud_dependant_values(world)
    update_hud_entity(world, **dictionary)


def update_hud_entity(world: zesper.World, **kwargs):
    hud_image = world.component_for_entity(world.hud_entity_id, Renderable).image
    # TODO: Is it necessary to clear the image before?

    full_heart_image = resource_manager.get_resource(FULL_HEART_RESOURCE_NAME)
    half_heart_image = resource_manager.get_resource(HALF_HEART_RESOURCE_NAME)
    empty_heart_image = resource_manager.get_resource(EMPTY_HEART_RESOURCE_NAME)

    num_whole_hearts, num_medium_hearts = divmod(kwargs['health_points'], WHOLE_HEART_HEALTH_POINTS)
    index = 0
    for idx in range(num_whole_hearts):
        hud_image.blit(full_heart_image, (idx * full_heart_image.get_width() + HEART_OFFSET.x, HEART_OFFSET.y))
        index += 1
    for idx in range(num_medium_hearts):
        hud_image.blit(half_heart_image, (index * half_heart_image.get_width() + HEART_OFFSET.x, HEART_OFFSET.y))
        index += 1
    for idx in range(player.MAX_HEALTH // 2 - num_medium_hearts - num_whole_hearts):
        hud_image.blit(empty_heart_image, (index * empty_heart_image.get_width() + HEART_OFFSET.x, HEART_OFFSET.y))
        index += 1


def get_hud_dependant_values(world: zesper.World) -> Dict[str, object]:  # TODO: Should I make the keys some sort of type/class?
    dictionary = {
        'health_points': world.component_for_entity(world.player_entity_id, Health).points
    }
    return dictionary
