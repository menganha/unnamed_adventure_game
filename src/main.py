import pygame

from config import Config
from scenes.overworld import OverWorldScene

pygame.init()
window = pygame.display.set_mode(Config.RESOLUTION, flags=pygame.SCALED, vsync=1)


def run_game():
    initial_scene = OverWorldScene(window)
    current_scene = initial_scene
    running = True
    while running:
        current_scene.on_enter()
        current_scene.run()
        current_scene.on_exit()
        current_scene = current_scene.next_scene
        if not current_scene:
            running = False
