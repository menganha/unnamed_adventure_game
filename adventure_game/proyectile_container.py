import pygame


class ProyectileContainer(pygame.sprite.Group):

    def __init__(self, *sprites):
        super().__init__(*sprites)
        self.proyectile_image = pygame.image.load('assets/sprites/arrow.png').convert_alpha()
