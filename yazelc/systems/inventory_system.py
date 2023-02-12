from event.event_manager import CollisionEvent, HudUpdateEvent
from yazelc import items
from yazelc import zesper
from yazelc.clock import Timer
from yazelc.components import Collectable, InteractorTag, Health, Animation, Renderable, Position, Velocity
from yazelc.player.player import MAX_HEALTH


class InventorySystem(zesper.Processor):
    TREASURE_TEXTURE_ID = 'TREASURE'
    TREASURE_TILE_SIZE = 16
    TREASURE_ANIMATION_DELAY = 5
    TREASURE_OBJECT_VELOCITY = -1
    TREASURE_OBJECT_LIFETIME = 15
    TREASURE_OBJECT_STOP_TIME = 5
    TREASURE_OBJECT_OFFSET = 5

    def __init__(self, player_entity_id: int, inventory: dict[items.CollectableItemType, int]):
        super(InventorySystem, self).__init__()
        self.player_entity_id = player_entity_id
        self.inventory = inventory
        # Here we may include weapons, etc., perhaps some other stuff like how many levels one has passed, etc, i.e., the current
        # state of the player. Or perhaps we should include this in another instance??

    def process(self):
        pass

    def on_collision(self, collision_event: CollisionEvent):

        # TODO: the collision system needs some rewrite as this checking of the collision doesn't seem right!
        if component := self.world.try_signature(collision_event.ent_1, collision_event.ent_2, Collectable):
            collectable_ent_id, collectable, player_ent = component
            # Check if the other entity is the players, i.e., no other enemy or moving entity with hitbox can pick up any pickable
            if player_ent == self.player_entity_id and not collectable.in_chest:
                self._add_pickable(collectable, self.player_entity_id)
                self.world.delete_entity(collectable_ent_id)

        if component := self.world.try_pair_signature(collision_event.ent_1, collision_event.ent_2, Collectable, InteractorTag):
            collectable_ent_id, collectable, interactor_entity, _ = component

            image_strip = self.world.resource_manager.get_animation_strip(self.TREASURE_TEXTURE_ID)
            animation = Animation(image_strip, delay=self.TREASURE_ANIMATION_DELAY, one_loop=True)
            renderable = Renderable(image_strip[0])
            self.world.add_component(collectable_ent_id, animation)
            self.world.add_component(collectable_ent_id, renderable)

            # Add animation of elevating item
            images = items.get_images(self.world, collectable.item_type)
            renderable = Renderable(images[0], depth=200)
            object_position = self.world.component_for_entity(collectable_ent_id, Position)
            position = Position(object_position.x, object_position.y - self.TREASURE_OBJECT_OFFSET)
            velocity = Velocity(0, self.TREASURE_OBJECT_VELOCITY)

            item_collected_entity = self.world.create_entity(velocity, position, renderable)

            # First script
            def stop_entity(entity: int):
                vel = self.world.component_for_entity(entity, Velocity)
                vel.y = 0

            delay = self.TREASURE_OBJECT_LIFETIME
            stop_entity_timer = Timer(delay, False, stop_entity, item_collected_entity)
            delay += self.TREASURE_OBJECT_LIFETIME
            delete_entity_timer = Timer(delay, False, self.world.delete_entity, item_collected_entity)
            self.timers.extend([stop_entity_timer, delete_entity_timer])

            self._add_pickable(collectable, self.player_entity_id)
            self.world.remove_component(collectable_ent_id, Collectable)
            # TODO: Make a pause here

    def _add_pickable(self, collectable: Collectable, player_ent: int):

        if collectable.item_type == items.CollectableItemType.HEART:
            health = self.world.component_for_entity(player_ent, Health)
            health.points = min(MAX_HEALTH, health.points + collectable.value)
            value = health.points
        else:
            self.inventory[collectable.item_type] += collectable.value
            value = self.inventory[collectable.item_type]

        hud_update_event = HudUpdateEvent(collectable.item_type, value)
        self.events.append(hud_update_event)
