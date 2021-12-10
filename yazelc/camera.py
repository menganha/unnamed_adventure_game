from yazelc import config as cfg
from yazelc import zesper
from yazelc.components import Position, Renderable, Vector


def create_camera(world: zesper.World):
    world.camera_entity_id = world.create_entity()
    world.add_component(world.camera_entity_id, Position(0, 0))


def get_position_of_entity_to_track(entity_id_to_follow: int, world: zesper.World) -> Vector:
    """
    Used to get the relative position of the entity to track with respect to the camera

    If the tracked entity has a renderable (image) then get the center of that image, otherwise get the position of
    that entity, and if it doesn't have any of the previous two components then return 0,0, i.e., just get a fixed camera
    """
    if renderable := world.try_component(entity_id_to_follow, Renderable):
        return Vector(int((cfg.RESOLUTION.x - renderable.width) / 2), int((cfg.RESOLUTION.y - renderable.height) / 2))
    elif position := world.try_component(entity_id_to_follow, Position):
        return Vector(int((cfg.RESOLUTION.x - position.x) / 2), int((cfg.RESOLUTION.y - position.y) / 2))
    else:
        return Vector(0, 0)
