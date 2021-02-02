from typing import List

import pygame
from pygame.math import Vector2

import adventure_game.config as cfg
from adventure_game.action import Action
from adventure_game.animation import PlayerAnimation
from adventure_game.arrow import Arrow
from adventure_game.bow import Bow
from adventure_game.control import Control
from adventure_game.direction import Direction
from adventure_game.enemy import Enemy
from adventure_game.enemy_group import EnemyGroup
from adventure_game.hitbox import Hitbox
from adventure_game.sword import Sword


class Player(pygame.sprite.Sprite):
    HITBOX_DEFLATION = -16
    DAMAGE_MOMENTUM = 2.5

    def __init__(self, group=pygame.sprite.Group()):
        super().__init__(group)
        self.group = group
        self.animation = PlayerAnimation()
        self.life = 10
        self.image = self.animation.current_sprite
        self.rect = self.image.get_rect()
        self.velocity = Vector2(0, 0)
        self.direction = Direction.DOWN
        self.position = Vector2((cfg.DIS_WIDTH // 2, cfg.DIS_HEIGHT // 2))
        self.rect.center = self.position
        self.out_of_bounds = Vector2(0, 0)
        self.cooldown = Action(cfg.COOLDOWN_TIME_PLAYER)
        self.hitbox = Hitbox(self.rect, self.HITBOX_DEFLATION, self.HITBOX_DEFLATION)
        self.sword = Sword(self.rect, attack_duration=len(self.animation.animation_data["attack up"]))
        self.bow = Bow(self.rect, group)

    def update(self, delta: float, control: Control, objects_group: List[pygame.Rect], enemy_group: EnemyGroup):
        self.bow.update(delta, objects_group)
        self.sword.update()
        self.cooldown.update()
        self.handle_input(control)
        self.handle_collision_with_enemy(enemy_group)
        self.handle_collision_with_objects(delta, objects_group)
        self.update_animation()
        self.move(delta)

    def handle_input(self, control: Control):
        if self.cooldown.is_idle() and self.sword.action.is_idle() and self.bow.action.is_idle():
            self.handle_move_input(control)
            self.handle_action_input(control)
            self.update_direction()

    def handle_action_input(self, control: Control):
        if control.attack and not control.previous_frame_action:
            self.sword.attack(self.direction)
            self.velocity[:] = 0, 0
        elif control.shoot and not control.previous_frame_action:
            self.bow.attack(self.direction)
            self.velocity[:] = 0, 0

    def handle_move_input(self, control: Control):
        self.velocity[:] = 0, 0
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

    def update_direction(self):
        if self.velocity.length() == 0:
            return
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
            if self.cooldown.is_idle() and self.hitbox.rect.colliderect(enemy.rect):
                self.get_hit(enemy.position)
                enemy.stay_idle()
            if self.sword.has_hit(enemy):
                enemy.get_hit(self.direction)

    def move(self, delta: float):
        self.position += delta * self.velocity
        self.rect.center = self.position

    def get_hit(self, enemy_position: Vector2):
        self.cooldown.restart()
        self.life -= 1
        vec_difference = self.position - enemy_position
        direction = Direction.closest_direction(vec_difference)
        self.velocity = cfg.VELOCITY * self.DAMAGE_MOMENTUM * direction.value

    def update_animation(self):
        if not self.velocity.elementwise() == 0:
            if self.direction == Direction.UP:
                frame_name = "walk up"
            elif self.direction == Direction.DOWN:
                frame_name = "walk down"
            elif self.direction == Direction.LEFT:
                frame_name = "walk left"
            elif self.direction == Direction.RIGHT:
                frame_name = "walk right"

            self.animation.next_frame(frame_name)

        if self.sword.action.in_progress():
            if self.direction == Direction.UP:
                frame_name = "attack up"
            elif self.direction == Direction.DOWN:
                frame_name = "attack down"
            elif self.direction == Direction.LEFT:
                frame_name = "attack left"
            elif self.direction == Direction.RIGHT:
                frame_name = "attack right"

            self.animation.next_frame(frame_name)

        self.image = self.animation.current_sprite.copy()
