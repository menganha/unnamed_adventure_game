from math import copysign

import pygame
from pygame.math import Vector2

import adventure_game.config as cfg
from adventure_game.animation import PlayerAnimation
from adventure_game.control import Control
from adventure_game.hitbox import Hitbox, SwordHitbox
from adventure_game.direction import Direction

from adventure_game.enemy import EnemyGroup, Enemy
from adventure_game.proyectile import Proyectile
from adventure_game.action import Action


class Player(pygame.sprite.Sprite):
    HITBOX_DEFLATION = 16
    SHOOT_COOLDOWN = 10

    def __init__(self):
        super().__init__()
        self.animation = PlayerAnimation()
        self.life = 10
        self.image = self.animation.current_sprite
        self.rect = self.image.get_rect()
        self.velocity = Vector2(0, 0)
        self.direction = Direction.DOWN
        self.position = Vector2((cfg.DIS_WIDTH // 2, cfg.DIS_HEIGHT // 2))
        self.rect.topleft = self.position
        self.out_of_bounds = Vector2(0, 0)
        self.cooldown_time = 0
        self.under_control = True
        self.shoot_action = Action(self.SHOOT_COOLDOWN)
        self.attack_action = Action(len(self.animation.animation_data["attack up"]))
        self.hitbox = None  # TODO: Change to an uninitialized hit box
        self.sword_hitbox = None
        self.set_up_hitboxes()

    def set_up_hitboxes(self):
        self.hitbox = Hitbox()
        self.hitbox.rect = self.rect.inflate((-self.HITBOX_DEFLATION, -self.HITBOX_DEFLATION))
        self.hitbox.get_offset2(self.rect)
        self.hitbox.position = self.position
        # self.hitbox.get_offset(self.rect.size)
        self.sword_hitbox = SwordHitbox(20, 40, 10, self.rect.size)
        self.sword_hitbox.get_offset(self.rect.size)
        # Temporary render the hitbox image as a red rectangle for debugging
        self.hitbox.set_image(cfg.RED)
        self.sword_hitbox.set_image(cfg.BLUE)
        # ---

    def handle_input(self, control, bullet_container):
        if self.under_control:
            self.velocity[:] = 0, 0
            self.handle_move_input(control)
            self.handle_action_input(control, bullet_container)
            self.update_direction()
        else:
            pass

    def handle_action_input(self, control: Control, bullet_container):
        if control.attack and self.attack_action.is_idle() and not control.previous_frame_action:
            self.attack_action.start()
        elif control.shoot and self.shoot_action.is_idle() and not control.previous_frame_action:
            self.shoot_action.start()
            Proyectile(self.rect.center, self.direction, abs_velocity=100, container=bullet_container)

    def handle_move_input(self, control: Control):
        if self.attack_action.in_progress():
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

    def move(self, delta):
        self.position += delta * self.velocity
        self.rect.topleft = self.position

    def handle_collision_with_objects(self, delta, physical_objects):
        for idx, vec in enumerate((Vector2(1, 0), Vector2(0, 1))):
            self.hitbox.set_position(self.position + delta * (self.velocity.elementwise() * vec))
            if self.hitbox.has_collided(physical_objects):
                self.velocity[idx] = 0

    def check_collision_with_enemy(self, enemy_group: EnemyGroup, proyectile_container: pygame.sprite.Group):
        # Temporary Shit
        self.sword_hitbox.set_position(self.position, self.direction)
        self.sword_hitbox.set_image(cfg.BLUE)
        enemy: Enemy
        arrow: Proyectile
        # --
        for enemy in enemy_group:
            if self.cooldown_time == 0:
                if self.hitbox.rect.colliderect(enemy.rect):
                    self.get_hit(enemy.position)
                    enemy.stay_idle()
            if self.attack_action.in_progress():
                if self.sword_hitbox.rect.colliderect(enemy.rect):
                    enemy.get_hit(self.direction)
            for arrow in proyectile_container:
                if arrow.hitbox.rect.colliderect(enemy.rect):
                    enemy.get_hit(self.direction)
                    arrow.kill()
        if self.cooldown_time >= 26:
            self.cooldown_time -= 1
        elif self.cooldown_time > 0:
            self.cooldown_time -= 1
            self.under_control = True

    def get_hit(self, enemy_position):
        self.cooldown_time = cfg.COOLDOW_TIME_PLAYER
        self.life -= 1
        self.under_control = False
        vec_difference = self.position - enemy_position
        direction = Direction.closest_direction(vec_difference)
        self.velocity = cfg.VELOCITY * 2 * direction.value

    def check_if_within_bounds(self):
        self.out_of_bounds = Vector2(0, 0)
        if self.position.x > cfg.DIS_WIDTH - cfg.SPRITE_SIZE // 2 or self.position.x < -cfg.SPRITE_SIZE // 2:
            self.out_of_bounds.x = copysign(1, self.position.x)
            self.velocity = self.out_of_bounds.elementwise() * -cfg.SCROLL_VELOCITY * 0.97
        if (
                self.position.y > cfg.DIS_HEIGHT - cfg.SPRITE_SIZE // 2
                or self.position.y < cfg.UI_HEIGHT - cfg.SPRITE_SIZE // 2
        ):
            self.out_of_bounds.y = copysign(1, self.position.y - cfg.UI_HEIGHT)
            self.velocity = self.out_of_bounds.elementwise() * -cfg.SCROLL_VELOCITY * 0.97

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

        if self.attack_action.in_progress():
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

    def update(self, delta, control: Control, in_transition: bool, objects_group, enemy_group, bullet_container):
        if not in_transition:
            self.shoot_action.update()
            self.attack_action.update()
            self.handle_input(control, bullet_container)
            self.check_collision_with_enemy(enemy_group, bullet_container)
            self.handle_collision_with_objects(delta, objects_group)
            self.update_animation()
            self.check_if_within_bounds()
        self.move(delta)
