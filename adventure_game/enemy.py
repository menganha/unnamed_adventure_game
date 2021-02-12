# TODO: Create an independent AI class
import pygame
from pygame.math import Vector2

import adventure_game.config as cfg
from adventure_game.direction import Direction
from adventure_game.hitbox import Hitbox
from adventure_game.state import State
from adventure_game.action import Action
from adventure_game.entity_sprite import EnititySprite


class Enemy:
    THINK_TIME = 70
    INVISIBLE_TIME = 12
    MAX_VISUAL_FIELD = 6000
    FRAMES_TO_WAIT = 10
    IDLE_FRAMES = 25
    DAMAGE_VELOCITY = 6 * cfg.FRAMERATE

    def __init__(self, position: Vector2, direction: Direction, abs_velocity: int, life: int, sprite: EnititySprite):
        self.group = None
        self.life = life
        self.position = Vector2(position)
        self.velocity = Vector2(0, 0)
        self.abs_velocity = abs_velocity
        self.direction = direction
        self.sprite = sprite
        self.state = sprite.state
        self.hitbox = Hitbox(sprite.rect)
        self.cooldown = Action(self.INVISIBLE_TIME)
        # self.think_counter = self.THINK_TIME
        self.force_frame = Action(self.FRAMES_TO_WAIT)  # TODO: Move to AI. Frames to delay the change of direction
        self.idle = Action(self.IDLE_FRAMES)  # TODO: Move to Action
        self.hit_sound = pygame.mixer.Sound("assets/sounds/hit.wav")

    def update(self, delta, physical_objects, player_position: Vector2):
        self.cooldown.update()
        self.idle.update()
        if self.idle.in_progress():
            self.velocity[:] = 0, 0
        elif self.cooldown.is_idle():
            self.handle_ai(player_position)
        self.handle_collisions_with_objects(delta, physical_objects)
        self.move(delta)

    def get_hit(self, direction: Direction):
        if self.cooldown.is_idle():
            self.cooldown.restart()
            self.hit_sound.play()
            self.velocity = self.DAMAGE_VELOCITY * direction.value
            self.life -= 1
            if self.life == 0:
                self.kill()

    def handle_ai(self, player_position: Vector2):
        distance_to_player = self.position.distance_squared_to(player_position)
        if distance_to_player < self.MAX_VISUAL_FIELD:
            vec_difference = player_position - self.position
            desired_direction = Direction.closest_direction(vec_difference)
            if desired_direction != self.direction:
                self.force_frame.update()
                if self.force_frame.is_idle():
                    self.force_frame.restart()
                    self.direction = desired_direction
            self.velocity = self.abs_velocity * self.direction.value
            self.state = State.WALK
        else:
            self.state = State.IDLE
            self.velocity[:] = 0, 0
        # elif self.think_counter == 0:
        #     self.think_counter = choice((self.THINK_TIME, 5))

        # if self.think_counter == self.THINK_TIME:
        #     self.direction.py = self.DIRECTION_VECTOR[randint(0, 3)]

        # self.velocity = cfg.VELOCITY * 0.5 * self.direction.py
        # self.think_counter -= 1

    def handle_collisions_with_objects(self, delta: float, physical_objects):
        for idx, vec in enumerate((Vector2(1, 0), Vector2(0, 1))):
            self.hitbox.move_with_respect_to_parent(self.position + delta * (self.velocity.elementwise() * vec))
            if self.hitbox.has_collided_with_rects(*physical_objects):
                self.velocity[idx] = 0

    def stay_idle(self):
        self.idle.restart()
        self.state = State.IDLE

    def move(self, delta):
        self.position.update(self.position + delta * self.velocity)
        self.sprite.update(self.direction, self.position, self.velocity, self.state)

    def kill(self):
        self.group.remove_enemy(self)

    def add(self, group):
        """Add to an enemy group"""
        self.group = group

    # def blink(self):
    #     self.image = self.animation.current_sprite.copy()
    #     if self.cooldown.counter % 7 > 4:
    #         self.image.fill(cfg.RED, special_flags=pygame.BLEND_RGBA_MULT)
    #     elif self.cooldown.counter % 7 > 2:
    #         self.image.fill(cfg.BLUE, special_flags=pygame.BLEND_RGBA_MULT)
    #     else:
    #         self.image.fill(cfg.GREEN, special_flags=pygame.BLEND_RGBA_MULT)
    #     alpha = 255
    # color = (255, 255, 255, alpha)
    # self.image.blit(self.image, self.image.get_rect(), special_flags=pygame.BLEND_RGBA_MULT)
