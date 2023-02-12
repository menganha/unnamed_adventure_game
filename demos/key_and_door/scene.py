import csv
from pathlib import Path
from typing import Optional

import pygame

from event.event_manager import EventType, CollisionEvent, HudUpdateEvent, ClockEvent
from yazelc import components as cmp
from yazelc import config
from yazelc import items
from yazelc import zesper
from yazelc.camera import Camera
from yazelc.controller import Button
from yazelc.items import CollectableItemType
from yazelc.keyboard import Keyboard
from yazelc.scenes.base_scene import BaseScene
from yazelc.systems.collision_system import CollisionSystem
from yazelc.systems.inventory_system import InventorySystem
from yazelc.systems.movement_system import MovementSystem
from yazelc.systems.player_input_system import PlayerInputSystem
from yazelc.systems.render_system import RenderSystem

VELOCITY = 1.5 - 1e-8  # This ensures that the rounding produces the displacement pattern 1,2,1,2... that averages a velocity of 1.5
VELOCITY_DIAGONAL = 1
FONT_ID = 'FONT'


class Hud:
    def __init__(self, world: zesper.World):
        self.world = world
        self.hud_component_id = self.world.create_entity()

        font = self.world.resource_manager.get_font(FONT_ID)
        hud_surface = pygame.surface.Surface((40, 15))
        hud_surface.fill(config.C_YELLOW)
        font.render_text_at('Keys: 0', hud_surface)
        self.world.add_component(self.hud_component_id, cmp.Renderable(hud_surface))

    def on_hud_update(self, event: HudUpdateEvent):
        # TODO: Keep a reference to the inventory, or all the variables it needs to display. When this
        #       event is fired then refresh the HUD. We don't need to pass values to the event message
        font = self.world.resource_manager.get_font(FONT_ID)
        hud_surface = self.world.component_for_entity(self.hud_component_id, cmp.Renderable).image
        hud_surface.fill(config.C_YELLOW)
        font.render_text_at(f'Keys: {event.value}', hud_surface)


