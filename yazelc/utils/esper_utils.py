"""
Utility functions complementing to the esper ECS library
"""
# TODO: Add this to the zesper module
from yazelc import zesper


def try_pair_signature(world: zesper.World, ent_1: int, ent_2: int, component_1, component_2):
    """
    Checks if the pair have each the corresponding input pair components in the two possible permutations.
    If found returns the entities paired with their respective components
    """
    component_1_1 = world.try_component(ent_1, component_1)
    component_2_2 = world.try_component(ent_2, component_2)

    component_1_2 = world.try_component(ent_1, component_2)
    component_2_1 = world.try_component(ent_2, component_1)

    if component_1_1 and component_2_2:
        return ent_1, component_1_1, ent_2, component_2_2
    elif component_1_2 and component_2_1:
        return ent_2, component_2_1, ent_1, component_1_2
    else:
        return None


def try_signature(world: zesper.World, ent_1: int, ent_2: int, component):
    """
    Same as above but only checked on a single entity
    """
    component_1 = world.try_component(ent_1, component)
    component_2 = world.try_component(ent_2, component)
    if component_1:
        return ent_1, component_1, ent_2
    elif component_2:
        return ent_2, component_2, ent_1
    else:
        return None
