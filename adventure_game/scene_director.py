import re

from pygame.math import Vector2

import adventure_game.config as cfg
from adventure_game.direction import Direction
from adventure_game.enemy_group import EnemyGroup
from adventure_game.player import Player
from adventure_game.world import World


class SceneDirector:
    """
    Manages all the changes necessary for transitioning into a new map chunk
    """
    VELOCITY_PLUS = 0.03

    def __init__(self, player: Player, world: World, enemy_group: EnemyGroup):
        self.player = player
        self.world = world
        self.enemy_group = enemy_group
        self.in_transition = False
        self.transition_direction = None

    def update(self, delta: float):
        if not self.in_transition:
            self.in_transition = True
            self._load_new_map()
            self.enemy_group.empty()
        self._scroll_player(delta)
        self._scroll_map(delta)
        if self._scroll_has_completed():
            self._load_enemies()
            self.world.offset = Vector2(0, 0)
            self.world.map_image = self.world.map_image_cache.copy()
            self.in_transition = False

    def under_control(self) -> bool:
        if not self.in_transition:
            self._get_transition_direction()
            return self.transition_direction is not None
        else:
            return True

    def _get_transition_direction(self):
        self.transition_direction = None
        if self.player.position.x > cfg.WORLD_WIDTH:
            self.transition_direction = Direction.RIGHT
        elif self.player.position.x < 0:
            self.transition_direction = Direction.LEFT
        elif self.player.position.y > cfg.WORLD_HEIGTH:
            self.transition_direction = Direction.DOWN
        elif self.player.position.y < cfg.UI_HEIGHT:
            self.transition_direction = Direction.UP

    def _scroll_player(self, delta: float):
        self.player.velocity = - cfg.SCROLL_VELOCITY * (1 - self.VELOCITY_PLUS) * self.player.direction.value
        self.player.update_animation()
        self.player.move(delta)

    def _scroll_map(self, delta: float):
        self.world.move(delta, cfg.SCROLL_VELOCITY, self.transition_direction.opposite())

    def _scroll_has_completed(self):
        return abs(self.world.offset.x) > cfg.WORLD_WIDTH or abs(self.world.offset.y) > cfg.WORLD_HEIGTH

    def _load_new_map(self):
        self._get_next_map_data_file()
        self.world.load_map()
        self.world.arrange_world(in_cache=True)
        self.world.offset_cache = self.transition_direction.value.elementwise() * Vector2(cfg.WORLD_WIDTH,
                                                                                          cfg.WORLD_HEIGTH)

    def _load_enemies(self):
        self.enemy_group.get_enemy_positions(self.world.map_data_file)
        self.enemy_group.create_enemies()

    def _get_next_map_data_file(self):
        match = re.match(r'data/level-x0(\d+)-y0(\d+)\.json', self.world.map_data_file)
        x = int(match.group(1)) + int(self.transition_direction.value.x)
        y = int(match.group(2)) - int(self.transition_direction.value.y)
        self.world.map_data_file = 'data/level-x0{:d}-y0{:d}.json'.format(x, y)
