from abc import abstractmethod

import unnamed_adventure_game.components as cmp
import unnamed_adventure_game.config as cfg
import unnamed_adventure_game.entity_fabric as fabric
import unnamed_adventure_game.systems as sys
from unnamed_adventure_game.maps import Maps
from unnamed_adventure_game.scenes import BaseScene
from unnamed_adventure_game.utils.component import position_of_unscaled_rect


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
        # player_x_pos = 439
        # player_y_pos = 415
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

        # position = self.world.component_for_entity(self.player_entity, cmp.Position)
        # hitbox = self.world.component_for_entity(self.player_entity, cmp.HitBox)
        # position.x, position.y = player_x_pos, player_y_pos

        # Add camera entity
        camera_entity = self.world.create_entity()
        self.world.add_component(camera_entity, cmp.Position(x=0, y=0))

        # Create enemy
        fabric.create_jelly_at(400, 400, self.world)

        # Create the systems for the scene
        input_system = sys.InputSystem()
        movement_system = sys.MovementSystem(min_x=0, max_x=cfg.RESOLUTION[0], min_y=0, max_y=cfg.RESOLUTION[1])
        script_system = sys.ScriptSystem()
        collision_system = sys.CollisionSystem()
        combat_system = sys.CombatSystem()
        visual_effect_system = sys.VisualEffectsSystem()
        transition_system = sys.TransitionSystem(self.player_entity, self)
        camera_system = sys.CameraSystem(camera_entity, entity_followed=self.player_entity)
        animation_system = sys.AnimationSystem()
        render_system = sys.RenderSystem(window=self.window, camera_entity=camera_entity)

        self.world.add_processor(input_system)
        self.world.add_processor(movement_system)
        self.world.add_processor(script_system)
        self.world.add_processor(collision_system)
        self.world.add_processor(combat_system)
        self.world.add_processor(visual_effect_system)
        self.world.add_processor(transition_system)
        self.world.add_processor(camera_system)
        self.world.add_processor(animation_system)
        self.world.add_processor(render_system)

    def on_exit(self):
        pass
