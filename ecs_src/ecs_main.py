import logging
from pathlib import Path

import pygame

import esper
import maps
from animation_stripe import AnimationStripe
from animation_system import AnimationSystem
from camera_system import CameraSystem
from combat_system import CombatSystem
from components import Renderable, Position, Velocity, HitBox, Input, MeleeWeapon, Health, Animation
from config import Config
from direction import Direction
from input_system import InputSystem
from keyboard import Keyboard
from movement_system import MovementSystem
from render_system import RenderSystem


def run():
    pygame.init()
    window = pygame.display.set_mode(Config.RESOLUTION, flags=pygame.SCALED)
    pygame.display.set_caption('Unnamed Adventure Game')
    clock = pygame.time.Clock()
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

    def input_processing(controlled_entity: int):
        """
        Note: If moving in two directions at the same time, e.g., up and right, the renderable direction
        attribute will always be the one in the vertical direction, i.e, up
        """
        keyboard.process_input()

        if keyboard.is_key_released(pygame.K_UP) or keyboard.is_key_released(pygame.K_DOWN):
            world.component_for_entity(controlled_entity, Velocity).y = 0
        if keyboard.is_key_down(pygame.K_DOWN):
            world.component_for_entity(controlled_entity, Velocity).y = 2
            world.component_for_entity(controlled_entity, Renderable).direction = Direction.SOUTH
        if keyboard.is_key_down(pygame.K_UP):
            world.component_for_entity(controlled_entity, Velocity).y = -2
            world.component_for_entity(controlled_entity, Renderable).direction = Direction.NORTH

        if keyboard.is_key_released(pygame.K_LEFT) or keyboard.is_key_released(pygame.K_RIGHT):
            world.component_for_entity(controlled_entity, Velocity).x = 0
        if keyboard.is_key_down(pygame.K_LEFT):
            world.component_for_entity(controlled_entity, Velocity).x = -2
            world.component_for_entity(controlled_entity, Renderable).direction = Direction.WEST
        if keyboard.is_key_down(pygame.K_RIGHT):
            world.component_for_entity(controlled_entity, Velocity).x = +2
            world.component_for_entity(controlled_entity, Renderable).direction = Direction.EAST

        if keyboard.is_key_pressed(pygame.K_SPACE):
            world.component_for_entity(controlled_entity, MeleeWeapon).frame_counter = 0

        if keyboard.is_key_pressed(pygame.K_q):
            Config.DEBUG_MODE = not Config.DEBUG_MODE

    world.add_component(player, Velocity(x=0, y=0))
    world.add_component(player, Position(x=100, y=100))
    world.add_component(player, Input(input_processing))
    world.add_component(player, Health())
    world.add_component(player, MeleeWeapon(range_front=8, offset=16))

    # Player Animations
    kwargs = {}
    for typ in ['idle', 'move']:
        for direction in ['up', 'down', 'left']:
            img_path = Path('assets', 'sprites', 'player', f'{typ}_{direction}.png')
            kwargs.update({f'{typ}_{direction}': AnimationStripe(img_path, sprite_width=32, delay=15)})

    world.add_component(player, Renderable(image=kwargs['idle_down'][0]))
    world.add_component(player, Animation(**kwargs))

    sprite_width = kwargs['idle_down'][0].get_width()
    sprite_height = kwargs['idle_down'][0].get_height()
    scale_offset = - int(sprite_width * 0.50)
    world.add_component(player, HitBox(3, 3, sprite_width, sprite_height, scale_offset))

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

    # Another motionless enemy entity:
    enemy = world.create_entity()
    enemy_idle_down_image_path = Path('assets', 'sprites', 'enemy', 'jelly_idle.png')
    enemy_idle_animation = AnimationStripe(enemy_idle_down_image_path, sprite_width=16, delay=15)
    world.add_component(enemy, Renderable(image=enemy_idle_animation[0]))
    world.add_component(enemy, Position(x=400, y=160))
    world.add_component(enemy, HitBox(400, 160, 16, 16))
    world.add_component(enemy, Animation(enemy_idle_animation))
    world.add_component(enemy, Health())

    # Create some Processor instances, and assign them to be processed.

    render_processor = RenderSystem(window=window, camera_entity=camera_entity)
    input_processor = InputSystem()
    animation_system = AnimationSystem()
    movement_processor = MovementSystem(min_x=0, max_x=Config.RESOLUTION[0], min_y=0, max_y=Config.RESOLUTION[1])
    camera_processor = CameraSystem(camera_entity, entity_followed=player)
    combat_system = CombatSystem()
    world.add_processor(input_processor)
    world.add_processor(animation_system)
    world.add_processor(combat_system)
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
