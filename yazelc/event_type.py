from enum import Enum

import pygame


class EventType(Enum):
    DEATH = pygame.event.custom_type()
    PAUSE = pygame.event.custom_type()
    COLLISION = pygame.event.custom_type()
    HUD_UPDATE = pygame.event.custom_type()
    RESTART = pygame.event.custom_type()
