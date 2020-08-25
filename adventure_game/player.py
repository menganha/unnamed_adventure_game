from math import copysign

import pygame
from pygame.math import Vector2

import adventure_game.config as cfg
from adventure_game.animation import PlayerAnimation
from adventure_game.control import Control


class Player(pygame.sprite.Sprite):
    hitbox_deflation = 16

    def __init__(self):
        super().__init__()
        self.animation = PlayerAnimation()
        self.image = self.animation.current_sprite
        self.rect = self.image.get_rect()
        self.rect.center = (cfg.DIS_WIDTH // 2, cfg.DIS_HEIGHT // 2)
        self.hitbox = self.rect.inflate(-self.hitbox_deflation, -self.hitbox_deflation)
        self.hitbox_image = pygame.Surface((self.hitbox.width, self.hitbox.height))
        self.hitbox_image.fill(cfg.RED)
        self.hitbox_image.set_alpha(100)
        self.velocity = Vector2(0, 0)
        self.direction = 0
        self.position = Vector2(self.rect.topleft)
        self.out_of_bounds = Vector2(0, 0)
        self.attacking = 0
        self.attack_length = len(self.animation.animation_data["attack up"])

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

    def update_direction(self, control):
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
        position = (
            self.position + delta * self.velocity + Vector2(self.hitbox_deflation // 2)
        )
        self.hitbox.topleft = position
        if self.hitbox.collidelist(physical_objects) != -1:
            self.velocity[:] = 0

    def check_collision_with_enemy(self, enemy_group: pygame.sprite.Group):
        # TODO: only registers hits for one frame. Fix this by setting a
        # condition on cool time when one has hitted an enemy. This is almost
        # done. and then change to self.attacking <= self.atack_length
        pass
        # if self.attacking == self.attack_length:
        #     offset_x = 0
        #     offset_y = 0
        #     if self.dir == 2:
        #         dim = (self.hitbox.rect.width, cfg.SWORD_HITBOX)
        #         offset_y = - cfg.SWORD_HITBOX
        #     if self.dir == 0:
        #         dim = (self.hitbox.rect.width, cfg.SWORD_HITBOX)
        #         offset_y = self.hitbox.rect.height + cfg.SWORD_HITBOX
        #     if self.dir == 1:
        #         dim = (cfg.SWORD_HITBOX, self.hitbox.rect.height)
        #         offset_x = - cfg.SWORD_HITBOX
        #     if self.dir == 3:
        #         dim = (cfg.SWORD_HITBOX, self.hitbox.rect.height)
        #         offset_x = self.hitbox.rect.width + cfg.SWORD_HITBOX

        #     sword_hitbox = pygame.Rect(
        #         (self.hitbox.rect.x + offset_x, self.hitbox.rect.y + offset_y),
        #         dim)
        #     # enemies_hit = pygame.sprite.spritecollide(sword_hitbox, enemy_group, dokill=False)
        #     # for enemy in enemies_hit:
        #     #     enemy.get_hit()

        #     for enemy in enemy_group.sprites():
        #         if sword_hitbox.colliderect(enemy.rect):
        #             enemy.get_hit()

        # enemies_collided = pygame.sprite.spritecollide(self.hitbox, enemy_group, dokill=False)
        # if enemies_collided:
        #     enemy_group.remove(enemies_collided)

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
            or self.position.y < -cfg.SPRITE_SIZE // 2
        ):
            self.out_of_bounds.y = copysign(1, self.position.y)
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

        # Temporary: Blit hitbox to sprite
        self.image = self.animation.current_sprite.copy()
        self.image.blit(self.hitbox_image, (8, 8))

    def update(
        self, delta, control: Control, in_transition, objects_group, enemy_group
    ):
        if not in_transition:
            self.handle_attack_input(control)
            self.handle_move_input(control)
            self.update_direction(control)
            self.handle_collision_with_objects(delta, objects_group)
            self.check_collision_with_enemy(enemy_group)
            self.update_animation()
            self.check_if_within_bounds()
        self.move(delta)
