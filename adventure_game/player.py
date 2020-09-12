from math import copysign

import pygame
from pygame.math import Vector2

import adventure_game.config as cfg
from adventure_game.animation import PlayerAnimation
from adventure_game.control import Control
from adventure_game.hitbox import Hitbox, SwordHitbox


class Player(pygame.sprite.Sprite):
    hitbox_deflation = 16

    def __init__(self):
        super().__init__()
        self.animation = PlayerAnimation()
        self.life = 5
        self.image = self.animation.current_sprite
        self.rect = self.image.get_rect()
        self.rect.center = (cfg.DIS_WIDTH // 2, cfg.DIS_HEIGHT // 2)
        self.hitbox = Hitbox(
            tuple(ele - self.hitbox_deflation for ele in self.rect.size)
        )
        self.hitbox.get_offset(self.rect.size)
        self.sword_hitbox = SwordHitbox(20, 40, 10, self.rect.size)
        self.sword_hitbox.get_offset(self.rect.size)
        # Temporary render the hitbox image as a red rectangle for debugging
        self.hitbox.set_image(cfg.RED)
        self.sword_hitbox.set_image(cfg.BLUE)
        # ---
        self.velocity = Vector2(0, 0)
        self.direction = 0
        self.position = Vector2(self.rect.topleft)
        self.out_of_bounds = Vector2(0, 0)
        self.attacking = 0
        self.attack_length = len(self.animation.animation_data["attack up"])
        self.cooldown_time = 0

    def handle_attack_input(self, control: Control):
        if self.attacking > 0:
            self.attacking -= 1
        if control.action and self.attacking == 0 and not control.previous_frame_action:
            self.attacking = self.attack_length

    def handle_move_input(self, control: Control):
        self.velocity[:] = 0, 0
        if self.attacking > 0:
            return
        if control.moving_up:
            self.velocity.y = -cfg.VELOCITY
        if control.moving_down:
            self.velocity.y = cfg.VELOCITY
        if control.moving_left:
            self.velocity.x = -cfg.VELOCITY
        if control.moving_right:
            self.velocity.x = cfg.VELOCITY

        if self.velocity.elementwise() != 0:
            self.velocity = 0.7071 * self.velocity

    def update_direction(self):
        """
        Direction dict: down 0, left 1, up 2, right 3
        """
        if self.velocity.x != 0 and self.velocity.y == 0:
            self.direction = 1 * (self.velocity.x < 0) + 3 * (self.velocity.x > 0)
        elif self.velocity.y != 0 and self.velocity.x == 0:
            self.direction = 2 * (self.velocity.y < 0) + 0 * (self.velocity.y > 0)

    def move(self, delta):
        self.position += delta * self.velocity
        self.rect.topleft = self.position

    def handle_collision_with_objects(self, delta, physical_objects):
        self.hitbox.set_position(self.position + delta * self.velocity)
        if self.hitbox.has_collided(physical_objects):
            self.velocity[:] = 0, 0

    def check_collision_with_enemy(self, enemy_group: pygame.sprite.Group):
        # Temporary Shit
        self.sword_hitbox.set_position(self.position, self.direction)
        self.sword_hitbox.set_image(cfg.BLUE)
        # --
        for enemy in enemy_group.sprites():
            if self.cooldown_time == 0:
                if self.hitbox.rectangle.colliderect(enemy.rect):
                    self.cooldown_time = cfg.COOLDOW_TIME_PLAYER
                    self.life -= 1
            if self.attacking > 0: #== self.attack_length:
                if self.sword_hitbox.rectangle.colliderect(enemy.rect):
                    enemy.get_hit(self.direction)
        if self.cooldown_time >= 28:
            self.velocity.x = cfg.VELOCITY * 2 * ((self.direction == 1) - (self.direction == 3))
            self.velocity.y = cfg.VELOCITY * 2 * ((self.direction == 2) - (self.direction == 0))
            self.cooldown_time -= 1
        elif self.cooldown_time > 0:
            self.cooldown_time -= 1

    def check_if_within_bounds(self):
        self.out_of_bounds = Vector2(0, 0)
        if (
            self.position.x > cfg.DIS_WIDTH - cfg.SPRITE_SIZE // 2
            or self.position.x < -cfg.SPRITE_SIZE // 2
        ):
            self.out_of_bounds.x = copysign(1, self.position.x)
            self.velocity = (
                -self.out_of_bounds.elementwise() * cfg.SCROLL_VELOCITY * 0.97
            )
        if (
            self.position.y > cfg.DIS_HEIGHT - cfg.SPRITE_SIZE // 2
            or self.position.y < cfg.UI_HEIGHT - cfg.SPRITE_SIZE // 2
        ):
            self.out_of_bounds.y = copysign(1, self.position.y - cfg.UI_HEIGHT)
            self.velocity = (
                -self.out_of_bounds.elementwise() * cfg.SCROLL_VELOCITY * 0.97
            )

    def update_animation(self):
        if not self.velocity.elementwise() == 0:
            if self.direction == 2:
                frame_name = "walk up"
            elif self.direction == 0:
                frame_name = "walk down"
            elif self.direction == 1:
                frame_name = "walk left"
            elif self.direction == 3:
                frame_name = "walk right"

            self.animation.next_frame(frame_name)

        if self.attacking > 0:
            if self.direction == 2:
                frame_name = "attack up"
            elif self.direction == 0:
                frame_name = "attack down"
            elif self.direction == 1:
                frame_name = "attack left"
            elif self.direction == 3:
                frame_name = "attack right"

            self.animation.next_frame(frame_name)

        self.image = self.animation.current_sprite.copy()

    def update(
        self, delta, control: Control, in_transition, objects_group, enemy_group
    ):
        if not in_transition:
            self.handle_attack_input(control)
            self.handle_move_input(control)
            self.update_direction()
            self.check_collision_with_enemy(enemy_group)
            self.handle_collision_with_objects(delta, objects_group)
            self.update_animation()
            self.check_if_within_bounds()
        self.move(delta)
