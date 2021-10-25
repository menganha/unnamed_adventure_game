import components as cmp
import esper
import scenes
from scenes.base_scene import BaseScene


class TransitionSystem(esper.Processor):
    TRANSITION_AREA_PERCENTAGE = 0.7

    def __init__(self, player_entity: int, current_scene: BaseScene):
        super().__init__()
        self.player_entity = player_entity
        self.current_scene = current_scene

    def process(self):
        player_hitbox = self.world.component_for_entity(self.player_entity, cmp.HitBox)
        for ent, (hitbox, door) in self.world.get_components(cmp.HitBox, cmp.Door):
            cropped_rect = player_hitbox.rect.clip(hitbox.rect)
            # if cropped_rect.size == (0, 0):
            #     continue
            cropped_rect_area = cropped_rect.w * cropped_rect.h
            door_hitbox_area = hitbox.rect.w * hitbox.rect.h
            if cropped_rect_area > door_hitbox_area * self.TRANSITION_AREA_PERCENTAGE:
                self.current_scene.in_scene = False
                player_components = self.world.components_for_entity(self.player_entity)
                next_scene_class = getattr(scenes, door.dest_scene)
                self.current_scene.next_scene = next_scene_class(self.current_scene.window, door.dest_x, door.dest_y,
                                                                 player_components)
