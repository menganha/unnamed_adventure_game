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
        self.velX = 0  # Current velocity
        self.velY = 0
        self.dir = 0  # Current direction
        self.out_of_bounds = [False, False]
        self.attacking = 0
        self.attack_length = len(self.animation.animation_data['attack up'])

    def handle_attack_input(self, delta, control: Control):
        if self.attacking > 0:
            self.attacking -= 1
        if (control.action
                and self.attacking == 0
                and not control.previous_frame_action):
            self.attacking = self.attack_length

    def handle_move_input(self, delta, control: Control):
        # Direction dict: down 0, left 1, up 2, right 3
        self.velX = 0
        self.velY = 0
        if self.attacking > 0:
            return
        if control.moving_up:
            self.velY = -cfg.VELOCITY
            self.dir = 2
        if control.moving_down:
            self.velY = cfg.VELOCITY
            self.dir = 0
        if control.moving_left:
            self.velX = -cfg.VELOCITY
            self.dir = 1
        if control.moving_right:
            self.velX = cfg.VELOCITY
            self.dir = 3
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

    def check_collision_with_enemy(self, enemy_group: pygame.sprite.Group):
        # TODO: only registers hits for one frame
        if self.attacking == self.attack_length:
            offset_x = 0
            offset_y = 0
            if self.dir == 2:
                dim = (self.hitbox.rect.width, cfg.SWORD_HITBOX)
                offset_y = - cfg.SWORD_HITBOX
            if self.dir == 0:
                dim = (self.hitbox.rect.width, cfg.SWORD_HITBOX)
                offset_y = self.hitbox.rect.height + cfg.SWORD_HITBOX
            if self.dir == 1:
                dim = (cfg.SWORD_HITBOX, self.hitbox.rect.height)
                offset_x = - cfg.SWORD_HITBOX
            if self.dir == 3:
                dim = (cfg.SWORD_HITBOX, self.hitbox.rect.height)
                offset_x = self.hitbox.rect.width + cfg.SWORD_HITBOX

            sword_hitbox = pygame.Rect(
                (self.hitbox.rect.x + offset_x, self.hitbox.rect.y + offset_y),
                dim)
            # enemies_hit = pygame.sprite.spritecollide(sword_hitbox, enemy_group, dokill=False)
            # for enemy in enemies_hit:
            #     enemy.get_hit()

            for enemy in enemy_group.sprites():
                if sword_hitbox.colliderect(enemy.rect):
                    enemy.get_hit()

        # enemies_collided = pygame.sprite.spritecollide(self.hitbox, enemy_group, dokill=False)
        # if enemies_collided:
        #     enemy_group.remove(enemies_collided)

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
        elif self.velY > 0:
            self.animation.next_frame('walk down')
        elif self.velX < 0:
            self.animation.next_frame('walk left')
        elif self.velX > 0:
            self.animation.next_frame('walk right')
        if self.attacking > 0:
            #TODO: animation.current_key is probably not going to be used
            # if 'up' in self.animation.current_key:
            if self.dir == 2:
                self.animation.next_frame('attack up')
            # if 'down' in self.animation.current_key:
            elif self.dir == 0:
                self.animation.next_frame('attack down')
            # if 'left' in self.animation.current_key:
            elif self.dir == 1:
                self.animation.next_frame('attack left')
            # if 'right' in self.animation.current_key:
            elif self.dir == 3:
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


