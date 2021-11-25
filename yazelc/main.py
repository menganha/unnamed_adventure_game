import logging

import pygame

from yazelc import config as cfg
from yazelc.scenes.gameplay_scene import GameplayScene

INITIAL_MAP = 'overworld'


def run_game():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    pygame.init()
    window = pygame.display.set_mode(cfg.RESOLUTION, pygame.SCALED, vsync=1)

    current_scene = GameplayScene(window, INITIAL_MAP, 26, 28)
    running = True
    while running:
        current_scene.on_enter()
        current_scene.run()
        current_scene.on_exit()
        current_scene = current_scene.next_scene
        if not current_scene:
            running = False

    pygame.quit()
