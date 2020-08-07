import pygame
import sys
import adventure_game.config as cfg
from adventure_game.player import Player
from adventure_game.control import Control
from adventure_game.world import World
from adventure_game.text import Text


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
        self.all_sprites.add(self.player)
        self.font = pygame.font.Font("./assets/font/PressStart2P.ttf", 8)
        self.debug_text = Text(self.font)
        self.pos_text = Text(self.font)
        self.delta = 0

    def game_loop(self):
        while not self.exit:

            self.delta = self.clock.tick(cfg.FRAMERATE) / 1000

            # Debugging
            self.debug_text.text = "vX, vY: {:}, {:}, {:}, {:}".format(
                self.player.velX, self.player.velY,
                int(self.delta * self.player.velX * cfg.FRAMERATE),
                int(self.delta * self.player.velY * cfg.FRAMERATE),
                )
            self.pos_text.text = "X, Y: {:.2}, {:.2}".format(
                self.player.rect.x/cfg.FRAMERATE, self.player.rect.y/cfg.FRAMERATE
                )
            self.pos_text.tY = 20
            self.debug_text.reRender()
            self.pos_text.reRender()

            # Handle Input
            self.control.handle_input()
            self.exit = self.control.exit

            # Update
            self.all_sprites.update(
                1/cfg.FRAMERATE, self.control, self.world.solid_objects, self.world.in_transition
                )
            self.world.update(self.player.out_of_bounds)
            #self.all_sprites.update(self.delta, self.control)

            # Render
            self.display.fill(cfg.WHITE)
            self.debug_text.draw(self.display)
            self.world.draw(self.display)
            self.all_sprites.draw(self.display)
            self.pos_text.draw(self.display)
            pygame.display.update()

        pygame.quit()
        sys.exit(0)
