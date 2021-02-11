# TODO: Create an independent AI class
from __future__ import annotations


import pygame
from pygame.math import Vector2

import adventure_game.config as cfg
from adventure_game.direction import Direction
from adventure_game.hitbox import Hitbox
from adventure_game.action import Action
from adventure_game.entity_sprite import EnititySprite



class Enemy:
    THINK_TIME = 70
    INVISIBLE_TIME = 25
    MAX_VISUAL_FIELD = 6000
    MAX_VELOCITY = cfg.VELOCITY * 0.5
    MAX_FRAME_WAIT = 10
    IDLE_TIME = 25

    def __init__(self, position: Vector2, direction: Direction, life: int, sprite: EnititySprite):
        self.group = None
        self.life = life
        self.position = Vector2(position)
        self.velocity = Vector2(0, 0)
        self.direction = direction
        self.sprite = sprite
        self.state = sprite.state
        self.hitbox = Hitbox(sprite.rect)
        self.cooldown = Action(self.INVISIBLE_TIME)
        # self.think_counter = self.THINK_TIME
        self.force_frame_count = self.MAX_FRAME_WAIT # TODO: Move to AI
        self.idle_counter = 0 # TODO: Move to Action
        self.hit_sound = pygame.mixer.Sound("assets/sounds/hit.wav")

    def update(self, delta, physical_objects, player_position: Vector2):
        self.cooldown.update()
        if self.cooldown.is_idle():
        #     self.animation.next_frame("walk")
        #     self.image = self.animation.current_sprite
            self.handle_ai(player_position)
        # elif self.cooldown.in_progress():
        #     self.blink()
        #     self.cooldown.update()
        # if self.idle_counter > 0:
        #     self.idle_counter -= 1
        #     self.velocity[:] = 0, 0
        self.handle_collisions_with_objects(delta, physical_objects)
        self.move(delta)

    def get_hit(self, direction: Direction):
        if self.cooldown.is_idle():
            self.cooldown.restart()
            self.hit_sound.play()
            self.velocity = cfg.VELOCITY * 2 * direction.value
            self.life -= 1
            if self.life == 0:
                self.kill()

    def handle_ai(self, player_position: Vector2):
        distance_to_player = self.position.distance_squared_to(player_position)
        if distance_to_player < self.MAX_VISUAL_FIELD:
            vec_difference = player_position - self.position
            desired_direction = Direction.closest_direction(vec_difference)
            if desired_direction != self.direction:
                self.force_frame_count -= 1
                if self.force_frame_count == 0:
                    self.force_frame_count = self.MAX_FRAME_WAIT
                    self.direction = desired_direction

            self.velocity = self.MAX_VELOCITY * self.direction.value
        else:
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
        self.idle_counter = self.IDLE_TIME

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
