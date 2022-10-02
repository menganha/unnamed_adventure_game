"""
Contains the details of getting a key and opening a locked door
"""

import sys

import pygame

pygame.init()
pygame.freetype.init()

from yazelc import config as cfg
from yazelc import scene_manager
from demos.key_and_door.scene import Scene

if __name__ == '__main__':
    window = pygame.display.set_mode((cfg.RESOLUTION.x, cfg.RESOLUTION.y), pygame.SCALED, vsync=1)
    gameplay_scene = Scene(window)
    scene_manager.run_game_loop(initial_scene=gameplay_scene)
    pygame.quit()
    sys.exit(0)
