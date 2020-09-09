import json
from random import randint

import pygame
from pygame.math import Vector2

import adventure_game.config as cfg
from adventure_game.animation import EnemyAnimation
from adventure_game.hitbox import Hitbox


class Enemy(pygame.sprite.Sprite):
    _think_time = 70

    def __init__(self, position):
        super().__init__()
        self.animation = EnemyAnimation.create_jelly_animation()
        self.image = self.animation.current_sprite
        self.rect = self.image.get_rect()
        self.hitbox = Hitbox(self.rect.size)
        self.position = Vector2(position)
        self.velocity = Vector2((0, 0))
        self.health = 4
        self.direction = 0
        self.rect.topleft = self.position
        self.blink_time = 0
        self.think_counter = self._think_time

    def get_hit(self, direction):
        if self.blink_time == 0:
            self.velocity.x = cfg.VELOCITY * 4 * (-(direction == 1) + (direction == 3))
            self.velocity.y = cfg.VELOCITY * 4 * (-(direction == 2) + (direction == 0))
            self.blink_time = cfg.BLINK_TIME
            self.health -= 1

    def handle_ai(self):
        if self.think_counter == 0:
            self.think_counter = self._think_time
        if self.think_counter == self._think_time:
            self.direction = randint(0, 3)

        self.velocity.x = cfg.VELOCITY*0.8 * (-(self.direction == 1) + (self.direction == 3))
        self.velocity.y = cfg.VELOCITY*0.8 * (-(self.direction == 2) + (self.direction == 0))
        self.think_counter -= 1

    def handle_collisions_with_objects(self, delta, physical_objects):
        position = self.position + delta*self.velocity
        self.hitbox.set_position(position)
        if self.hitbox.rectangle.collidelist(physical_objects) != -1:
            self.velocity[:] = 0, 0

    def move(self, delta):
        self.position += delta*self.velocity
        self.rect.topleft = self.position

    def update(self, delta, physical_objects):
        if self.health == 0:
            self.kill()
        if self.blink_time == 0:
            self.animation.next_frame("walk")
            self.image = self.animation.current_sprite
            self.handle_ai()
        elif self.blink_time > 0:
            # TODO: Beautify this condition
            if self.blink_time == 18:
                self.velocity[:] = 0, 0
            if self.blink_time % 6 < 3:
                alpha = 0
            else:
                alpha = 255
            color = (255, 255, 255, alpha)
            self.image = self.animation.current_sprite.copy()
            self.image.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
            self.blink_time -= 1

        self.handle_collisions_with_objects(delta, physical_objects)
        self.move(delta)


class EnemyGroup(pygame.sprite.Group):
    def __init__(self, current_map):
        super().__init__()
        self.current_map = current_map
        self.enemy_positions = []
        self.get_enemy_positions()
        self.create_enemies()

    def get_enemy_positions(self):
        with open(self.current_map) as file:
            self.data = json.load(file)['layers']
        self.enemy_positions = []
        for layer in self.data:
            if layer['type'] == 'objectgroup' and 'enemies' in layer['name']:
                for obj_dict in layer['objects']:
                    self.enemy_positions.append([obj_dict['x'], obj_dict['y']])

    def create_enemies(self):
        for pos in self.enemy_positions:
            self.add(Enemy(pos))

    def update(self, delta, new_map, in_transition, physical_objects):
        if new_map != self.current_map:
            self.empty()
            if not in_transition:
                self.current_map = new_map
                self.get_enemy_positions()
                self.create_enemies()
        else:
            super().update(delta, physical_objects)

        # Define how they move
        # Define how they react when player is nearby
        # Check if dead. If so, remove it from the group
