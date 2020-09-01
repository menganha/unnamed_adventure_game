import sys

import pygame

import adventure_game.config as cfg
from adventure_game.control import Control
from adventure_game.enemy import EnemyGroup
from adventure_game.player import Player
from adventure_game.text import Text
from adventure_game.world import World


class Game():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Untitled Adventure Game')
        self.display = pygame.display.set_mode((cfg.DIS_WIDTH, cfg.DIS_HEIGHT))
        self.clock = pygame.time.Clock()
        self.exit = False
        self.control = Control()
        self.player = Player()
        self.world = World()
        self.enemies = EnemyGroup(self.world.current_map)
        self.generic_container = pygame.sprite.Group(self.player)
        self.font = pygame.font.Font("./assets/font/PressStart2P.ttf", 8)
        self.debug_text = Text(self.font, str(self.player.life))
        self.delta = 0
        self.fps = 0

    def game_loop(self):
        while not self.exit:

            self.delta = self.clock.tick(cfg.FRAMERATE) / 1000
            # self.delta = self.clock.tick_busy_loop(cfg.FRAMERATE) / 1000
            self.delta = 1 / cfg.FRAMERATE

            # Handle Input
            self.control.handle_input()
            self.exit = self.control.exit

            # Update
            self.generic_container.update(
                self.delta, self.control,
                self.world.in_transition,
                self.world.solid_objects,
                self.enemies)
            self.world.update(self.delta, self.player.out_of_bounds)
            self.enemies.update(
                self.delta,
                self.world.current_map,
                self.world.in_transition,
                self.world.solid_objects)
            self.debug_text.text = str(self.player.life)
            self.debug_text.reRender()

            # Render
            self.world.draw(self.display)
            # self.display.blit(self.player.red_surface, self.player.position + (8, 8))
            self.generic_container.draw(self.display)
            self.enemies.draw(self.display)
            self.display.blit(self.player.sword_hitbox.image, self.player.sword_hitbox.position)
            self.display.blit(self.player.hitbox.image, self.player.hitbox.position)
            self.debug_text.draw(self.display)
            pygame.display.update()

        pygame.quit()
        sys.exit(0)
