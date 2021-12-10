"""
Stores all the game globals
"""
import pygame

from yazelc.utils.game_utils import ImmutableVec

RESOLUTION = ImmutableVec(256, 224)
DEBUG_MODE = False

C_BLACK = pygame.Color(0, 0, 0)
C_WHITE = pygame.Color(255, 255, 255)
C_GREEN = pygame.Color(0, 255, 0, 70)
C_RED = pygame.Color(200, 0, 0, 70)
C_BLUE = pygame.Color(0, 0, 255, 70)
C_TRANSPARENT = pygame.Color(0, 0, 0, 0)
