import esper

import unnamed_adventure_game.config as cfg
from unnamed_adventure_game.components import Position, Renderable


class CameraSystem(esper.Processor):
    """
    Updates the camera entity to center around the input entity position
    """

    def __init__(self, camera_entity: int, entity_followed: int):
        super().__init__()
        self.camera_entity = camera_entity
        self.entity_followed = entity_followed
        self.ent_ = None
        self.entity_tracked_relative_coord = None

    def process(self):
        camera_pos = self.world.component_for_entity(self.camera_entity, Position)
        entity_followed_pos = self.world.component_for_entity(self.entity_followed, Position)

        # Check if the the followed entity is a visible object and extract and memoize its dimensions
        if not self.entity_tracked_relative_coord:
            self.entity_tracked_relative_coord = [0, 0]
            if renderable := self.world.try_component(self.entity_followed, Renderable):
                self.entity_tracked_relative_coord[0] = int((cfg.RESOLUTION[0] - renderable.width) / 2)
                self.entity_tracked_relative_coord[1] = int((cfg.RESOLUTION[1] - renderable.height) / 2)

        camera_pos.x = - entity_followed_pos.x + self.entity_tracked_relative_coord[0]
        camera_pos.y = - entity_followed_pos.y + self.entity_tracked_relative_coord[1]

        camera_pos.x = min(0, camera_pos.x)
        camera_pos.y = min(0, camera_pos.y)
