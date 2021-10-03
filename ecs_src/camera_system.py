from . import esper
from .components import Position, Renderable
from .config import Config


class CameraSystem(esper.Processor):
    """
    Updates the camera entity to center around the input entity position
    """
    def __init__(self, camera_entity: int, entity_followed: int):
        super().__init__()
        self.camera_entity = camera_entity
        self.entity_followed = entity_followed
        self.ent_tracked_width = None
        self.ent_tracked_height = None

    def process(self):
        camera_pos = self.world.component_for_entity(self.camera_entity, Position)
        entity_followed_pos = self.world.component_for_entity(self.entity_followed, Position)

        # Check if the the followed entity is a physical object (renderable) and extract and memoize
        # its dimensions
        if not (self.ent_tracked_height and self.ent_tracked_width):
            self.ent_tracked_width = 0
            self.ent_tracked_height = 0
            renderable = self.world.try_component(self.entity_followed, Renderable)
            if renderable:
                self.ent_tracked_width = renderable.width
                self.ent_tracked_height = renderable.height

        camera_pos.x = - entity_followed_pos.x + int((Config.RESOLUTION[0] - self.ent_tracked_width)/2)
        camera_pos.y = - entity_followed_pos.y + int((Config.RESOLUTION[1] - self.ent_tracked_height)/2)

        camera_pos.x = min(0, camera_pos.x)
        camera_pos.y = min(0, camera_pos.y)
