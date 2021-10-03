import logging

import pygame

import esper
import maps
from camera_system import CameraSystem
from components import Renderable, Position, Velocity, HitBox, Input
from config import Config
from input_system import InputSystem
from keyboard import Keyboard
from movement_system import MovementSystem
from render_system import RenderSystem


def run():
    pygame.init()
    window = pygame.display.set_mode(Config.RESOLUTION, flags=pygame.SCALED)
    pygame.display.set_caption('Unnamed Adventure Game')
    clock = pygame.time.Clock()
    c_blue = pygame.Color(50, 153, 213)
    c_white = pygame.Color(255, 255, 255)
    c_green = pygame.Color(0, 255, 0)
    pygame.key.set_repeat(1, 1)

    # Initialize Logging
    logging.basicConfig(level=logging.INFO)

    # initialize keyboard
    keyboard = Keyboard()

    # Initialize Esper world, and create a "player" Entity with a few Components.
    world = esper.World()

    # Define player entity
    player = world.create_entity()
    player_surface = pygame.Surface((16, 16))
    player_surface.fill(c_blue)

    def input_processing(player_entity: int):
        keyboard.process_input()

        if keyboard.is_key_released(pygame.K_UP) or keyboard.is_key_released(pygame.K_DOWN):
            world.component_for_entity(player_entity, Velocity).y = 0
        if keyboard.is_key_down(pygame.K_DOWN):
            world.component_for_entity(player_entity, Velocity).y = 2
        if keyboard.is_key_down(pygame.K_UP):
            world.component_for_entity(player_entity, Velocity).y = -2

        if keyboard.is_key_released(pygame.K_LEFT) or keyboard.is_key_released(pygame.K_RIGHT):
            world.component_for_entity(player_entity, Velocity).x = 0
        if keyboard.is_key_down(pygame.K_LEFT):
            world.component_for_entity(player_entity, Velocity).x = -2
        if keyboard.is_key_down(pygame.K_RIGHT):
            world.component_for_entity(player_entity, Velocity).x = +2

    world.add_component(player, Velocity(x=0, y=0))
    world.add_component(player, Position(x=20, y=20))
    world.add_component(player, HitBox(20, 20, player_surface.get_width(), player_surface.get_height()))
    world.add_component(player, Input(input_processing))
    world.add_component(player, Renderable(image=player_surface))

    # Add map entity
    map_entity = world.create_entity()
    map_surface = maps.create_map_image('ecs_data/overworld_map.tmx')
    world.add_component(map_entity, Position(x=0, y=0))
    world.add_component(map_entity, Renderable(image=map_surface, depth=3))

    # Add camera entity
    camera_entity = world.create_entity()
    world.add_component(camera_entity, Position(x=0, y=0))

    # Add a solid tile
    solid_tile = world.create_entity()
    tile_surface = pygame.Surface((30, 30))
    tile_surface.fill(c_green)
    world.add_component(solid_tile, Position(x=40, y=45))
    world.add_component(solid_tile, Renderable(image=tile_surface))
    world.add_component(solid_tile, HitBox(40, 45, tile_surface.get_width(), tile_surface.get_height()))

    # Another motionless Entity:
    enemy_surface = pygame.Surface((10, 10))
    enemy_surface.fill(c_white)
    enemy = world.create_entity()
    world.add_component(enemy, Renderable(image=enemy_surface))
    world.add_component(enemy, Renderable(image=enemy_surface))
    world.add_component(enemy, Position(x=400, y=100))

    # Create some Processor instances, and assign them to be processed.

    render_processor = RenderSystem(window=window, camera_entity=camera_entity)
    input_processor = InputSystem()
    movement_processor = MovementSystem(min_x=0, max_x=Config.RESOLUTION[0], min_y=0, max_y=Config.RESOLUTION[1])
    camera_processor = CameraSystem(camera_entity, entity_followed=player)
    world.add_processor(input_processor)
    world.add_processor(movement_processor)
    world.add_processor(camera_processor)
    world.add_processor(render_processor)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        world.process()
        clock.tick(Config.FPS)


if __name__ == "__main__":
    run()
    pygame.quit()
