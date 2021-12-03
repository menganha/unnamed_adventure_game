from typing import Dict

import esper

from yazelc import event_manager
from yazelc.components import Health
from yazelc.event_type import EventType
from yazelc.hud import HUD


class HUDSystem(esper.Processor):
    """ Checks if the inventory/health and status has changed and changes the HUD accordingly """

    def __init__(self, hud: HUD, player_entity_id: int):
        self.hud = hud
        self.player_entity_id = player_entity_id
        self.cache_values = None
        event_manager.subscribe(EventType.HUD_UPDATE, self.on_hud_update)

    def process(self):
        # If it's the first time processing the frame just initialize the cache values
        if self.cache_values is None:
            self.cache_values = self.get_hud_dependant_values()
            self.hud.update_surface(**self.cache_values)
            return
        hud_values = self.get_hud_dependant_values()
        for variable in hud_values:
            has_changed = False
            if self.cache_values[variable] != hud_values[variable]:
                self.cache_values[variable] = hud_values[variable]
                has_changed = True
            if has_changed:
                self.hud.update_surface(**hud_values)

    def get_hud_dependant_values(self) -> Dict[str, object]:  # TODO: Should I make the keys some sort of type/class?
        dictionary = {
            'health_points': self.world.component_for_entity(self.player_entity_id, Health).points
        }
        return dictionary

    def on_hud_update(self):  # TODO: Will this be necessary at some point?
        self.hud.update_surface(**self.get_hud_dependant_values())
