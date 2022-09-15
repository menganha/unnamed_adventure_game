from yazelc import zesper
from yazelc.components import Collectable
from yazelc.components import Health
from yazelc.event import CollisionEvent, HudUpdateEvent
from yazelc.items import CollectableItemType
from yazelc.player.player import MAX_HEALTH


class InventorySystem(zesper.Processor):
    def __init__(self, player_entity_id: int, inventory: dict[CollectableItemType, int]):
        super(InventorySystem, self).__init__()
        self.player_entity_id = player_entity_id
        self.inventory = inventory
        # Here we may include weapons, etc., perhaps some other stuff like how many levels one has passed, etc, i.e., the current
        # state of the player. Or perhaps we should include this in another instance??

    def process(self):
        pass

    def on_collision(self, collision_event: CollisionEvent):

        if not (component := self.world.try_signature(collision_event.ent_1, collision_event.ent_2, Collectable)):
            return
        collectable_ent_id, collectable, player_ent = component
        # Check if the other entity is the players, i.e., no other enemy or moving entity with hitbox can pick up any pickable
        if player_ent != self.player_entity_id:
            return
        if collectable.item_type == CollectableItemType.HEART:
            health = self.world.component_for_entity(player_ent, Health)
            health.points = min(MAX_HEALTH, health.points + collectable.value)
            value = health.points
        else:
            value = self._add_pickable(collectable)

        hud_update_event = HudUpdateEvent(collectable.item_type, value)
        self.events.append(hud_update_event)
        self.world.delete_entity(collectable_ent_id)

    def _add_pickable(self, pickable: Collectable) -> int:
        self.inventory[pickable.item_type] += pickable.value
        return self.inventory[pickable.item_type]
