import pygame
from pygame.math import Vector2
from math import copysign
import adventure_game.config as cfg
from adventure_game.control import Control
from adventure_game.animation import PlayerAnimation


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.animation = PlayerAnimation()
        self.image = self.animation.current_sprite
        self.rect = self.image.get_rect()
        self.rect.center = (cfg.DIS_WIDTH//2, cfg.DIS_HEIGHT//2)
        self.hitbox = self.rect.inflate(-16, -16)
        self.velX = 0  # Current velocity
        self.velY = 0
        self.direction = 0  # Current direction
        self.position = Vector2(self.rect.topleft)
        self.out_of_bounds = [False, False]
        self.attacking = 0
        self.attack_length = len(self.animation.animation_data['attack up'])

    def handle_attack_input(self, control: Control):
        if self.attacking > 0:
            self.attacking -= 1
        if (control.action
                and self.attacking == 0
                and not control.previous_frame_action):
            self.attacking = self.attack_length

    def handle_move_input(self, control: Control):
        # Direction dict: down 0, left 1, up 2, right 3
        self.velX = 0
        self.velY = 0
        if self.attacking > 0:
            return
        if control.moving_up:
            self.velY = -cfg.VELOCITY
            self.direction = 2
        if control.moving_down:
            self.velY = cfg.VELOCITY
            self.direction = 0
        if control.moving_left:
            self.velX = -cfg.VELOCITY
            self.direction = 1
        if control.moving_right:
            self.velX = cfg.VELOCITY
            self.direction = 3
        # if self.velX == 0 and self.velY == 0:
        #     self.animation.reset()

        if self.velX != 0 and self.velY != 0:
            # if self.velX < 0:
            #     self.animation_key = 'left'
            # else:
            #     self.animation_key = 'right'
            self.velX = copysign(0.7071 * self.velX, self.velX)
            self.velY = copysign(0.7071 * self.velY, self.velY)

    def move(self, delta):
        self.position.x += delta * self.velX
        self.position.y += delta * self.velY
        self.rect.topleft = self.position

    def handle_collision_with_objects(self, delta, physical_objects):
        position_x = self.position.x + delta * self.velX + 8
        position_y = self.position.y + delta * self.velY + 8
        self.hitbox.x = position_x
        self.hitbox.y = position_y
        if self.hitbox.collidelist(physical_objects) != -1:
            self.velX = 0
            self.velY = 0

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
        self.out_of_bounds = Vector2((0, 0))
        if (self.position.x > cfg.DIS_WIDTH - cfg.SPRITE_SIZE//2
                or self.position.x < -cfg.SPRITE_SIZE//2):
            self.out_of_bounds.x = copysign(1, self.position.x)
            self.velX = -self.out_of_bounds.x*cfg.SCROLL_VELOCITY*0.9
            self.velY = 0
        if (self.position.y > cfg.DIS_HEIGHT - cfg.SPRITE_SIZE//2
                or self.position.y < -cfg.SPRITE_SIZE//2):
            self.out_of_bounds.y = copysign(1, self.position.y)
            self.velX = 0
            self.velY = -self.out_of_bounds.y*cfg.SCROLL_VELOCITY*0.9

    def update_animation(self):
        if self.velY < 0:
            self.animation.next_frame('walk up')
        elif self.velY > 0:
            self.animation.next_frame('walk down')
        elif self.velX < 0:
            self.animation.next_frame('walk left')
        elif self.velX > 0:
            self.animation.next_frame('walk right')
        if self.velX != 0 and self.velY != 0:
            if self.velY < 0:
                self.animation_key = 'walk up'
            else:
                self.animation_key = 'walk down'

        if self.attacking > 0:
            #TODO: animation.current_key is probably not going to be used
            if self.direction == 2:
                self.animation.next_frame('attack up')
            elif self.direction == 0:
                self.animation.next_frame('attack down')
            elif self.direction == 1:
                self.animation.next_frame('attack left')
            elif self.direction == 3:
                self.animation.next_frame('attack right')

        self.image = self.animation.current_sprite

    def draw_hitbox_over_sprite(self):
        """
        Debug function to draw hitbox over sprite
        """
        self.red_surface = pygame.Surface((self.hitbox.w, self.hitbox.h))
        self.red_surface.fill(cfg.RED)

    def update(self, delta, control: Control, in_transition, objects_group, enemy_group):
        if not in_transition:
            self.handle_attack_input(control)
            self.handle_move_input(control)
            self.handle_collision_with_objects(delta, objects_group)
            self.check_collision_with_enemy(enemy_group)
            self.update_animation()
            self.check_if_within_bounds()
            self.draw_hitbox_over_sprite()
        self.move(delta)
