import esper

import yazelc.components as cmp
from yazelc import event_manager
from yazelc.event_type import EventType
from yazelc.scenes.base_scene import BaseScene
from yazelc.utils.esper import try_signature


class TransitionSystem(esper.Processor):

    def __init__(self, current_scene: BaseScene):
        super().__init__()
        self.current_scene = current_scene
        event_manager.subscribe(EventType.COLLISION, self.on_collision)

    def process(self):
        pass

    def on_collision(self, ent1: int, ent2: int):

        if not (component := try_signature(self.world, ent1, ent2, cmp.Door)):
            return
        ent_door, door, player_ent = component
        if player_ent != self.current_scene.PLAYER_ENTITY:  # Check if the other entity is the players
            return
        self.current_scene.in_scene = False
        player_components = self.world.components_for_entity(player_ent)
        next_scene_class = getattr(scenes, door.target_scene)
        self.current_scene.next_scene = next_scene_class(self.current_scene.window, door.target_x, door.target_y, player_components)
