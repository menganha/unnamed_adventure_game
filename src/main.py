import logging

import pygame

import config as cfg
from scenes.overworld import OverWorldScene


def run_game():
    logging.basicConfig(level=logging.INFO)
    pygame.init()
    window = pygame.display.set_mode(cfg.RESOLUTION, flags=pygame.SCALED, vsync=1)

    current_scene = OverWorldScene(window, 24, 28)
    running = True
    while running:
        current_scene.on_enter()
        current_scene.run()
        current_scene.on_exit()
        current_scene = current_scene.next_scene
        if not current_scene:
            running = False

    pygame.quit()
