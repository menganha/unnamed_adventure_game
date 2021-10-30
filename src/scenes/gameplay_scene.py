from abc import abstractmethod

import components as cmp
import config as cfg
import entity_fabric as fabric
import systems as sys
from component_utils import position_of_unscaled_rect
from maps import Maps
from scenes import BaseScene


class GameplayScene(BaseScene):

    @property
    @abstractmethod
    def map_data_file(self):
        pass

    def on_enter(self):
        # Add map entity
        overworld_map = Maps(self.map_data_file)
        for idx, map_layer in enumerate(overworld_map.create_map_image()):
            layer_entity = self.world.create_entity()
            self.world.add_component(layer_entity, cmp.Position(x=0, y=0))
            depth = 1000 * (idx - 1)
            self.world.add_component(layer_entity, cmp.Renderable(image=map_layer, depth=depth))

        for position, hitbox, wall_tag in overworld_map.create_solid_rectangles():
            self.world.create_entity(position, hitbox, wall_tag)
        for door, hitbox in overworld_map.create_doors():
            self.world.create_entity(door, hitbox)

        # Add player entity
        player_x_pos, player_y_pos = overworld_map.get_center_coord_from_tile(self.start_tile_x_pos,
                                                                              self.start_tile_y_pos)
        if not self.player_entity:
            self.player_entity = fabric.create_player_at(center_x_pos=player_x_pos, center_y_pos=player_y_pos,
                                                         world=self.world)
        else:
            position = self.world.component_for_entity(self.player_entity, cmp.Position)
            velocity = self.world.component_for_entity(self.player_entity, cmp.Velocity)
            hitbox = self.world.component_for_entity(self.player_entity, cmp.HitBox)
            velocity.x, velocity.y = (0, 0)
            hitbox.rect.center = (player_x_pos, player_y_pos)
            position.x, position.y = position_of_unscaled_rect(hitbox)

        # Add camera entity
        camera_entity = self.world.create_entity()
        self.world.add_component(camera_entity, cmp.Position(x=0, y=0))

        # Create enemy
        fabric.create_jelly_at(400, 400, self.world)

        # Create some Processor instances, and assign them to be processed.
        input_processor = sys.InputSystem()
        physics_system = sys.CollisionWithSolidsSystem()
        render_processor = sys.RenderSystem(window=self.window, camera_entity=camera_entity)
        animation_system = sys.AnimationSystem()
        transition_system = sys.TransitionSystem(self.player_entity, self)
        movement_processor = sys.MovementSystem(min_x=0, max_x=cfg.RESOLUTION[0],
                                                min_y=0, max_y=cfg.RESOLUTION[1])
        camera_processor = sys.CameraSystem(camera_entity, entity_followed=self.player_entity)
        combat_system = sys.CombatSystem(player_entity=self.player_entity)
        self.world.add_processor(input_processor)
        self.world.add_processor(animation_system)
        self.world.add_processor(combat_system)
        self.world.add_processor(movement_processor)
        self.world.add_processor(transition_system)
        self.world.add_processor(physics_system)
        self.world.add_processor(camera_processor)
        self.world.add_processor(render_processor)

    def on_exit(self):
        pass