class Scene(BaseScene):

    def __init__(self, window: pygame.Surface):
        super().__init__(window)
        self.inventory: Optional[dict[CollectableItemType, int]] = None
        self.hud: Optional[Hud] = None

    def on_exit(self):
        pass

    def on_enter(self):

        # World creation
        map_data_file = Path('demos', 'key_and_door', 'map_data.csv')
        with open(map_data_file, newline='') as csv_file:
            reader = csv.reader(csv_file)
            y_pos = 0
            for row in reader:
                x_pos = 0
                for ele in row:
                    if int(ele):
                        hitbox = cmp.HitBox(x_pos, y_pos, config.TILE_WIDTH, config.TILE_WIDTH, impenetrable=True)
                        position = cmp.Position(x_pos, y_pos)
                        image = pygame.Surface((config.TILE_WIDTH, config.TILE_WIDTH))
                        image.fill(config.C_RED)
                        renderable = cmp.Renderable(image)
                        self.world.create_entity(hitbox, position, renderable)
                    x_pos += config.TILE_WIDTH
                y_pos += config.TILE_WIDTH

        # Player creation
        player_entity_id = self.world.create_entity()
        x_pos, y_pos = 100, 100
        width, height = 7, 7
        image = pygame.Surface((width, height))
        image.fill(config.C_BLUE)
        self.world.add_component(player_entity_id, cmp.Renderable(image=image, depth=100))
        self.world.add_component(player_entity_id, cmp.HitBox(x_pos, y_pos, width, height))
        self.world.add_component(player_entity_id, cmp.Position(x=x_pos, y=y_pos))
        self.world.add_component(player_entity_id, cmp.Velocity(x=0, y=0))
        self.world.add_component(player_entity_id, cmp.Input(handle_input_function=self.handle_input))
        self.world.add_component(player_entity_id, cmp.Health())

        self.inventory = {collectable_type: 0 for collectable_type in CollectableItemType}

        # key creation
        x_pos = 200
        y_pos = 200
        image = pygame.Surface((5, 5))
        image.fill(config.C_YELLOW)
        items.create_entity(items.CollectableItemType.KEY, image, x_pos, y_pos, self.world)

        # Get the input device
        controller = Keyboard()

        # Initialize the HUD
        font_path = Path('assets', 'font', 'Anonymous Pro.ttf')
        self.world.resource_manager.add_font(font_path, 10, config.C_BLACK, FONT_ID)
        self.hud = Hud(self.world)

        # Create Door
        door_entity = self.world.create_entity()
        x_pos, y_pos = 15 * config.TILE_WIDTH, 4 * config.TILE_WIDTH
        width, height = config.TILE_WIDTH, config.TILE_WIDTH
        image = pygame.Surface((width, height))
        image.fill(config.C_GREEN)
        self.world.add_component(door_entity, cmp.Renderable(image=image, depth=100))
        self.world.add_component(door_entity, cmp.Position(x=x_pos, y=y_pos))
        self.world.add_component(door_entity, cmp.Door('dummy_map', 0, 0))
        self.world.add_component(door_entity, cmp.HitBox(x_pos, y_pos, width, height, impenetrable=True))

        # Initialize static camera
        camera = Camera(0, 0, config.RESOLUTION.x, config.RESOLUTION.y)

        # Systems
        input_system = PlayerInputSystem(controller)
        movement_system = MovementSystem()
        collision_system = CollisionSystem()
        inventory_system = InventorySystem(player_entity_id, self.inventory)
        render_system = RenderSystem(self.window, camera)

        self.event_manager.subscribe(EventType.COLLISION, self.on_interaction_with_door)
        self.event_manager.subscribe(EventType.COLLISION, inventory_system.on_collision)
        self.event_manager.subscribe(EventType.HUD_UPDATE, self.hud.on_hud_update)
        self.event_manager.subscribe(EventType.CLOCK, self.on_clock_event)

        processors = [input_system, movement_system, collision_system, inventory_system, render_system]
        for proc in processors:
            self.world.add_processor(proc)

    def on_interaction_with_door(self, collision_event: CollisionEvent):
        if result := self.world.try_pair_signature(collision_event.ent_1, collision_event.ent_2, cmp.Door, cmp.InteractorTag):
            door_ent, door_component, _, _ = result
            if self.inventory[CollectableItemType.KEY] >= 1:
                self.inventory[CollectableItemType.KEY] -= 1
                hud_event = HudUpdateEvent(CollectableItemType.KEY, self.inventory[CollectableItemType.KEY])
                self.event_manager.add_events(hud_event)
                self.world.delete_entity(door_ent)

    def on_clock_event(self, clock_event: ClockEvent):
        self.world.delete_entity(clock_event.entity_id)

    @staticmethod
    def handle_input(player_entity, controller, world):
        velocity = world.component_for_entity(player_entity, cmp.Velocity)
        position = world.component_for_entity(player_entity, cmp.Position)

        direction_x = - controller.is_button_down(Button.LEFT) + controller.is_button_down(Button.RIGHT)
        direction_y = - controller.is_button_down(Button.UP) + controller.is_button_down(Button.DOWN)

        abs_vel = VELOCITY_DIAGONAL if (direction_y and direction_x) else VELOCITY
        velocity.x = direction_x * abs_vel
        velocity.y = direction_y * abs_vel

        # Snaps position to grid when the respective key has been released.  This allows for a deterministic movement
        # pattern by eliminating any decimal residual accumulated when resetting the position to an integer value
        horizontal_key_released = controller.is_button_released(Button.LEFT) or controller.is_button_released(Button.RIGHT)
        vertical_key_released = controller.is_button_released(Button.UP) or controller.is_button_released(Button.DOWN)

        if horizontal_key_released:
            position.x = round(position.x)
        if vertical_key_released:
            position.y = round(position.y)

        if controller.is_button_pressed(Button.A):
            hitbox = cmp.HitBox(0, 0, 10, 5)
            player_hitbox = world.component_for_entity(player_entity, cmp.HitBox)
            hitbox.rect.x = player_hitbox.rect.x
            hitbox.rect.y = player_hitbox.rect.y - 5

            hitbox_entity_id = world.create_entity()
            world.add_component(hitbox_entity_id, hitbox)
            world.add_component(hitbox_entity_id, cmp.Position(hitbox.rect.x, hitbox.rect.y))
            image = pygame.Surface((10, 5))
            image.fill(config.C_WHITE)
            world.add_component(hitbox_entity_id, cmp.Renderable(image))
            world.add_component(hitbox_entity_id, cmp.InteractorTag())
            world.add_component(hitbox_entity_id, cmp.Timer(0))
