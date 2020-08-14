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


class PlayerHitBox(pygame.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        self.rect = rect.inflate(-16, -16)
        self.image = pygame.Surface((self.rect.width, self.rect.height), flags=1)
        self.image.fill(cfg.RED)

    def update(self, vel_x, vel_y):
        self.rect.move_ip(vel_x, vel_y)


class Player(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.animation = PlayerAnimation()
        self.sprite = PlayerSprite(self.animation.current_sprite)
        self.hitbox = PlayerHitBox(self.sprite.rect)
        self.hitbox.add(self)
        self.sprite.add(self)
        self.velX = 0
        self.velY = 0
        self.out_of_bounds = [False, False]
        self.cooldown_time = 0

    def handle_attack_input(self, delta, control: Control):
        if (control.action
                and self.cooldown_time == 0
                and not control.previous_frame_action):
            self.cooldown_time = len(self.animation.animation_data['attack up'])
        if self.cooldown_time > 0:
            self.cooldown_time -= 1

    def handle_move_input(self, delta, control: Control):
        self.velX = 0
        self.velY = 0

        if self.cooldown_time > 0:
            return
        if control.moving_up:
            self.velY = -cfg.VELOCITY
        if control.moving_down:
            self.velY = cfg.VELOCITY
        if control.moving_left:
            self.velX = -cfg.VELOCITY
        if control.moving_right:
            self.velX = cfg.VELOCITY
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
        distance_x = int(delta * self.velX * cfg.FRAMERATE)
        distance_y = int(delta * self.velY * cfg.FRAMERATE)
        self.sprite.rect.move_ip(distance_x, distance_y)

    def handle_collision_with_objects(self, physical_objects):
        if self.hitbox.rect.move(self.velX, self.velY).collidelist(physical_objects) != -1:
            self.velX = 0
            self.velY = 0
            # distance_x = int(delta * self.velX * cfg.FRAMERATE)
            # distance_y = int(delta * self.velY * cfg.FRAMERATE)
            # self.sprite.rect.move_ip(distance_x, distance_y)

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
        self.velX = -self.out_of_bounds[0]*scroll_velocity
        self.velY = -self.out_of_bounds[1]*scroll_velocity

        if not in_transition:
            self.out_of_bounds = [0, 0]

    def update_animation(self):
        if self.velY < 0:
            self.animation.next_frame('walk up')
        if self.velY > 0:
            self.animation.next_frame('walk down')
        if self.velX < 0:
            self.animation.next_frame('walk left')
        if self.velX > 0:
            self.animation.next_frame('walk right')
        if self.cooldown_time > 0:
            if 'up' in self.animation.current_key:
                self.animation.next_frame('attack up')
            if 'down' in self.animation.current_key:
                self.animation.next_frame('attack down')
            if 'left' in self.animation.current_key:
                self.animation.next_frame('attack left')
            if 'right' in self.animation.current_key:
                self.animation.next_frame('attack right')

        self.sprite.image = self.animation.current_sprite

    def update(self, delta, control: Control, in_transition, objects_group, enemy_group):
        if any(self.out_of_bounds):
            self.transition(delta, in_transition)
        else:
            self.handle_attack_input(delta, control)
            self.handle_move_input(delta, control)
            self.handle_collision_with_objects(objects_group)
            self.check_collision_with_enemy(enemy_group)
            self.update_animation()
            self.check_if_within_bounds()
        self.move(delta)
        super().update(self.velX, self.velY)


