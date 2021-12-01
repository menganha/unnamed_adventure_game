from pathlib import Path
from typing import Dict

import esper
import pygame

from yazelc import components as cmp
from yazelc import config as cfg

WHOLE_HEART_HEALTH_POINTS = 2
HUD_HEIGHT = 40


# TODO: Pattern seems to suggest that these functions may adapt better to a class since, e.g., the heart surface
#   and really the whole hud surface may be constant which has to be updated from time to time.

# TODO: Include half a heart image

def create_hud_image(player_entitity_id: int, world: esper.World) -> pygame.surface.Surface:
    # Creates the backaground surface
    hud_surface = pygame.surface.Surface((cfg.RESOLUTION[0], HUD_HEIGHT), flags=pygame.SRCALPHA)
    # Updates the heart count
    # TODO: very inefficient consider resources manager
    HEART_IMAGE = pygame.image.load(Path('assets', 'sprites', 'full_heart.png')).convert_alpha()
    health = world.component_for_entity(player_entitity_id, cmp.Health)
    # updates other aspects of the hud
    # ...
    num_whole_hearts, num_medium_hearts = divmod(health.points, WHOLE_HEART_HEALTH_POINTS)
    for idx in range(num_whole_hearts):
        hud_surface.blit(HEART_IMAGE, (idx * HEART_IMAGE.get_width(), 0))
    for idx in range(num_medium_hearts):
        hud_surface.blit(HEART_IMAGE, (idx * HEART_IMAGE.get_width(), 0))

    return hud_surface


def get_hud_dependant_values(player_entity_id: int, world: esper.World) -> Dict[str, object]:
    dictionary = {
        'health_points': world.component_for_entity(player_entity_id, cmp.Health).points
    }
    return dictionary
