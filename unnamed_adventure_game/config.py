"""
Stores all the game globals
"""
import pygame

RESOLUTION = 256, 224
DEBUG_MODE = False

C_BLACK = pygame.Color(0, 0, 0)
C_WHITE = pygame.Color(255, 255, 255)
C_GREEN = pygame.Color(0, 255, 0, 70)
C_RED = pygame.Color(200, 0, 0, 70)
C_BLUE = pygame.Color(0, 0, 255, 70)

# MAIN PLAYER PROPERTIES

# This ensures that the rounding produces the displacement pattern 1,2,1,2.. that averages a velocity of 1.5
VELOCITY = 1.5 - 1.e-8
VELOCITY_DIAGONAL = 1

# SWORD PROPERTIES
SWORD_FRONT_RANGE = 5
SWORD_SIDE_RANGE = 20
SWORD_DAMAGE = 5
SWORD_ACTIVE_FRAMES = 20
