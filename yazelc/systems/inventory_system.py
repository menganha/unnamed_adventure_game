from yazelc import components as cmp
from yazelc import event_manager
from yazelc import zesper
from yazelc.event_type import EventType
from yazelc.items import PickableItemType
from yazelc.player import player
from yazelc.player.inventory import Inventory


class InventorySystem(zesper.Processor):

    def __init__(self, player_entity_id: str, inventory: Inventory):
        self.player_entity_id = player_entity_id
        self.inventory = inventory
        event_manager.subscribe(EventType.COLLISION, self.on_collision)

    def process(self):
        pass

    def on_collision(self, ent1: int, ent2: int):

        if not (component := self.world.try_signature(ent1, ent2, cmp.Pickable)):
            return
        pickable_ent, pickable, player_ent = component

        # Check if the other entity is the players, i.e., no other enemy or moving entity with hitbox can pick up any pickable
        if player_ent != self.player_entity_id:
            return

        if pickable.item_type == PickableItemType.HEART:
            health = self.world.component_for_entity(player_ent, cmp.Health)
            health.points = min(player.MAX_HEALTH, health.points + pickable.value)
            value = health.points
        else:
            value = self.inventory.add_pickable(pickable)

        event_manager.post_event(EventType.HUD_UPDATE, pickable.item_type, value)
        self.world.delete_entity(pickable_ent)
