from yazelc import hud
from yazelc import zesper
from yazelc.event.events import HudUpdateEvent
from yazelc.items import CollectableItemType


class HudSystem(zesper.Processor):
    def __init__(self, hud_entity_id):
        super().__init__()
        self.hud_entity_id = hud_entity_id

    def process(self):
        pass

    def on_hud_update(self, hud_update_event: HudUpdateEvent):
        if hud_update_event.pickable_item_type == CollectableItemType.HEART:
            hud.update_hud_hearts(self.hud_entity_id, hud_update_event.value, self.world)
        # Add here more conditions
