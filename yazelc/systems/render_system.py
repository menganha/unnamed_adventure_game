import pygame

from yazelc import components as cmp
from yazelc import config as cfg
from yazelc import zesper


class RenderSystem(zesper.Processor):
    def __init__(self, window: pygame.Surface, camera_entity_id: int = None):
        self.camera_entity_id = camera_entity_id
        self.window = window

    def process(self):
        self.window.fill(cfg.C_BLACK)
        if self.camera_entity_id:
            camera_pos = self.world.component_for_entity(self.camera_entity_id, cmp.Position)
        else:
            camera_pos = cmp.Position()

        # Render sprites
        for ent, rend in sorted(self.world.get_component(cmp.Renderable), key=lambda x: x[1].depth, reverse=False):

            # TODO: This section feels like it does not belong here ===
            health = self.world.try_component(ent, cmp.Health)
            if health and health.cool_down_counter > 0:
                flags = pygame.BLEND_RGBA_ADD
            else:
                flags = 0
            # =======================================================

            if position := self.world.try_component(ent, cmp.Position):
                screen_pos = position - camera_pos
            else:
                screen_pos = cmp.Position()

            self.window.blit(rend.image, (round(screen_pos.x), round(screen_pos.y)), special_flags=flags)

        # Render native shapes which are (normally) associated with particle effects
        for ent, (vfx, pos) in self.world.get_components(cmp.VisualEffect, cmp.Position):
            rect = pygame.Rect(round(pos.x - camera_pos.x), round(pos.y - camera_pos.y), 1, 1)
            pygame.draw.rect(self.window, vfx.color, rect)

        if cfg.DEBUG_MODE:  # On debug mode then render all hitboxes
            for ent, (hitbox) in self.world.get_component(cmp.HitBox):
                hb_surface = pygame.Surface((hitbox.rect.w, hitbox.rect.h), flags=pygame.SRCALPHA)
                hb_surface.fill(cfg.C_BLUE)
                self.window.blit(hb_surface, (hitbox.rect.x - round(camera_pos.x), hitbox.rect.y - round(camera_pos.y)))

        pygame.display.flip()
