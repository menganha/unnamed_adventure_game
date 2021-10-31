import esper
import pygame

import unnamed_adventure_game.config as cfg
from unnamed_adventure_game.components import Renderable, Position, HitBox, Health


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
                                       key=lambda x: x[1][0].depth, reverse=False):
            health = self.world.try_component(ent, Health)
            if health and health.cool_down_counter > 0:
                flags = pygame.BLEND_RGBA_ADD
            else:
                flags = 0
            self.window.blit(rend.image, (pos.x + camera_pos.x, pos.y + camera_pos.y), special_flags=flags)

        if cfg.DEBUG_MODE:  # On debug mode then render all hitboxes
            for ent, (hitbox) in self.world.get_component(HitBox):
                hb_surface = pygame.Surface((hitbox.rect.w, hitbox.rect.h), flags=pygame.SRCALPHA)
                hb_surface.fill(cfg.C_BLUE)
                self.window.blit(hb_surface, (hitbox.rect.x + camera_pos.x, hitbox.rect.y + camera_pos.y))

        pygame.display.flip()
