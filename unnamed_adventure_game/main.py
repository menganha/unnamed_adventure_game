import logging

import pygame

import unnamed_adventure_game.config as cfg
from unnamed_adventure_game.scenes import OverWorldScene


def run_game():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    pygame.init()
    pygame.font.init()
    window = pygame.display.set_mode(cfg.RESOLUTION, pygame.SCALED, vsync=1)

    current_scene = OverWorldScene(window, 26, 28)
    running = True
    while running:
        current_scene.on_enter()
        current_scene.run()
        current_scene.on_exit()
        current_scene = current_scene.next_scene
        if not current_scene:
            running = False

    pygame.quit()
