import pygame

from ecs_src import esper
from ecs_src.components import Renderable, Position


class RenderSystem(esper.Processor):
    def __init__(self, window, clear_color=(0, 0, 0)):
        super().__init__()
        self.window = window
        self.clear_color = clear_color

    def process(self):
        # Clear the window:
        self.window.fill(self.clear_color)
        # This will iterate over every Entity that has this Component, and blit it:
        for ent, (rend, pos) in self.world.get_components(Renderable, Position):
            self.window.blit(rend.image, (pos.x, pos.y))
        # Flip the framebuffers
        pygame.display.flip()
