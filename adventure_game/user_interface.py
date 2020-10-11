import pygame
import adventure_game.config as cfg


class UserInterface:
    SIDE_MARGIN = 4

    def __init__(self, target_display, font):
        self.container = pygame.sprite.LayeredDirty()
        # TODO: Introduce a background class with all the elements that are going to be
        # constant
        self.background = Background(font)
        self.hearts = HeartContainers(self.container)
        self.container.clear(target_display, self.background.surface)

    def update(self, player_life):
        self.container.update(player_life)

    def draw(self, target_display):
        return self.container.draw(target_display)


class Background:
    """
    Contains all static (non-changing) UI elements
    """

    def __init__(self, font):
        self.surface = pygame.Surface((cfg.UI_WIDTH, cfg.UI_HEIGHT)).convert()
        self.surface.fill(cfg.BLACK)
        self.font = font

        life_text = font.render("--LIFE--", False, cfg.WHITE, cfg.BLACK)
        self.surface.blit(life_text, (UserInterface.SIDE_MARGIN, 4))

        life_text = font.render("--WEAPON--", False, cfg.WHITE, cfg.BLACK)
        self.surface.blit(life_text, (UserInterface.SIDE_MARGIN + 100, 4))

        life_text = font.render("--ITEM--", False, cfg.WHITE, cfg.BLACK)
        self.surface.blit(life_text, (UserInterface.SIDE_MARGIN + 200, 4))

        life_text = font.render("--GOLD--", False, cfg.WHITE, cfg.BLACK)
        self.surface.blit(life_text, (UserInterface.SIDE_MARGIN + 300, 4))

class HeartContainers(pygame.sprite.DirtySprite):
    """
    Handle the heart sprites in the. A full heart contains 2 heart units.
    """

    def __init__(self, container, max_hearts=5, heart_units=10):
        super().__init__(container)
        self.heart_image_size = (15, 15)
        self.full_heart_image = pygame.image.load("assets/sprites/full_heart.png").convert_alpha()
        self.half_heart_image = pygame.image.load("assets/sprites/half_heart.png").convert_alpha()
        self.empty_heart_image = pygame.image.load("assets/sprites/empty_heart.png").convert_alpha()
        self.max_hearts = max_hearts
        self.heart_units = heart_units
        self.image = self.get_max_hearts_background_image()
        self.rect = self.image.get_rect()
        self.rect.move_ip(UserInterface.SIDE_MARGIN, self.heart_image_size[1] - 2)
        self.update(0)
        self.dirty = 1

    def get_max_hearts_background_image(self):
        height = self.heart_image_size[1]
        width = self.heart_image_size[0] * self.max_hearts
        surface = pygame.Surface((width, height)).convert()
        surface.fill(cfg.BLACK)
        return surface

    def update(self, player_life):
        if player_life != self.heart_units:
            self.heart_units = player_life
            self.image = self.get_max_hearts_background_image()

            full_hearts = self.heart_units // 2
            half_heart = self.heart_units % 2

            for heart_idx in range(self.max_hearts):
                if heart_idx < full_hearts:
                    self.image.blit(self.full_heart_image, (self.heart_image_size[0] * heart_idx, 0))
                elif half_heart:
                    self.image.blit(self.half_heart_image, (self.heart_image_size[0] * heart_idx, 0))
                    half_heart = 0
                else:
                    self.image.blit(self.empty_heart_image, (self.heart_image_size[0] * heart_idx, 0))

            self.dirty = 1
