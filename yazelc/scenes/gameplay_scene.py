from math import copysign
from pathlib import Path

import pygame

from yazelc import camera
from yazelc import components as cmp
from yazelc import config as cfg
from yazelc import enemy
from yazelc import hud
from yazelc import items
from yazelc import player
from yazelc import resource_manager
from yazelc.event_type import EventType
from yazelc.gamepad import Gamepad
from yazelc.keyboard import Keyboard
from yazelc.maps import Maps
from yazelc.menu.death_menu_creator import DeathMenuCreator
from yazelc.scenes.base_scene import BaseScene
from yazelc.systems.ai_system import AISystem
from yazelc.systems.animation_system import AnimationSystem
from yazelc.systems.camera_system import CameraSystem
from yazelc.systems.collision_system import CollisionSystem
from yazelc.systems.combat_system import CombatSystem
from yazelc.systems.dialog_system import DialogSystem
from yazelc.systems.hud_system import HUDSystem
from yazelc.systems.input_system import InputSystem
from yazelc.systems.inventory_system import InventorySystem
from yazelc.systems.menu_input_system import MenuInputSystem
from yazelc.systems.movement_system import MovementSystem
from yazelc.systems.render_system import RenderSystem
from yazelc.systems.script_system import ScriptSystem
from yazelc.systems.transition_system import TransitionSystem
from yazelc.systems.visual_effects_system import VisualEffectsSystem

FULL_HEART_IMAGE_PATH = Path('assets', 'sprites', 'full_heart.png')
HALF_HEART_IMAGE_PATH = Path('assets', 'sprites', 'half_heart.png')
EMPTY_HEART_IMAGE_PATH = Path('assets', 'sprites', 'empty_heart.png')
FONT_PATH = Path('assets', 'font', 'Anonymous Pro.ttf')


