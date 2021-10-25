"""
Stores all the game globals
"""
import pygame

from scenes.house import HouseScene
from scenes.overworld import OverWorldScene

FPS = 60
RESOLUTION = 256, 224
DEBUG_MODE = False
C_GREEN = pygame.Color(0, 255, 0, 70)
C_RED = pygame.Color(200, 0, 0, 70)
C_BLUE = pygame.Color(0, 0, 255, 70)
SCENES = {'overworld': OverWorldScene, 'house': HouseScene}
