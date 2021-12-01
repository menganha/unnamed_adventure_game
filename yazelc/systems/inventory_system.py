import esper

from yazelc import components as cmp
from yazelc import event_manager
from yazelc import player
from yazelc.event_type import EventType
from yazelc.items import ItemType
from yazelc.utils.esper_utils import try_signature


class InventorySystem(esper.Processor):

    def __init__(self, player_entity_id: int):
        super().__init__()
        self.player_entity_id = player_entity_id
        event_manager.subscribe(EventType.COLLISION, self.on_collision)

    def process(self):
        pass

    def on_collision(self, ent1: int, ent2: int):

        if not (component := try_signature(self.world, ent1, ent2, cmp.Pickable)):
            return
        pickable_ent, pickable, player_ent = component
        if player_ent != self.player_entity_id:  # Check if the other entity is the players
            return

        if pickable.item_type == ItemType.HEART:
            health = self.world.component_for_entity(player_ent, cmp.Health)
            health.points = min(player.MAX_HEALTH, health.points + 1)
        else:
            player.INVENTORY[pickable.item_type] += 1

        self.world.delete_entity(pickable_ent)
