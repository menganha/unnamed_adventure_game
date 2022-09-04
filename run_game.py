import logging

import pygame

pygame.init()
pygame.freetype.init()

from yazelc import config as cfg
from yazelc import scene_manager
from yazelc.scenes.gameplay_scene import GameplayScene
from yazelc.utils.game_utils import ImmutableVec

INITIAL_MAP = 'overworld'
INITIAL_POS = ImmutableVec(27, 24)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    window = pygame.display.set_mode((cfg.RESOLUTION.x, cfg.RESOLUTION.y), pygame.SCALED, vsync=1)
    gameplay_scene = GameplayScene(window, INITIAL_MAP, INITIAL_POS.x, INITIAL_POS.y)
    scene_manager.run_game_loop(initial_scene=gameplay_scene)
    pygame.quit()
