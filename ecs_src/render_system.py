import pygame

import esper
from components import Renderable, Position


class RenderSystem(esper.Processor):
    def __init__(self, window, camera_entity: int, clear_color=(0, 0, 0)):
        super().__init__()
        self.window = window
        self.camera_entity = camera_entity
        self.clear_color = clear_color

    def process(self):
        self.window.fill(self.clear_color)
        camera_pos = self.world.component_for_entity(self.camera_entity, Position)
        for ent, (rend, pos) in sorted(self.world.get_components(Renderable, Position),
                                       key=lambda x: x[1][0].depth, reverse=True):
            self.window.blit(rend.image, (pos.x + camera_pos.x, pos.y + camera_pos.y))
        pygame.display.flip()
