from math import copysign
from pathlib import Path
from typing import Optional, Any

import pygame

from yazelc import components as cmp
from yazelc import config as cfg
from yazelc import dialog_box
from yazelc import enemy
from yazelc import hud
from yazelc import items
from yazelc import zesper
from yazelc.camera import Camera
from yazelc.components import Input
from yazelc.event import EventType, PauseEvent, DeathEvent, RestartEvent, CollisionEvent
from yazelc.gamepad import Gamepad
from yazelc.items import CollectableItemType
from yazelc.keyboard import Keyboard
from yazelc.map import Map, WorldMap
from yazelc.menu import menu_box
from yazelc.player import player
from yazelc.scenes import transition_effects
from yazelc.scenes.base_scene import BaseScene
from yazelc.systems.ai_system import AISystem
from yazelc.systems.animation_system import AnimationSystem
from yazelc.systems.camera_system import CameraSystem
from yazelc.systems.collision_system import CollisionSystem
from yazelc.systems.combat_system import CombatSystem
from yazelc.systems.dialog_system import DialogSystem
from yazelc.systems.input_system import InputSystem
from yazelc.systems.inventory_system import InventorySystem
from yazelc.systems.movement_system import MovementSystem
from yazelc.systems.render_system import RenderSystem
from yazelc.systems.visual_effects_system import VisualEffectsSystem
from yazelc.utils.game_utils import Direction, Status

FULL_HEART_IMAGE_PATH = Path('assets', 'sprites', 'full_heart.png')
PLAYER_IMAGE_PATH = Path('assets', 'sprites', 'player')
HALF_HEART_IMAGE_PATH = Path('assets', 'sprites', 'half_heart.png')
EMPTY_HEART_IMAGE_PATH = Path('assets', 'sprites', 'empty_heart.png')
JELLY_ENEMY_PATH = Path('assets', 'sprites', 'enemy', 'jelly_idle.png')
COINS_IMAGE_PATH = Path('assets', 'sprites', 'coins.png')
TREASURE_IMAGE_PATH = Path('assets', 'sprites', 'treasure.png')
WEAPON_IMAGE_PATH = Path('assets', 'sprites', 'weapon')
FONT_PATH = Path('assets', 'font', 'Anonymous Pro.ttf')
FONT_SIZE = 12
ZERO_THRESHOLD = 1e-2
FONT_COLOR = cfg.C_WHITE
BOMB_IMG_PATH = Path('assets', 'sprites', 'bomb.png')
MAP_VELOCITY_TRANSITION = 4
PROCESSOR_PRIORITY = {
    AISystem: 11,
    InputSystem: 10,
    MovementSystem: 9,
    CollisionSystem: 8,
    DialogSystem: 7,
    CombatSystem: 6,
    InventorySystem: 5,
    VisualEffectsSystem: 4,
    CameraSystem: 3,
    AnimationSystem: 2,
    RenderSystem: 1}


