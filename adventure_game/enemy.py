import json
from random import choice, randint

import pygame
from pygame.math import Vector2

import adventure_game.config as cfg
from adventure_game.animation import EnemyAnimation
from adventure_game.hitbox import Hitbox
from adventure_game.player import Player


class Enemy(pygame.sprite.Sprite):
    THINK_TIME = 70
    MAX_BLINK_TIME = 35
    MAX_VISUAL_FIELD = 6000
    MAX_VELOCITY = cfg.VELOCITY * 0.5
    MAX_FRAME_WAIT = 10
    IDLE_TIME = 25
    DIRECTION_VECTOR = (
        Vector2(0, 1),
        Vector2(-1, 0),
        Vector2(0, -1),
        Vector2(1, 0),
        Vector2(1, 1),
        Vector2(-1, 1),
        Vector2(-1, -1),
        Vector2(1, 1),
    )

    def __init__(self, position, animation, health):
        super().__init__()
        self.animation = animation
        self.image = self.animation.current_sprite
        self.rect = self.image.get_rect()
        self.hitbox = Hitbox(self.rect.size)
        self.position = Vector2(position)
        self.velocity = Vector2(0, 0)
        self.health = health
        self.direction = self.DIRECTION_VECTOR[randint(0, 3)]
        self.rect.topleft = self.position
        self.blink_time = 0
        self.think_counter = self.THINK_TIME
        self.force_frame_count = self.MAX_FRAME_WAIT
        self.idle_counter = 0
        self.hit_sound = pygame.mixer.Sound("assets/sounds/hit.wav")

    def get_hit(self, direction_idx):
        if self.blink_time == 0:
            self.hit_sound.play()
            self.velocity = cfg.VELOCITY * 4 * self.DIRECTION_VECTOR[direction_idx]
            self.blink_time = cfg.BLINK_TIME
            self.health -= 1

    def handle_ai(self, player: Player):
        distance_to_player = self.position.distance_squared_to(player.position)
        if distance_to_player < self.MAX_VISUAL_FIELD:
            vec_difference = player.position - self.position
            desired_direction = max(self.DIRECTION_VECTOR, key=lambda x: x.dot(vec_difference))
            if desired_direction != self.direction:
                self.force_frame_count -= 1
                if self.force_frame_count == 0:
                    self.force_frame_count = self.MAX_FRAME_WAIT
                    self.direction = desired_direction

            self.velocity = self.MAX_VELOCITY * self.direction
        else:
            self.velocity[:] = 0, 0
        # elif self.think_counter == 0:
        #     self.think_counter = choice((self.THINK_TIME, 5))

        # if self.think_counter == self.THINK_TIME:
        #     self.direction = self.DIRECTION_VECTOR[randint(0, 3)]

        # self.velocity = cfg.VELOCITY * 0.5 * self.direction
        # self.think_counter -= 1

    def handle_collisions_with_objects(self, delta, physical_objects):
        for idx, vec in enumerate((Vector2(1, 0), Vector2(0, 1))):
            self.hitbox.set_position(self.position + delta * (self.velocity.elementwise() * vec))
            if self.hitbox.has_collided(physical_objects):
                self.velocity[idx] = 0

    def stay_idle(self):
        self.idle_counter = self.IDLE_TIME

    def move(self, delta):
        self.position += delta * self.velocity
        self.rect.topleft = self.position

    def update(self, delta, physical_objects, player: Player):
        if self.health == 0:
            self.kill()
        if self.blink_time == 0:
            self.animation.next_frame("walk")
            self.image = self.animation.current_sprite
            self.handle_ai(player)
        elif self.blink_time > 0:
            if self.blink_time == self.MAX_BLINK_TIME // 2:
                self.velocity[:] = 0, 0
            self.blink()
            self.blink_time -= 1
        if self.idle_counter > 0:
            self.idle_counter -= 1
            self.velocity[:] = 0, 0

        self.handle_collisions_with_objects(delta, physical_objects)
        self.move(delta)

    def blink(self):
        if self.blink_time % 6 < 3:
            alpha = 0
        else:
            alpha = 255
        color = (255, 255, 255, alpha)
        self.image = self.animation.current_sprite.copy()
        self.image.fill(color, special_flags=pygame.BLEND_RGBA_MULT)

    @classmethod
    def create_enemy_jelly(cls, position):
        return cls(position, EnemyAnimation.create_jelly_animation(), health=4)

    @classmethod
    def create_enemy_dragon(cls, position):
        return cls(position, EnemyAnimation.create_dragon_animation(), health=10)

    # TODO: Think about inheritance instead of these ugly fabric methods


class EnemyGroup(pygame.sprite.Group):
    def __init__(self, current_map):
        super().__init__()
        self.current_map = current_map
        self.enemy_list = []
        self.get_enemy_positions()
        self.create_enemies()

    def get_enemy_positions(self):
        with open(self.current_map) as file:
            data = json.load(file)["layers"]
        self.enemy_list = []
        for layer in data:
            if layer["type"] == "objectgroup" and "enemies" in layer["name"]:
                for obj_dict in layer["objects"]:
                    if 'properties' in obj_dict:
                        kind = obj_dict['properties'][0]['value']
                    else:
                        kind = 'jelly'
                    self.enemy_list.append({'pos': (obj_dict["x"], obj_dict["y"]), 'kind': kind})

    def create_enemies(self):
        for enemy in self.enemy_list:
            if enemy['kind'] == 'dragon':
                self.add(Enemy.create_enemy_dragon(enemy['pos']))
            else:
                self.add(Enemy.create_enemy_jelly(enemy['pos']))

    def update(self, delta, new_map, in_transition, physical_objects, player: Player):
        if new_map != self.current_map:
            self.empty()
            if not in_transition:
                self.current_map = new_map
                self.get_enemy_positions()
                self.create_enemies()
        else:
            super().update(delta, physical_objects, player)
