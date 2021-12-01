from typing import Dict

import esper
import pygame

from yazelc import event_manager
from yazelc import hud
from yazelc.event_type import EventType


class HUDSystem(esper.Processor):
    """ Checks if the inventory/health and status has changed and changes the HUD accordingly """

    def __init__(self, hud_image: pygame.Surface, player_entity_id: int, cached_values: Dict[str, object]):
        self.hud_image = hud_image
        self.player_entity_id = player_entity_id
        self.cache_values = cached_values
        event_manager.subscribe(EventType.HUD_UPDATE, self.on_hud_update)

    def process(self):
        hud_values = hud.get_hud_dependant_values(self.player_entity_id, self.world)
        for variable in hud_values:
            if self.cache_values[variable] != hud_values[variable]:
                self.on_hud_update()
                self.cache_values[variable] = hud_values[variable]

    def on_hud_update(self):
        self.hud_image = hud.create_hud_image(self.player_entity_id, self.world)
