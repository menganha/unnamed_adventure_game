"""
Define all Event types here
"""

from dataclasses import dataclass
from functools import partial

from pygame import Color

from yazelc.components import Collectable
from yazelc.controller import Controller
from yazelc.items import CollectableItemType

eventclass = partial(dataclass, frozen=True)


@eventclass
class InputEvent:
    controller: Controller


@eventclass
class BlockInputEvent:
    block_frames: int


class DeathEvent:
    pass


@eventclass
class DeleteEntityEvent:
    entity_id: int


@eventclass
class CollectionEvent:
    """ When player or interactor collider touches a collectable """
    collectable_id: int
    collectable: Collectable
    collector_id: int


class EnemyDecisionEvent:
    pass


class PauseEvent:
    pass


@eventclass
class DamageEvent:
    victim_id: int
    attacker_id: int


class ResumeEvent:
    pass


class RestartEvent:
    pass


@eventclass
class CollisionEvent:
    ent_1: int
    ent_2: int


@eventclass
class HudUpdateEvent:
    pickable_item_type: CollectableItemType
    value: int


@eventclass
class ExplosionEvent:
    """ Visual effect system event """
    position: tuple[int, int]
    n_particles: int
    max_vel: int
    color: Color


@eventclass
class BombExplosionEvent:
    bomb_entity_id: int
