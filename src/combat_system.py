import pygame

import esper
from components import MeleeWeapon, Health, HitBox, Position, Renderable
from direction import Direction

"""
BIG TODO:  We have to think how to decoouple the direction values from the renderable. It doesn't 
smell good. Is it possible to take it away at all? we can derive it from the current velocity values isn't it?
"""


class CombatSystem(esper.Processor):

    def process(self):
        for ent, (weapon, pos, rend) in self.world.get_components(MeleeWeapon, Position, Renderable):
            # TODO: Should all entities with a weapon have a renderable? how to impose this?
            if weapon.frame_counter == 0:
                continue

            components = [(target_ent, tup) for (target_ent, tup) in self.world.get_components(HitBox, Health)
                          if target_ent != ent]
            weapon_hitbox = self.__get_weapon_hitbox(pos, rend, weapon)
            index = weapon_hitbox.collidelist([hb.rect for _, (hb, _) in components])
            if index != -1:
                entity_hit, (_, health) = components[index]
                if health.frame_counter == 0:
                    health.frame_counter = health.cooldown_frames
                    health.points -= weapon.power
                # health.frame_counter -= 1
                if health.points == 0:
                    self.world.delete_entity(entity_hit)
            weapon.frame_counter -= 1

        for ent, (health) in self.world.get_component(Health):
            if health.frame_counter > 0:
                health.frame_counter -= 1

    @staticmethod
    def __get_weapon_hitbox(position: Position, renderable: Renderable, weapon: MeleeWeapon) -> pygame.Rect:
        """
        Returns the weapon hitbox by moving it to its holding entity position and
        offsetting it depending on the sprite direction and weapon offset
        """
        if renderable.direction in (Direction.WEST, Direction.EAST):
            rect = weapon.rect_h
        else:
            rect = weapon.rect_v
        rect.centerx = position.x + int(renderable.width / 2)
        rect.centery = position.y + int(renderable.height / 2)
        rect.move_ip(weapon.offset * renderable.direction.value.x, weapon.offset*renderable.direction.value.y)
        return rect