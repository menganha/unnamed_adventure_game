from yazelc import event_manager
from yazelc import hud
from yazelc import zesper
from yazelc.components import Position
from yazelc.event_type import EventType


class HUDSystem(zesper.Processor):
    """ Checks if the inventory/health and status has changed and changes the HUD accordingly """

    def __init__(self):
        event_manager.subscribe(EventType.HUD_UPDATE, self.on_hud_update)

    def process(self):
        # If it's the first time processing the frame just initialize the cache values
        position = self.world.component_for_entity(self.world.hud_entity_id, Position)
        camera_position = self.world.component_for_entity(self.world.camera_entity_id, Position)
        position.x, position.y = camera_position.x, camera_position.y

    def on_hud_update(self):
        hud_dependant_values = hud.get_hud_dependant_values(self.world)
        hud.update_hud_entity(self.world, **hud_dependant_values)
