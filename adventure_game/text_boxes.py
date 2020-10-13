from adventure_game import config as cfg
import pygame


class TextBox(pygame.sprite.Sprite):
    def __init__(self, font: pygame.font.Font, message: str):
        self.font = font
        self.message = message
        self.image = pygame.Surface(300, 100)
        self.rect = self.image.get_rect().move(200, 100)
        message_rendered = font.render(message, False, cfg.WHITE)
        self.image.blit(message_rendered, (0, 0))

    def something(self):
        pass