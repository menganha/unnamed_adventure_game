import esper
import pygame

import unnamed_adventure_game.components as cmp
import unnamed_adventure_game.config as cfg


class RenderSystem(esper.Processor):
    def __init__(self, window, camera_entity: int, clear_color=(0, 0, 0)):
        super().__init__()
        self.window = window
        self.camera_entity = camera_entity
        self.clear_color = clear_color

    def process(self):
        self.window.fill(self.clear_color)
        camera_pos = self.world.component_for_entity(self.camera_entity, cmp.Position)

        # Render sprites
        for ent, (rend, pos) in sorted(self.world.get_components(cmp.Renderable, cmp.Position),
                                       key=lambda x: x[1][0].depth, reverse=False):
            health = self.world.try_component(ent, cmp.Health)
            if health and health.cool_down_counter > 0:
                flags = pygame.BLEND_RGBA_ADD
            else:
                flags = 0
            self.window.blit(rend.image, (round(pos.x + camera_pos.x), round(pos.y + camera_pos.y)), special_flags=flags)

        # Render native shapes which are (normally) associated with particle effects
        for ent, (vfx, pos) in self.world.get_components(cmp.VisualEffectTag, cmp.Position):
            pygame.draw.circle(self.window, vfx.color, (round(pos.x + camera_pos.x), round(pos.y + camera_pos.y)), radius=1)

        if cfg.DEBUG_MODE:  # On debug mode then render all hitboxes
            for ent, (hitbox) in self.world.get_component(cmp.HitBox):
                hb_surface = pygame.Surface((hitbox.rect.w, hitbox.rect.h), flags=pygame.SRCALPHA)
                hb_surface.fill(cfg.C_BLUE)
                self.window.blit(hb_surface, (hitbox.rect.x + round(camera_pos.x), hitbox.rect.y + round(camera_pos.y)))

        pygame.display.flip()
