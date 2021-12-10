import yazelc.config as cfg
from yazelc import zesper
from yazelc.components import Position, Vector


class CameraSystem(zesper.Processor):
    """
    Updates the camera entity to center around the input entity position
    """

    def __init__(self, entity_followed: int, offset: Vector, max_dimensions: Vector):
        super().__init__()
        self.entity_followed = entity_followed
        self.max_dimensions = max_dimensions
        self.offset = offset

    def process(self):
        camera_pos = self.world.component_for_entity(self.world.camera_entity_id, Position)
        entity_followed_pos = self.world.component_for_entity(self.entity_followed, Position)

        camera_pos.x = entity_followed_pos.x - self.offset.x
        camera_pos.y = entity_followed_pos.y - self.offset.y

        camera_pos.x = max(0, camera_pos.x)
        camera_pos.y = max(0, camera_pos.y)
        camera_pos.x = min(self.max_dimensions.x - cfg.RESOLUTION.x, camera_pos.x)
        camera_pos.y = min(self.max_dimensions.y - cfg.RESOLUTION.y, camera_pos.y)
