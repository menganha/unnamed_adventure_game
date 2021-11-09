import esper

import unnamed_adventure_game.components as cmp
from unnamed_adventure_game import event_manager
from unnamed_adventure_game import scenes
from unnamed_adventure_game.event_type import EventType
from unnamed_adventure_game.utils.esper import try_signature


class TransitionSystem(esper.Processor):

    def __init__(self, player_entity: int, current_scene: scenes.BaseScene):
        super().__init__()
        self.player_entity = player_entity
        self.current_scene = current_scene
        event_manager.subscribe(EventType.COLLISION, self.on_collision)

    def process(self):
        pass

    def on_collision(self, ent1: int, ent2: int):

        if not (component := try_signature(self.world, ent1, ent2, cmp.Door)):
            return
        ent_door, door, player_ent = component
        if player_ent != self.player_entity:  # Check if the other entity is the players
            return
        self.current_scene.in_scene = False
        player_components = self.world.components_for_entity(player_ent)
        next_scene_class = getattr(scenes, door.dest_scene)
        self.current_scene.next_scene = next_scene_class(self.current_scene.window, door.dest_x, door.dest_y, player_components)