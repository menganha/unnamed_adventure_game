import pygame

import esper
from components import Renderable, Position, HitBox, MeleeWeapon
from config import Config as CFG


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

        # On debug mode then render all hitboxes
        if CFG.DEBUG_MODE:
            for ent, (hitbox) in self.world.get_component(HitBox):
                hb_surface = pygame.Surface((hitbox.rect.w, hitbox.rect.h), flags=pygame.SRCALPHA)
                hb_surface.fill(CFG.C_GREEN)
                self.window.blit(hb_surface, (hitbox.rect.x + camera_pos.x, hitbox.rect.y + camera_pos.y))

                weapon = self.world.try_component(ent, MeleeWeapon)
                if weapon:
                    weapon_surface = pygame.Surface((weapon.rect_h.w, weapon.rect_h.h), flags=pygame.SRCALPHA)
                    weapon_surface.fill(CFG.C_RED)
                    self.window.blit(weapon_surface, (weapon.rect_h.x + camera_pos.x, weapon.rect_h.y + camera_pos.y))

                    weapon_surface = pygame.Surface((weapon.rect_v.w, weapon.rect_v.h), flags=pygame.SRCALPHA)
                    weapon_surface.fill(CFG.C_RED)
                    self.window.blit(weapon_surface, (weapon.rect_v.x + camera_pos.x, weapon.rect_v.y + camera_pos.y))

        pygame.display.flip()
