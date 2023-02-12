"""
Define all Event types here
"""

from yazelc.components import Position, Health, Weapon
from yazelc.controller import Controller
from yazelc.items import CollectableItemType


class InputEvent:
    def __init__(self, controller: Controller):
        self.controller = controller


class DeathEvent:
    pass


class PauseEvent:
    pass


class DamageEvent:
    def __init__(self, victim_id: int, victim_health: Health, attacker_id: int, attacker_weapon: Weapon):
        self.victim_id = victim_id
        self.victim_health = victim_health
        self.attacker_id = attacker_id
        self.attacker_weapon = attacker_weapon


class ResumeEvent:
    pass


class RestartEvent:
    pass


class CollisionEvent:

    def __init__(self, ent_1: int, ent_2: int):
        self.ent_1 = ent_1
        self.ent_2 = ent_2


class HudUpdateEvent:

    def __init__(self, collectable_item_type: CollectableItemType, value: int):
        self.pickable_item_type = collectable_item_type
        self.value = value


class BombExplosionEvent:
    def __init__(self, bomb_entity_id: int, position: Position):
        self.bomb_entity_id = bomb_entity_id
        self.position = position