class GameplayScene(BaseScene):

    def __init__(self, window: pygame.Surface, map_file_path: Path, start_tile_x_pos: int, start_tile_y_pos: int,
                 player_components: Optional[tuple[Any, ...]] = None):
        super().__init__(window)
        self.map_data_file = map_file_path
        self.start_tile_x_pos = start_tile_x_pos
        self.start_tile_y_pos = start_tile_y_pos
        self._cached_scene_processors: list[zesper.Processor] = []
        self._input_storage: list[tuple[int, Input]] = []  # Stores the input components removed temporarily during a pause state
        self.player_entity_id: Optional[int] = None
        self.camera: Optional[Camera] = None
        self.maps: Optional[Map] = None
        if player_components:
            self.player_entity_id = self.world.create_entity(*player_components)

    def on_enter(self):

        self.load_resources()
        self._generate_map()
        self._generate_objects()

        # Add player entity
        player_x_pos, player_y_pos = self.maps.get_center_coord_from_tile(self.start_tile_x_pos, self.start_tile_y_pos)
        if self.player_entity_id is None:
            self.player_entity_id = player.create_player_at(center_x_pos=player_x_pos, center_y_pos=player_y_pos, world=self.world)
        else:
            position = self.world.component_for_entity(self.player_entity_id, cmp.Position)
            velocity = self.world.component_for_entity(self.player_entity_id, cmp.Velocity)
            hitbox = self.world.component_for_entity(self.player_entity_id, cmp.HitBox)
            velocity.x, velocity.y = (0, 0)
            hitbox.center = (player_x_pos, player_y_pos)
            position.x, position.y = player.get_position_of_sprite(hitbox)

        # Add camera entity
        self.camera = Camera(0, 0, self.maps.width, self.maps.height)
        self.camera.track_entity(self.player_entity_id, self.world)

        # Initialize the HUD
        hud.create_hud_entity(self.world)

        # Create a pickable item
        for idx in range(3):
            x_pos, y_pos = self.maps.get_center_coord_from_tile(7 + idx, 17)
            items.create_entity(CollectableItemType.COIN, x_pos, y_pos, self.world)
        # items.create_entity(items.PickableItemType.HEART, 300, 355, self.world)
        # items.create_entity(items.PickableItemType.HEART, 350, 355, self.world)
        inventory = {collectable_type: 0 for collectable_type in CollectableItemType}

        # Get the input device
        pygame.joystick.init()
        if pygame.joystick.get_count():
            controller = Gamepad(pygame.joystick.Joystick(0))
        else:
            controller = Keyboard()
            pygame.joystick.quit()

        # Create the systems for the scene
        combat_system = CombatSystem(self.player_entity_id)
        dialog_system = DialogSystem()
        inventory_system = InventorySystem(self.player_entity_id, inventory)
        self.world.add_processor(AISystem(), PROCESSOR_PRIORITY[AISystem])
        self.world.add_processor(InputSystem(controller), PROCESSOR_PRIORITY[InputSystem])
        self.world.add_processor(MovementSystem(), PROCESSOR_PRIORITY[MovementSystem])
        self.world.add_processor(CollisionSystem(), PROCESSOR_PRIORITY[CollisionSystem])
        self.world.add_processor(dialog_system, PROCESSOR_PRIORITY[DialogSystem])
        self.world.add_processor(combat_system, PROCESSOR_PRIORITY[CombatSystem])
        self.world.add_processor(inventory_system, PROCESSOR_PRIORITY[InventorySystem])
        self.world.add_processor(VisualEffectsSystem(), PROCESSOR_PRIORITY[VisualEffectsSystem])
        self.world.add_processor(CameraSystem(self.camera), PROCESSOR_PRIORITY[CameraSystem])
        self.world.add_processor(AnimationSystem(), PROCESSOR_PRIORITY[AnimationSystem])
        self.world.add_processor(RenderSystem(self.window, self.camera), PROCESSOR_PRIORITY[RenderSystem])

        # Register events
        self.event_manager.subscribe(EventType.COLLISION, combat_system.on_collision)
        self.event_manager.subscribe(EventType.COLLISION, dialog_system.on_collision)
        self.event_manager.subscribe(EventType.COLLISION, inventory_system.on_collision)
        self.event_manager.subscribe(EventType.DEATH, self.on_death)
        self.event_manager.subscribe(EventType.RESTART, self.on_restart)
        self.event_manager.subscribe(EventType.PAUSE, self.on_pause)
        self.event_manager.subscribe(EventType.COLLISION, self.on_hit_door)

    def load_resources(self):
        """ Should load all resources for a given scene """
        world_map = WorldMap.from_map_file_path(self.map_data_file)
        for tileset_image_path in world_map.get_needed_images_path():
            self.world.resource_manager.add_texture(tileset_image_path)
        self.world.resource_manager.add_font(FONT_PATH, FONT_SIZE, FONT_COLOR, dialog_box.DIALOG_FONT_ID)
        self.world.resource_manager.add_font(FONT_PATH, FONT_SIZE, FONT_COLOR, menu_box.MENU_FONT_ID)
        self.world.resource_manager.add_texture(FULL_HEART_IMAGE_PATH)
        self.world.resource_manager.add_texture(HALF_HEART_IMAGE_PATH)
        self.world.resource_manager.add_texture(EMPTY_HEART_IMAGE_PATH)
        self.world.resource_manager.add_animation_strip(JELLY_ENEMY_PATH, enemy.JELLY_SPRITE_WIDTH, explicit_name=enemy.JELLY_ID)
        self.world.resource_manager.add_animation_strip(TREASURE_IMAGE_PATH, InventorySystem.TREASURE_TILE_SIZE,
                                                        explicit_name=InventorySystem.TREASURE_TEXTURE_ID)
        self.world.resource_manager.add_animation_strip(COINS_IMAGE_PATH, items.COIN_TILE_SIZE, explicit_name=CollectableItemType.COIN.name)
        self.world.resource_manager.add_animation_strip(BOMB_IMG_PATH, player.BOMB_SPRITE_WIDTH, explicit_name=player.BOMB_SPRITES_ID)
        for direction in [Direction.UP, Direction.DOWN, Direction.RIGHT, Direction.LEFT]:
            for typ in [Status.MOVING, Status.ATTACKING]:
                flip = False
                identifier = f'{typ.name}_{direction.name}'
                dir_str = direction.name
                if direction == Direction.LEFT:
                    flip = True
                    dir_str = Direction.RIGHT.name
                img_path = PLAYER_IMAGE_PATH / f'{typ.name}_{dir_str}.png'.lower()
                self.world.resource_manager.add_animation_strip(img_path, player.SPRITE_SIZE, flip, identifier)

        # idle animation
        for direction in [Direction.UP, Direction.DOWN, Direction.RIGHT, Direction.LEFT]:
            identifier = f'{Status.MOVING.name}_{direction.name}'
            alias = f'{Status.IDLE.name}_{direction.name}'
            self.world.resource_manager.add_animation_alias(identifier, alias)

        for direction in [Direction.UP, Direction.DOWN, Direction.RIGHT, Direction.LEFT]:
            identifier = f'wooden_sword_{direction.name}'
            img_path = WEAPON_IMAGE_PATH / f'{identifier}.png'.lower()
            flip = False
            if direction == Direction.LEFT:
                flip = True
                img_path = WEAPON_IMAGE_PATH / f'wooden_sword_{Direction.RIGHT.name}.png'.lower()
            self.world.resource_manager.add_animation_strip(img_path, player.SWORD_SPRITE_WIDTH, flip, identifier)

    def _generate_map(self, x_pos: int = 0, y_pos: int = 0):
        """
        Generates the map with all the relevant data, e.g., items, enemies, triggers, etc.
        """

        self.maps = Map(self.map_data_file, self.world.resource_manager)

        for depth, map_layer in self.maps.get_map_images():
            layer_entity_id = self.world.create_entity()
            self.world.add_component(layer_entity_id, cmp.Position(x=x_pos, y=y_pos))
            self.world.add_component(layer_entity_id, cmp.Renderable(image=map_layer, depth=depth))
            self.maps.layer_entities.append(layer_entity_id)

    def _generate_objects(self):
        dialog_font = self.world.resource_manager.get_font(dialog_box.DIALOG_FONT_ID)
        for components in self.maps.create_objects():
            ent_id = self.world.create_entity(*components)
            self.maps.object_entities.append(ent_id)
        for components in self.maps.create_interactive_objects(dialog_font):
            ent_id = self.world.create_entity(*components)
            self.maps.object_entities.append(ent_id)
        for door, hitbox in self.maps.create_doors():
            ent_id = self.world.create_entity(door, hitbox)
            self.maps.object_entities.append(ent_id)
        for pos_x, pos_y, enemy_type in self.maps.create_enemies():
            ent_id = enemy.create_jelly_at(pos_x, pos_y, self.world)  # TODO: Generalize for any type of enemy
            self.maps.object_entities.append(ent_id)

    def on_exit(self):
        if type(self.next_scene) == type(self) and self.next_scene != self:  # Why do we make this check?
            transition_effects.closing_circle(self.player_entity_id, self.camera, self.world)

    def on_pause(self, pause_event: PauseEvent):
        """ Handles the events of pause and unpause"""
        self.paused = not self.paused
        if self.paused:
            # Removes all control form other entities unless it has a dialog or menu component
            # We store these components locally for later reinsertion
            for entity, input_ in self.world.get_component(cmp.Input):
                if not self.world.has_component(entity, cmp.Dialog) and not self.world.has_component(entity, cmp.Menu):
                    self._input_storage.append((entity, input_))
                    self.world.remove_component(entity, cmp.Input)
            self._cached_scene_processors = self.world.remove_all_processors_except(RenderSystem, DialogSystem, InputSystem)
        else:
            for entity, input_ in self._input_storage:
                self.world.add_component(entity, input_)
            self._input_storage = []
            for proc in self._cached_scene_processors:
                self.world.add_processor(proc)
            self._cached_scene_processors = []

    def on_restart(self, restart_event: RestartEvent):
        self.in_scene = False
        self.next_scene = self
        self.player_entity_id = None  # TODO: Should one keep the player or store some information here?
        self.world.clear_database()
        self.event_manager.clear()

    def on_hit_door(self, collision_event: CollisionEvent):
        # TODO: Fix bug where enemies can go through doors since there are no solid hitboxes preventing movement
        if component := self.world.try_signature(collision_event.ent_1, collision_event.ent_2, cmp.Door):
            ent_door, door, player_ent = component
            if player_ent != self.player_entity_id:  # Check if the other entity is the players
                return
            if door.target_map.parent != self.map_data_file.parent:
                self.in_scene = False
                player_components = self.world.components_for_entity(self.player_entity_id)
                current_scene_class = type(self)
                self.next_scene = current_scene_class(self.window, door.target_map, door.target_x, door.target_y, player_components)
            else:
                self.empty_queues()

                # Delete object entities and store references to old map layer image entities
                for ent_id in self.maps.object_entities:
                    if self.world.entity_exists(ent_id):
                        self.world.delete_entity(ent_id)
                previous_map_layers = self.maps.layer_entities

                player_position = self.world.component_for_entity(player_ent, cmp.Position)
                player_hitbox = self.world.component_for_entity(player_ent, cmp.HitBox)
                player_velocity = self.world.component_for_entity(player_ent, cmp.Velocity)

                # player_position.x, player_position.y = self.maps.get_coord_from_tile(door.target_x, door.target_y)
                # player_hitbox.rect.centerx, player_hitbox.rect.centery = player.get_position_of_hitbox(player_position)

                normal = [0 if abs(value) < ZERO_THRESHOLD else copysign(1, value) for value in (player_velocity.x, player_velocity.y)]
                map_velocity = [- value * MAP_VELOCITY_TRANSITION for value in normal]
                new_map_position = [nor * res for (nor, res) in zip(normal, cfg.RESOLUTION)]

                # Generate new map and add velocity to the map layers and player
                self.map_data_file = door.target_map
                self._generate_map(*new_map_position)

                for layer_entity_id in self.maps.layer_entities:
                    self.world.add_component(layer_entity_id, cmp.Velocity(*map_velocity))
                for layer_entity_id in previous_map_layers:
                    self.world.add_component(layer_entity_id, cmp.Velocity(*map_velocity))

                # Store some processors and remove them temporarily
                for processor_type in (InputSystem, CollisionSystem, CameraSystem):
                    proc = self.world.get_processor(processor_type)
                    self._cached_scene_processors.append(proc)
                    self.world.remove_processor(processor_type)

                # Run the animation. Remove magic numbers
                distance = (cfg.RESOLUTION.x if abs(normal[0]) > ZERO_THRESHOLD else cfg.RESOLUTION.y)
                frames_to_exit = round(distance / MAP_VELOCITY_TRANSITION)
                # TODO: The amount of tiles is variable. For example for transitions without doors it , e.g., 1.2 instead of 3
                velocity_for_three_tiles = [map_vel + 3 * cfg.TILE_WIDTH * nor / frames_to_exit for (map_vel, nor) in
                                            zip(map_velocity, normal)]
                player_velocity.x, player_velocity.y = velocity_for_three_tiles
                while frames_to_exit > 0:
                    self.world.process()
                    frames_to_exit -= 1

                player_velocity.x, player_velocity.y = 0, 0
                player_position.x, player_position.y = self.maps.get_coord_from_tile(door.target_x, door.target_y)
                player_hitbox.centerx, player_hitbox.centery = player.get_position_of_hitbox(player_position)

                # Remove velocity components and delete old map layer entities
                for layer_entity_id in self.maps.layer_entities:
                    self.world.remove_component(layer_entity_id, cmp.Velocity)
                for layer_entity_id in previous_map_layers:
                    self.world.delete_entity(layer_entity_id)

                # Generate new objects and add the cached processors
                self._generate_objects()
                for proc in self._cached_scene_processors:
                    self.world.add_processor(proc, PROCESSOR_PRIORITY[type(proc)])
                self._cached_scene_processors = []

                # Marks the event as handled
                return True

    def on_death(self, death_event: DeathEvent):
        """
        Saves the status of the player (weapons, hearts, etc., wherever that is allocated in the end), removes all processors
        except the animation and render processor, and creates a death menu
        """
        self.world.remove_all_processors_except(RenderSystem, InputSystem)

        # for entity_id in self.world.map_layers_entity_id:
        #     self.world.delete_entity(entity_id)

        menu_box.create_death_menu(self.world)
