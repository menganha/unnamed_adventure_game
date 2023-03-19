"""
Stores all the game globals
"""
import pygame

from yazelc.utils.game_utils import IVec

RESOLUTION = IVec(272, 240)
TILE_WIDTH = 16
DEBUG_MODE = False

C_BLACK = pygame.Color(0, 0, 0)
C_WHITE = pygame.Color(255, 255, 255)
C_GREEN = pygame.Color(0, 255, 0)
C_RED = pygame.Color(255, 0, 0)
C_LIGHT_RED = pygame.Color(255, 0, 0)
C_GREY = pygame.Color(136, 139, 141, 0)
C_BLUE = pygame.Color(0, 0, 255)
C_LIGHT_BLUE = pygame.Color(0, 0, 255)
C_YELLOW = pygame.Color(255, 255, 0)
C_TRANSPARENT = pygame.Color(0, 0, 0, 0)
C_TRANSPARENT_BLUE = pygame.Color(0, 0, 255, 90)
