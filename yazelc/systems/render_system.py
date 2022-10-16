import pygame

from yazelc import components as cmp
from yazelc import config as cfg
from yazelc import zesper
from yazelc.camera import Camera


class RenderSystem(zesper.Processor):
    def __init__(self, window: pygame.Surface, camera: Camera):
        super().__init__()
        self.camera = camera
        self.window = window

    def process(self):
        self.window.fill(cfg.C_BLACK)

        # Render sprites
        camera_pos = self.camera.pos
        for ent, (rend, pos) in sorted(self.world.get_components(cmp.Renderable, cmp.Position), key=lambda x: x[1][0].depth, reverse=False):

            # TODO: This section feels like it does not belong here ===
            health = self.world.try_component(ent, cmp.Health)
            if health and health.cool_down_counter > 0:
                flags = pygame.BLEND_RGBA_ADD
            else:
                flags = 0
            # =======================================================

            if pos.absolute:  # ition := self.world.try_component(ent, cmp.Position):
                screen_pos = pos
            else:
                screen_pos = pos - camera_pos

            self.window.blit(rend.image, (round(screen_pos.x), round(screen_pos.y)), special_flags=flags)

        # TODO: They can be on the the same loop if the position has the absolute flag on
        # Render native shapes which are (normally) associated with particle effects
        for ent, (vfx, pos) in self.world.get_components(cmp.VisualEffect, cmp.Position):
            rect = pygame.Rect(round(pos.x - camera_pos.x), round(pos.y - camera_pos.y), 1, 1)
            pygame.draw.rect(self.window, vfx.color, rect)

        if cfg.DEBUG_MODE:  # On debug mode then render all hitboxes
            for ent, (hitbox) in self.world.get_component(cmp.HitBox):
                hb_surface = pygame.Surface((hitbox.w, hitbox.h), flags=pygame.SRCALPHA)
                hb_surface.fill(cfg.C_BLUE)
                self.window.blit(hb_surface, (hitbox.x - round(camera_pos.x), hitbox.y - round(camera_pos.y)))

        pygame.display.flip()
