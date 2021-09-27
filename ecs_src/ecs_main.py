import pygame
from ecs_src import esper
from ecs_src.components import Renderable, Position, Velocity
from ecs_src.render_processor import RenderProcessor
from ecs_src.movement_processor import MovementProcessor


FPS = 60
RESOLUTION = 640, 480


def run():
    pygame.init()
    window = pygame.display.set_mode(RESOLUTION, flags=pygame.SCALED)
    pygame.display.set_caption('Unnamed Adventure Game')
    clock = pygame.time.Clock()
    BLUE = pygame.Color(50, 153, 213)
    WHITE = pygame.Color(255, 255, 255)
    pygame.key.set_repeat(1, 1)

    # Initialize Esper world, and create a "player" Entity with a few Components.
    world = esper.World()
    player = world.create_entity()
    world.add_component(player, Velocity(x=0, y=0))

    player_surface = pygame.Surface((16, 16))
    player_surface.fill(BLUE)

    world.add_component(player, Renderable(image=player_surface))
    world.add_component(player, Position(x=100, y=100))

    # Another motionless Entity:
    enemy_surface = pygame.Surface((10, 10))
    enemy_surface.fill(WHITE)
    enemy = world.create_entity()
    world.add_component(enemy, Renderable(image=enemy_surface))
    world.add_component(enemy, Position(x=400, y=100))

    # Create some Processor instances, and assign them to be processed.
    render_processor = RenderProcessor(window=window)
    movement_processor = MovementProcessor(min_x=0, max_x=RESOLUTION[0], min_y=0, max_y=RESOLUTION[1])
    world.add_processor(render_processor)
    world.add_processor(movement_processor)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    world.component_for_entity(player, Velocity).x = -3
                elif event.key == pygame.K_RIGHT:
                    world.component_for_entity(player, Velocity).x = 3
                elif event.key == pygame.K_UP:
                    world.component_for_entity(player, Velocity).y = -3
                elif event.key == pygame.K_DOWN:
                    world.component_for_entity(player, Velocity).y = 3
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    world.component_for_entity(player, Velocity).x = 0
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    world.component_for_entity(player, Velocity).y = 0

        # A single call to world.process() will update all Processors:
        world.process()
        clock.tick(FPS)


if __name__ == "__main__":
    run()
    pygame.quit()
