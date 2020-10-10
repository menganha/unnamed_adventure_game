import sys

import pygame

import adventure_game.config as cfg
import adventure_game.utilities as utils
from adventure_game.control import Control
from adventure_game.enemy import EnemyGroup
from adventure_game.player import Player
from adventure_game.text import Text
from adventure_game.world import World
from adventure_game.user_interface import UserInterface


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Untitled Adventure Game")
        self.screen = pygame.display.set_mode((cfg.DIS_WIDTH * cfg.SCALE, cfg.DIS_HEIGHT * cfg.SCALE))
        self.display = pygame.Surface((cfg.DIS_WIDTH, cfg.DIS_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("./assets/font/PressStart2P.ttf", 8)
        self.exit = False
        self.control = Control()
        self.player = Player()
        self.world = World()
        self.ui = UserInterface(self.display, self.font)
        self.enemies = EnemyGroup(self.world.current_map)
        self.player_container = pygame.sprite.Group(self.player)
        self.debug_text = Text(self.font, str(self.player.life))
        self.delta = 0
        self.fps = 0

    def game_loop(self):
        while not self.exit:

            self.delta = self.clock.tick(cfg.FRAMERATE) / 1000
            self.delta = 1 / cfg.FRAMERATE

            # Handle Input
            self.control.handle_input()
            self.exit = self.control.exit

            # Update
            self.world.update(self.delta, self.player.out_of_bounds)
            self.ui.update(self.player.life)
            self.player_container.update(
                self.delta,
                self.control,
                self.world.in_transition,
                self.world.solid_objects,
                self.enemies,
            )
            self.enemies.update(
                self.delta,
                self.world.current_map,
                self.world.in_transition,
                self.world.solid_objects,
                self.player
            )

            # Render
            self.world.draw(self.display)
            ui_rects = self.ui.draw(self.display)
            self.player_container.draw(self.display)
            self.enemies.draw(self.display)
            self.display.blit(self.player.sword_hitbox.image, self.player.sword_hitbox.position)
            self.display.blit(self.player.hitbox.image, self.player.hitbox.position)
            self.screen.blit(
                pygame.transform.scale(self.display, (cfg.DIS_WIDTH * 2, cfg.DIS_HEIGHT * 2)),
                (0, 0),
            )
            # TODO -- Improve this mess
            updated_rectangles = [utils.scale_rects(rects, cfg.SCALE) for rects in ui_rects]
            updated_rectangles = updated_rectangles + [
                pygame.Rect(0, cfg.UI_HEIGHT * 2, cfg.WORLD_WIDTH * 2, cfg.WORLD_HEIGTH * 2)
            ]
            # --
            pygame.display.update(updated_rectangles)

        pygame.quit()
        sys.exit(0)
