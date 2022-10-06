from pathlib import Path
from typing import List, Optional

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
from yazelc.event import EventType, PauseEvent, DeathEvent, RestartEvent
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
from yazelc.systems.script_system import ClockSystem
from yazelc.systems.transition_system import TransitionSystem
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
FONT_COLOR = cfg.C_WHITE
BOMB_IMG_PATH = Path('assets', 'sprites', 'bomb.png')


class GameplayScene(BaseScene):

    def __init__(self, window: pygame.Surface, map_file_path: Path, start_tile_x_pos: int, start_tile_y_pos: int,
                 player_components: Optional[List[object]] = None):
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

        # Add map entity  TODO: Move this chunk to the Map class
        self.maps = Map(self.map_data_file, self.world.resource_manager)
        self.maps.add_map_to_the_world(self.world)

        dialog_font = self.world.resource_manager.get_font(dialog_box.DIALOG_FONT_ID)
        for components in self.maps.create_objects(dialog_font):
            self.world.create_entity(*components)
        for door, hitbox in self.maps.create_doors():
            self.world.create_entity(door, hitbox)
        for door, hitbox in self.maps.create_doors():
            self.world.create_entity(door, hitbox)
        for pos_x, pos_y, enemy_type in self.maps.create_enemies():
            enemy.create_jelly_at(pos_x, pos_y, self.world)  # TODO: Generalize for any type of enemy

        # Add player entity
        player_x_pos, player_y_pos = self.maps.get_center_coord_from_tile(self.start_tile_x_pos, self.start_tile_y_pos)
        if self.player_entity_id is None:
            self.player_entity_id = player.create_player_at(center_x_pos=player_x_pos, center_y_pos=player_y_pos, world=self.world)
        else:
            position = self.world.component_for_entity(self.player_entity_id, cmp.Position)
            velocity = self.world.component_for_entity(self.player_entity_id, cmp.Velocity)
            hitbox = self.world.component_for_entity(self.player_entity_id, cmp.HitBox)
            velocity.x, velocity.y = (0, 0)
            hitbox.rect.center = (player_x_pos, player_y_pos)
            position.x, position.y = player.get_position_of_sprite(hitbox)

        # Add camera entity
        self.camera = Camera(0, 0, self.maps.width, self.maps.height)
        self.camera.track_entity(self.player_entity_id, self.world)

        # Initialize the HUD
        hud.create_hud_entity(self.world)

        # Create enemy
        enemy.create_jelly_at(200, 450, self.world)

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
        # TODO: Instantiate them already on the scene processor list!!
        ai_system = AISystem()
        input_system = InputSystem(controller)
        movement_system = MovementSystem()
        script_system = ClockSystem()
        collision_system = CollisionSystem()
        dialog_system = DialogSystem()
        combat_system = CombatSystem(self.player_entity_id)
        inventory_system = InventorySystem(self.player_entity_id, inventory)
        visual_effect_system = VisualEffectsSystem()
        transition_system = TransitionSystem(self, self.player_entity_id)
        camera_system = CameraSystem(self.camera)
        animation_system = AnimationSystem()
        render_system = RenderSystem(self.window, self.camera)

        scene_processors = []
        scene_processors.extend(  # Note they are added in a give order
            [ai_system, input_system, movement_system, script_system, collision_system, dialog_system, combat_system, inventory_system,
             visual_effect_system, transition_system, camera_system, animation_system, render_system])
        for processor in scene_processors:
            self.world.add_processor(processor)

        # Register some events
        self.event_manager.subscribe(EventType.COLLISION, combat_system.on_collision)
        self.event_manager.subscribe(EventType.COLLISION, dialog_system.on_collision)
        self.event_manager.subscribe(EventType.COLLISION, transition_system.on_collision)
        self.event_manager.subscribe(EventType.COLLISION, inventory_system.on_collision)
        self.event_manager.subscribe(EventType.DEATH, self.on_death)
        self.event_manager.subscribe(EventType.RESTART, self.on_restart)
        self.event_manager.subscribe(EventType.PAUSE, self.on_pause)

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
            for typ in [Status.IDLE, Status.MOVING, Status.ATTACKING]:
                identifier = f'{typ.name}_{direction.name}'
                img_path = PLAYER_IMAGE_PATH / f'{identifier}.png'.lower()
                flip = False
                if direction == Direction.LEFT:
                    img_path = PLAYER_IMAGE_PATH / f'{typ.name}_{Direction.RIGHT.name}.png'.lower()
                    flip = True
                self.world.resource_manager.add_animation_strip(img_path, player.SPRITE_SIZE, flip, identifier)
        for direction in [Direction.UP, Direction.DOWN, Direction.RIGHT, Direction.LEFT]:
            identifier = f'wooden_sword_{direction.name}'
            img_path = WEAPON_IMAGE_PATH / f'{identifier}.png'.lower()
            flip = False
            if direction == Direction.LEFT:
                img_path = WEAPON_IMAGE_PATH / f'wooden_sword_{Direction.RIGHT.name}.png'.lower()
                flip = True
            self.world.resource_manager.add_animation_strip(img_path, player.SWORD_SPRITE_WIDTH, flip, identifier)

    def on_exit(self):
        if type(self.next_scene) == type(self) and self.next_scene != self:
            # transition_effects.closing_circle(self.player_entity_id, self.camera, self.world)
            transition_effects.map_translation(self.maps, self.next_scene, self.world)

    def on_pause(self, pause_event: PauseEvent):
        """ Handles the events of pause and unpause"""
        self.paused = not self.paused
        if self.paused:
            menu_box.create_pause_menu(self.world)
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

    def on_death(self, death_event: DeathEvent):
        """
        Saves the status of the player (weapons, hearts, etc., wherever that is allocated in the end), removes all processors
        except the animation and render processor, and creates a death menu
        """
        self.world.remove_all_processors_except(RenderSystem, InputSystem)

        # for entity_id in self.world.map_layers_entity_id:
        #     self.world.delete_entity(entity_id)

        menu_box.create_death_menu(self.world)
