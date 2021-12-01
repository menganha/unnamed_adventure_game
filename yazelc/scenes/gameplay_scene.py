import pygame

from yazelc import components as cmp
from yazelc import enemy
from yazelc import items
from yazelc import player
from yazelc.gamepad import Gamepad
from yazelc.keyboard import Keyboard
from yazelc.maps import Maps
from yazelc.scenes.base_scene import BaseScene
from yazelc.systems.ai_system import AISystem
from yazelc.systems.animation_system import AnimationSystem
from yazelc.systems.camera_system import CameraSystem
from yazelc.systems.collision_system import CollisionSystem
from yazelc.systems.combat_system import CombatSystem
from yazelc.systems.input_system import InputSystem
from yazelc.systems.inventory_system import InventorySystem
from yazelc.systems.movement_system import MovementSystem
from yazelc.systems.render_system import RenderSystem
from yazelc.systems.script_system import ScriptSystem
from yazelc.systems.transition_system import TransitionSystem
from yazelc.systems.visual_effects_system import VisualEffectsSystem


class GameplayScene(BaseScene):

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
        if not self.PLAYER_ENTITY:
            self.PLAYER_ENTITY = player.create_player_at(center_x_pos=player_x_pos, center_y_pos=player_y_pos, world=self.world)
        else:
            position = self.world.component_for_entity(self.PLAYER_ENTITY, cmp.Position)
            velocity = self.world.component_for_entity(self.PLAYER_ENTITY, cmp.Velocity)
            hitbox = self.world.component_for_entity(self.PLAYER_ENTITY, cmp.HitBox)
            velocity.x, velocity.y = (0, 0)
            hitbox.rect.center = (player_x_pos, player_y_pos)
            position.x, position.y = player.get_position_of_sprite(hitbox)

        # Add camera entity
        camera_entity = self.world.create_entity()
        self.world.add_component(camera_entity, cmp.Position(x=0, y=0))

        # Create enemy
        enemy.create_jelly_at(400, 400, self.world)

        # Create a pickable item
        items.create_entity(items.ItemType.HEART, 700, 700, self.world)

        # Get the input device
        pygame.joystick.init()
        if pygame.joystick.get_count():
            controller = Gamepad(pygame.joystick.Joystick(0))
        else:
            controller = Keyboard()
            pygame.joystick.quit()

        # Create the systems for the scene
        ai_system = AISystem()
        input_system = InputSystem(controller)
        movement_system = MovementSystem()
        script_system = ScriptSystem()
        collision_system = CollisionSystem()
        combat_system = CombatSystem()
        inventory_system = InventorySystem(self.PLAYER_ENTITY)
        visual_effect_system = VisualEffectsSystem()
        transition_system = TransitionSystem(self)
        camera_system = CameraSystem(camera_entity, entity_followed=self.PLAYER_ENTITY, max_x=overworld_map.width,
                                     max_y=overworld_map.height)
        animation_system = AnimationSystem()
        render_system = RenderSystem(window=self.window, camera_entity=camera_entity)

        self.world.add_processor(ai_system)
        self.world.add_processor(input_system)
        self.world.add_processor(movement_system)
        self.world.add_processor(script_system)
        self.world.add_processor(collision_system)
        self.world.add_processor(combat_system)
        self.world.add_processor(inventory_system)
        self.world.add_processor(visual_effect_system)
        self.world.add_processor(transition_system)
        self.world.add_processor(camera_system)
        self.world.add_processor(animation_system)
        self.world.add_processor(render_system)

    def on_exit(self):
        pass
