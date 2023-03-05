import logging
import sys
from pathlib import Path

import pygame

from yazelc.gamepad import Gamepad
from yazelc.keyboard import Keyboard

pygame.init()
pygame.freetype.init()
pygame.mixer.init()

from yazelc import config as cfg
from yazelc import scene_manager
from yazelc.scenes.gameplay_scene import GameplayScene
from yazelc.utils.game_utils import ImmutableVec

INITIAL_MAP = Path('data', 'overworld', 'overworld_1.tmx')
INITIAL_POS = ImmutableVec(10, 24)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    if len(sys.argv) == 4:
        map_path = Path(sys.argv[1])
        initial_pos_x = int(sys.argv[2])
        initial_pos_y = int(sys.argv[3])
    else:
        map_path = INITIAL_MAP
        initial_pos_x = INITIAL_POS.x
        initial_pos_y = INITIAL_POS.y
    window = pygame.display.set_mode((cfg.RESOLUTION.x, cfg.RESOLUTION.y), pygame.SCALED, vsync=1)

    # Get the main input device
    pygame.joystick.init()
    if pygame.joystick.get_count():
        controller = Gamepad(pygame.joystick.Joystick(0))
        logging.info('Using gamepad controller')
    else:
        controller = Keyboard()
        pygame.joystick.quit()
        logging.info('Using keyboard controller')

    gameplay_scene = GameplayScene(window, controller, map_path, initial_pos_x, initial_pos_y)
    scene_manager.run_game_loop(initial_scene=gameplay_scene)
    pygame.quit()
