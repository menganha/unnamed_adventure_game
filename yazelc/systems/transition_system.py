from __future__ import annotations

from typing import TYPE_CHECKING

from yazelc import components as cmp
from yazelc import event_manager
from yazelc import zesper
from yazelc.event_type import EventType

if TYPE_CHECKING:
    from yazelc.scenes.gameplay_scene import GameplayScene


# TODO: Fix bug where enemies can go through doors since there are no solid hitboxes preventing movement
class TransitionSystem(zesper.Processor):
    """ Transition between gameplay scenes """

    def __init__(self, current_scene: GameplayScene):
        super().__init__()
        self.current_scene = current_scene
        event_manager.subscribe(EventType.COLLISION, self.on_collision)

    def process(self):
        pass

    def on_collision(self, ent1: int, ent2: int):

        if not (component := self.world.try_signature(ent1, ent2, cmp.Door)):
            return
        ent_door, door, player_ent = component
        if player_ent != self.world.player_entity_id:  # Check if the other entity is the players
            return
        self.current_scene.in_scene = False
        player_components = self.world.components_for_entity(player_ent)
        current_scene_class = type(self.current_scene)
        self.current_scene.next_scene = current_scene_class(self.current_scene.window, door.target_map,
                                                            door.target_x, door.target_y, player_components)
