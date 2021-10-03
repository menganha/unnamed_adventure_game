from . import esper
from .components import Position
from .config import Config


class CameraSystem(esper.Processor):
    """
    Updates the camera entity to center around the input entity position
    """
    def __init__(self, camera_entity: int, entity_followed: int):
        super().__init__()
        self.camera_entity = camera_entity
        self.entity_followed = entity_followed

    def process(self):
        camera_pos = self.world.component_for_entity(self.camera_entity, Position)
        entity_followed_pos = self.world.component_for_entity(self.entity_followed, Position)

        camera_pos.x = - entity_followed_pos.x + int(Config.RESOLUTION[0]/2)
        camera_pos.y = - entity_followed_pos.y + int(Config.RESOLUTION[1]/2)

        # map_pos.x = -camera_pos.x
        # map_pos.y = -camera_pos.y
        # for ent, pos in self.world.get_component(Position):
        #     pos.x -= camera_pos.x
        #     pos.y -= kamera_pos.y