class GameplayScene(BaseScene):

    def on_enter(self):
        # Initialize some values
        self.in_scene = True
        self.scene_processors = []

        # Add resources (TODO: maybe do this in a separate module as they seem to be all over the place)
        resource_manager.add_resource(FULL_HEART_IMAGE_PATH)
        resource_manager.add_resource(HALF_HEART_IMAGE_PATH)
        resource_manager.add_resource(EMPTY_HEART_IMAGE_PATH)
        resource_manager.add_resource(FONT_PATH)

        # Add map entity
        overworld_map = Maps(self.map_data_file)
        for idx, map_layer in enumerate(overworld_map.create_map_image()):
            layer_entity_id = self.world.create_entity()
            self.world.add_component(layer_entity_id, cmp.Position(x=0, y=0))
            depth = 1000 * (idx - 1)
            self.world.add_component(layer_entity_id, cmp.Renderable(image=map_layer, depth=depth))
            self.world.map_layers_entity_id.append(layer_entity_id)

        for position, hitbox, wall_tag in overworld_map.create_solid_rectangles():
            self.world.create_entity(position, hitbox, wall_tag)
        for door, hitbox in overworld_map.create_doors():
            self.world.create_entity(door, hitbox)
        for interactive_tag, text, hitbox in overworld_map.create_signs():
            self.world.create_entity(interactive_tag, text, hitbox)

        # Add player entity
        player_x_pos, player_y_pos = overworld_map.get_center_coord_from_tile(self.start_tile_x_pos,
                                                                              self.start_tile_y_pos)
        if self.world.player_entity_id is None:
            player.create_player_at(center_x_pos=player_x_pos, center_y_pos=player_y_pos, world=self.world)
        else:
            position = self.world.component_for_entity(self.world.player_entity_id, cmp.Position)
            velocity = self.world.component_for_entity(self.world.player_entity_id, cmp.Velocity)
            hitbox = self.world.component_for_entity(self.world.player_entity_id, cmp.HitBox)
            velocity.x, velocity.y = (0, 0)
            hitbox.rect.center = (player_x_pos, player_y_pos)
            position.x, position.y = player.get_position_of_sprite(hitbox)

        # Add camera entity
        camera.create_camera(self.world)

        # Initialize the HUD
        hud.create_hud_entity(self.world)

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
        # TODO: Instantiate them already on the scene processor list!!
        ai_system = AISystem()
        input_system = InputSystem(controller)
        movement_system = MovementSystem()
        script_system = ScriptSystem()
        collision_system = CollisionSystem()
        dialog_system = DialogSystem()
        combat_system = CombatSystem()
        inventory_system = InventorySystem()
        visual_effect_system = VisualEffectsSystem()
        transition_system = TransitionSystem(self)
        camera_system = CameraSystem(self.world.player_entity_id,
                                     camera.get_position_of_entity_to_track(self.world.player_entity_id, self.world),
                                     cmp.Vector(overworld_map.width, overworld_map.height))
        animation_system = AnimationSystem()
        render_system = RenderSystem(window=self.window)
        hud_system = HUDSystem()

        self.scene_processors.extend(  # Note they are added in a give order
            [ai_system, input_system, movement_system, script_system, collision_system, dialog_system, combat_system, inventory_system,
             visual_effect_system, transition_system, camera_system, animation_system, hud_system, render_system]
        )
        for processor in self.scene_processors:
            self.world.add_processor(processor)

    def on_exit(self):
        if type(self.next_scene) == type(self) and self.next_scene != self:
            # TODO: Fine tune all of these parameters
            total_exit_frames = 80
            stop_frame_num = 20
            # Take out some processors perhaps
            # continue running in the door
            camera_pos = self.world.component_for_entity(self.world.camera_entity_id, cmp.Position)
            velocity = self.world.component_for_entity(self.world.player_entity_id, cmp.Velocity)
            position = self.world.component_for_entity(self.world.player_entity_id, cmp.HitBox).rect.copy()
            velocity.x = 0.30 * copysign(1.0, velocity.x) if abs(velocity.x) > 1e-4 else 0
            velocity.y = 0.30 * copysign(1.0, velocity.y) if abs(velocity.y) > 1e-4 else 0
            self.world.remove_processor(InputSystem)
            self.world.remove_processor(TransitionSystem)
            self.world.remove_processor(CameraSystem)

            effect_id = self.world.create_entity()
            radius = cfg.RESOLUTION.x - 100
            cover_surface = pygame.Surface((cfg.RESOLUTION.x, cfg.RESOLUTION.y))
            cover_surface.fill(cfg.C_BLACK)
            cover_surface.set_colorkey(cfg.C_WHITE)
            pygame.draw.circle(cover_surface, cfg.C_WHITE, (position.x - camera_pos.x, position.y - camera_pos.y), radius)
            renderable = cmp.Renderable(image=cover_surface, depth=6000)
            self.world.add_component(effect_id, renderable)
            self.world.add_component(effect_id, cmp.Position(camera_pos.x, camera_pos.y))

            while total_exit_frames > 0:

                self.world.process()

                cover_surface.fill(cfg.C_BLACK)
                pygame.draw.circle(cover_surface, cfg.C_WHITE, (position.x - camera_pos.x, position.y - camera_pos.y), radius)
                self.world.component_for_entity(effect_id, cmp.Renderable).image = cover_surface
                radius -= 5

                if total_exit_frames == stop_frame_num:
                    velocity.x = 0
                    velocity.y = 0

                total_exit_frames -= 1

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.in_scene = False
                self.next_scene = None
            elif event.type == EventType.DEATH.value:
                self.handle_death()
            elif event.type == EventType.PAUSE.value:
                self.paused = not self.paused
                if self.paused:
                    controller = self.world.get_processor(InputSystem).controller
                    self.world.remove_all_processors_except(RenderSystem)
                    self.world.add_processor(MenuInputSystem(controller))
                else:
                    self.world.clear_processors()
                    for proc in self.scene_processors:
                        self.world.add_processor(proc)
            elif event.type == EventType.RESTART.value:
                self.in_scene = False
                self.next_scene = self
                self.world.clear_database()  # TODO: Should one keep the player or store some information here?

    def handle_death(self):
        # Saves the status of the player (weapons, hearts, etc., wherever that is allocated in the end)
        # Removes all processors except the animation and render processor
        controller = self.world.get_processor(InputSystem).controller
        self.world.remove_all_processors_except(RenderSystem)
        self.world.add_processor(MenuInputSystem(controller))

        self.world.delete_entity(self.world.hud_entity_id)
        for entity_id in self.world.map_layers_entity_id:
            self.world.delete_entity(entity_id)

        death_menu_creator = DeathMenuCreator()
        death_menu_creator.create_entity(self.world)
        # Creates a script to be run every frame such that when it ends shows a menu with either continue or exits the game
        # self.world.remove_component(self.world.player_entity_id, cmp.Health)
        # world.remove_component(world.player_entity_id, cmp.Animation)
        # Creates a new menu entity with the continue or quit message. That entity controls the actions of restarting the
        # game, etc.
        # ...
