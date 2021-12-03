from pathlib import Path

import pygame

from yazelc import config as cfg
from yazelc import player


class HUD:
    WHOLE_HEART_HEALTH_POINTS = 2
    HUD_WIDTH = cfg.RESOLUTION[0]
    HUD_HEIGHT = 40
    FULL_HEART_IMAGE_PATH = Path('assets', 'sprites', 'full_heart.png')
    HALF_HEART_IMAGE_PATH = Path('assets', 'sprites', 'half_heart.png')
    EMPTY_HEART_IMAGE_PATH = Path('assets', 'sprites', 'empty_heart.png')
    HEART_OFFSET = 2, 2

    def __init__(self):
        self.full_heart_image = pygame.image.load(self.FULL_HEART_IMAGE_PATH).convert_alpha()
        self.half_heart_image = pygame.image.load(self.HALF_HEART_IMAGE_PATH).convert_alpha()
        self.empty_heart_image = pygame.image.load(self.EMPTY_HEART_IMAGE_PATH).convert_alpha()
        self.hud_surface = pygame.surface.Surface((self.HUD_WIDTH, self.HUD_HEIGHT), flags=pygame.SRCALPHA)

    def update_surface(self, health_points: int):
        # Clear surface
        # updates other aspects of the hud
        # ...
        # updates hearts
        num_whole_hearts, num_medium_hearts = divmod(health_points, self.WHOLE_HEART_HEALTH_POINTS)
        index = 0
        for idx in range(num_whole_hearts):
            index = idx
            self.hud_surface.blit(self.full_heart_image,
                                  (index * self.full_heart_image.get_width() + self.HEART_OFFSET[0], self.HEART_OFFSET[1]))
        for idx in range(num_medium_hearts):
            index += 1
            self.hud_surface.blit(self.half_heart_image,
                                  (index * self.half_heart_image.get_width() + self.HEART_OFFSET[0], self.HEART_OFFSET[1]))
        for idx in range(player.MAX_HEALTH // 2 - num_medium_hearts - num_whole_hearts):
            index += 1
            self.hud_surface.blit(self.empty_heart_image,
                                  (index * self.empty_heart_image.get_width() + self.HEART_OFFSET[0], self.HEART_OFFSET[1]))
