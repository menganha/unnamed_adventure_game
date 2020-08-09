import pygame
from math import copysign
import adventure_game.config as cfg
from adventure_game.control import Control
from adventure_game.animation import PlayerAnimation


class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (cfg.DIS_WIDTH//2, cfg.DIS_HEIGHT//2)


class Player(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.animation = PlayerAnimation()
        self.sprite = PlayerSprite(self.animation.current_sprite)
        self.sprite.add(self)
        self.velX = 0
        self.velY = 0
        self.animation_counter = 0
        self.out_of_bounds = [False, False]

    def handle_action(self, delta, control: Control):
        if control.action:
            pass

    def move(self, delta, control: Control, physical_objects):
        self.velX = 0
        self.velY = 0
        # self.animation_key = 'idleRight'
        if control.moving_up:
            self.velY = -cfg.VELOCITY
            self.animation.next_frame('walk up')
        if control.moving_down:
            self.velY = cfg.VELOCITY
            self.animation.next_frame('walk down')
        if control.moving_left:
            self.velX = -cfg.VELOCITY
            self.animation.next_frame('walk left')
        if control.moving_right:
            self.velX = cfg.VELOCITY
            self.animation.next_frame('walk right')

        if self.velX != 0 and self.velY != 0:
            # if self.velX < 0:
            #     self.animation_key = 'left'
            # else:
            #     self.animation_key = 'right'
            self.velX = copysign(0.7071 * self.velX, self.velX)
            self.velY = copysign(0.7071 * self.velY, self.velY)

        self.sprite.image = self.animation.current_sprite

        old_pos_x = self.sprite.rect.x
        old_pos_y = self.sprite.rect.y
        self.sprite.rect.x += int(delta * self.velX * cfg.FRAMERATE)
        self.sprite.rect.y += int(delta * self.velY * cfg.FRAMERATE)
        hitbox = self.sprite.rect  # .inflate(-16, -16)
        # hitbox.y += 8

        if hitbox.collidelist(physical_objects) != -1:
            self.sprite.rect.x = old_pos_x
            self.sprite.rect.y = old_pos_y

        self.check_if_within_bounds()

    def check_collision_with_enemy(self, enemy_group):
        enemies_collided = pygame.sprite.spritecollide(self.sprite, enemy_group, dokill=False)
        if enemies_collided is None:
            pass
        else:
            pass

    def check_if_within_bounds(self):
        if (self.sprite.rect.x > cfg.DIS_WIDTH - cfg.SPRITE_SIZE//2
                or self.sprite.rect.x < -cfg.SPRITE_SIZE//2):
            self.out_of_bounds[0] = copysign(1, self.sprite.rect.x)
        if (self.sprite.rect.y > cfg.DIS_HEIGHT - cfg.SPRITE_SIZE//2
                or self.sprite.rect.y < -cfg.SPRITE_SIZE//2):
            self.out_of_bounds[1] = copysign(1, self.sprite.rect.y)

    def transition(self, delta, in_transition):
        # Reduce the velocity on frames where the position is an even number
        scroll_velocity = cfg.SCROLL_VELOCITY
        if (self.out_of_bounds[0] or self.out_of_bounds[1]) and not in_transition:
            scroll_velocity = cfg.SCROLL_VELOCITY - 10
        self.sprite.rect.x += -self.out_of_bounds[0]*scroll_velocity
        self.sprite.rect.y += -self.out_of_bounds[1]*scroll_velocity

        if not in_transition:
            self.out_of_bounds = [0, 0]

    def update(self, delta, control: Control, in_transition, physical_objects, enemy_group):
        if any(self.out_of_bounds):
            self.transition(delta, in_transition)
        else:
            self.move(delta, control, physical_objects)
            self.check_collision_with_enemy(enemy_group)
            self.handle_action(delta, control)
