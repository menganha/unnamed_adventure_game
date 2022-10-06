from __future__ import annotations

from typing import TYPE_CHECKING

from yazelc import components as cmp
from yazelc import zesper
from yazelc.event import CollisionEvent

if TYPE_CHECKING:
    from yazelc.scenes.gameplay_scene import GameplayScene


# TODO: Fix bug where enemies can go through doors since there are no solid hitboxes preventing movement
# TODO: This system is unnecessary since it only defines one collision handling. Better accomodate this on the
#       gameplay class
class TransitionSystem(zesper.Processor):
    """ Transition between gameplay scenes """

    def __init__(self, current_scene: GameplayScene, player_entity_id: int):
        super().__init__()
        self.current_scene = current_scene
        self.player_entity_id = player_entity_id

    def process(self):
        pass

    def on_collision(self, collision_event: CollisionEvent):

        if component := self.world.try_signature(collision_event.ent_1, collision_event.ent_2, cmp.Door):
            ent_door, door, player_ent = component
            if player_ent != self.player_entity_id:  # Check if the other entity is the players
                return
            self.current_scene.in_scene = False
            player_components = self.world.components_for_entity(player_ent)
            current_scene_class = type(self.current_scene)
            self.current_scene.next_scene = current_scene_class(self.current_scene.window, door.target_map,
                                                                door.target_x, door.target_y, player_components)
