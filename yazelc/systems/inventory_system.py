from yazelc import components as cmp
from yazelc import event_manager
from yazelc import zesper
from yazelc.event_type import EventType
from yazelc.items import ItemType
from yazelc.player import player


class InventorySystem(zesper.Processor):

    def __init__(self):
        super().__init__()
        event_manager.subscribe(EventType.COLLISION, self.on_collision)

    def process(self):
        pass

    def on_collision(self, ent1: int, ent2: int):

        if not (component := self.world.try_signature(ent1, ent2, cmp.Pickable)):
            return
        pickable_ent, pickable, player_ent = component
        if player_ent != self.world.player_entity_id:  # Check if the other entity is the players
            return

        if pickable.item_type == ItemType.HEART:
            health = self.world.component_for_entity(player_ent, cmp.Health)
            health.points = min(player.MAX_HEALTH, health.points + 1)
            event_manager.post_event(EventType.HUD_UPDATE)
        else:
            player.INVENTORY[pickable.item_type] += 1

        self.world.delete_entity(pickable_ent)
