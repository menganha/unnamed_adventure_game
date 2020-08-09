import pygame
import sys
import adventure_game.config as cfg
from adventure_game.player import Player
from adventure_game.control import Control
from adventure_game.world import World
from adventure_game.text import Text
from adventure_game.enemy import EnemyGroup


class Game():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Untitled Dog Game')
        self.display = pygame.display.set_mode((cfg.DIS_WIDTH, cfg.DIS_HEIGHT))
        self.clock = pygame.time.Clock()
        self.exit = False
        self.control = Control()
        self.all_sprites = pygame.sprite.Group()
        self.player = Player()
        self.world = World()
        self.enemies = EnemyGroup(self.world.current_map)
        self.font = pygame.font.Font("./assets/font/PressStart2P.ttf", 8)
        self.debug_text = Text(self.font)
        self.delta = 0

    def game_loop(self):
        while not self.exit:

            self.delta = self.clock.tick(cfg.FRAMERATE) / 1000

            # Handle Input
            self.control.handle_input()
            self.exit = self.control.exit

            # Update
            self.player.update(1/cfg.FRAMERATE, self.control,
                               self.world.in_transition,
                               self.world.solid_objects,
                               self.enemies)
            self.world.update(self.player.out_of_bounds)
            self.enemies.update(self.world.current_map, self.world.in_transition)

            # Render
            self.display.fill(cfg.WHITE)
            self.debug_text.draw(self.display)
            self.world.draw(self.display)
            self.player.draw(self.display)
            self.enemies.draw(self.display)
            pygame.display.update()

        pygame.quit()
        sys.exit(0)
