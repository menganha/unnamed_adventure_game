from typing import List

import pygame
from pygame.math import Vector2

import adventure_game.config as cfg
from adventure_game.action import Action
from adventure_game.bow import Bow
from adventure_game.control import Control
from adventure_game.direction import Direction
from adventure_game.enemy import Enemy
from adventure_game.enemy_group import EnemyGroup
from adventure_game.hitbox import Hitbox
from adventure_game.player_sprite import PlayerSprite
from adventure_game.state import State
from adventure_game.sword import Sword


class Player:
    HITBOX_DEFLATION = -16
    DAMAGE_MOMENTUM = 2.5
    COOLDOWN_TIME = 10

    def __init__(self):
        self.life = 10
        self.position = Vector2((cfg.DIS_WIDTH // 2, cfg.DIS_HEIGHT // 2))
        self.velocity = Vector2(0, 0)
        self.state = State.IDLE
        self.direction = Direction.DOWN
        self.sprite_group = pygame.sprite.Group()
        self.sprite = PlayerSprite(self.position, self.direction, self.state, self.sprite_group)
        self.hitbox = Hitbox(self.sprite.rect, self.HITBOX_DEFLATION, self.HITBOX_DEFLATION)
        self.cooldown = Action(self.COOLDOWN_TIME)
        self.sword = Sword(self.sprite.rect)
        self.bow = Bow(self.sprite.rect, self.sprite_group)

    def update(self, delta: float, control: Control, objects_group: List[pygame.Rect], enemy_group: EnemyGroup):
        self.bow.update(delta, objects_group)
        self.sword.update()
        self.cooldown.update()
        if self.cooldown.is_idle() and self.sword.action.is_idle() and self.bow.action.is_idle():
            self.handle_input(control)
        self.handle_collision_with_enemy(enemy_group)
        self.handle_collision_with_objects(delta, objects_group)
        self.move(delta)

    def handle_input(self, control: Control):
        self.velocity[:] = 0, 0

        if control.attack:
            self.sword.attack(self.direction)
            self.state = State.ATTACK
            return
        if control.shoot:
            self.bow.attack(self.direction)
            self.state = State.IDLE
            return
        if control.up:
            self.velocity.y = -cfg.VELOCITY
        if control.down:
            self.velocity.y = cfg.VELOCITY
        if control.left:
            self.velocity.x = -cfg.VELOCITY
        if control.right:
            self.velocity.x = cfg.VELOCITY

        if self.velocity.elementwise() != 0:
            self.velocity = 0.7071 * self.velocity

        if self.velocity.length_squared() == 0:
            self.state = State.IDLE
        else:
            self.state = State.WALK
            self.update_direction()

    def update_direction(self):
        if self.velocity.y == 0:
            if self.velocity.x > 0:
                self.direction = Direction.RIGHT
            else:
                self.direction = Direction.LEFT
        elif self.velocity.x == 0:
            if self.velocity.y > 0:
                self.direction = Direction.DOWN
            else:
                self.direction = Direction.UP

    def handle_collision_with_objects(self, delta: float, physical_objects: List[pygame.Rect]):
        for idx, vec in enumerate((Vector2(1, 0), Vector2(0, 1))):
            self.hitbox.move_with_respect_to_parent(self.position + delta * (self.velocity.elementwise() * vec))
            if self.hitbox.has_collided_with_rects(*physical_objects):
                self.velocity[idx] = 0

    def handle_collision_with_enemy(self, enemy_group: EnemyGroup):
        enemy: Enemy
        for enemy in enemy_group:
            if self.cooldown.is_idle() and self.hitbox.has_collided_with(enemy.hitbox):
                self.get_hit(enemy.position)
                enemy.stay_idle()
            if self.sword.has_hit(enemy):
                enemy.get_hit(self.direction)
            for arrow in self.bow.quiver:
                if arrow.has_hit(enemy):
                    enemy.get_hit(arrow.direction)
                    arrow.kill()

    def get_hit(self, enemy_position: Vector2):
        self.cooldown.restart()
        self.life -= 1
        vec_difference = self.position - enemy_position
        direction = Direction.closest_direction(vec_difference)
        self.velocity = cfg.VELOCITY * self.DAMAGE_MOMENTUM * direction.value

    def move(self, delta: float):
        self.position.update(self.position + delta * self.velocity)
        self.sprite.update(self.direction, self.position, self.velocity, self.state)
