from pathlib import Path

import pygame

import esper
from animation_stripe import AnimationStripe
from animation_system import AnimationSystem
from camera_system import CameraSystem
from combat_system import CombatSystem
from components import Renderable, Position, Velocity, HitBox, Input, Health, Animation
from config import Config
from input_system import InputSystem
from maps import Maps
from movement_system import MovementSystem
from physics_system import PhysicsSystem
from render_system import RenderSystem


def run():
    pygame.init()
    window = pygame.display.set_mode(Config.RESOLUTION, flags=pygame.SCALED)
    # pygame.display.set_caption('Unnamed Adventure Game')
    clock = pygame.time.Clock()
    pygame.key.set_repeat(1, 1)

    # Initialize Esper world, and create a "player" Entity with a few Components.
    world = esper.World()

    # Define player entity
    player = world.create_entity()

    world.add_component(player, Velocity(x=0, y=0))
    world.add_component(player, Position(x=350, y=370))
    world.add_component(player, Input())
    world.add_component(player, Health())
    # world.add_component(player, MeleeWeapon(range_front=8, range_side=16, offset=8))

    # Player Animations
    kwargs = {}
    for typ in ['idle', 'move', 'attack']:
        for direction in ['up', 'down', 'left']:
            img_path = Path('assets', 'sprites', 'player', f'{typ}_{direction}.png')
            delay = 4 if typ == 'attack' else 7
            kwargs.update({f'{typ}_{direction}': AnimationStripe(img_path, sprite_width=32, delay=delay)})

    world.add_component(player, Renderable(image=kwargs['idle_down'][0]))
    world.add_component(player, Animation(**kwargs))

    sprite_width = kwargs['idle_down'][0].get_width()
    sprite_height = kwargs['idle_down'][0].get_height()
    scale_offset = - int(sprite_width * 0.50)
    world.add_component(player, HitBox(3, 3, sprite_width, sprite_height, scale_offset))

    # Add map entity
    map_entity = world.create_entity()
    overworld_map = Maps('data/overworld_map.tmx')
    map_surface = overworld_map.create_map_image()
    world.add_component(map_entity, Position(x=0, y=0))
    world.add_component(map_entity, Renderable(image=map_surface, depth=3))

    for position, hitbox in overworld_map.create_solid_rectangles():
        world.create_entity(position, hitbox)

    # Add camera entity
    camera_entity = world.create_entity()
    world.add_component(camera_entity, Position(x=0, y=0))

    # Another motionless enemy entity:
    enemy = world.create_entity()
    enemy_idle_down_image_path = Path('assets', 'sprites', 'enemy', 'jelly_idle.png')
    enemy_idle_animation = AnimationStripe(enemy_idle_down_image_path, sprite_width=16, delay=15)
    world.add_component(enemy, Renderable(image=enemy_idle_animation[0]))
    world.add_component(enemy, Position(x=400, y=400))
    world.add_component(enemy, HitBox(400, 160, 16, 16))
    world.add_component(enemy, Animation(enemy_idle_animation))
    world.add_component(enemy, Health())

    # Create some Processor instances, and assign them to be processed.

    input_processor = InputSystem()
    physics_system = PhysicsSystem()
    render_processor = RenderSystem(window=window, camera_entity=camera_entity)
    animation_system = AnimationSystem()
    movement_processor = MovementSystem(min_x=0, max_x=Config.RESOLUTION[0], min_y=0, max_y=Config.RESOLUTION[1])
    camera_processor = CameraSystem(camera_entity, entity_followed=player)
    combat_system = CombatSystem(player_entity=player)
    world.add_processor(input_processor)
    world.add_processor(animation_system)
    world.add_processor(combat_system)
    world.add_processor(movement_processor)
    world.add_processor(physics_system)
    world.add_processor(camera_processor)
    world.add_processor(render_processor)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        world.process()
        clock.tick(Config.FPS)
