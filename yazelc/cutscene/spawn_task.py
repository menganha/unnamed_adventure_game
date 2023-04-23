from typing import Any

from yazelc.cutscene.task import Task
from yazelc.zesper import World


class SpawnTask(Task):
    """ Creates an entity with the given components and delete it if duration_frames is negative """

    def __init__(self, *components: Any, duration_frames: int = 1):
        self.components = components
        self.duration_frames = duration_frames if duration_frames >= 0 else 1
        self._ent_id = None
        self._delete_on_finished = duration_frames >= 0

    def update(self, world: World):
        if self._ent_id is None:
            self._ent_id = world.create_entity(*self.components)
        self.duration_frames -= 1

    def is_finished(self, world: World) -> bool:
        finished = self.duration_frames <= 0
        if finished and self._delete_on_finished:
            world.delete_entity(self._ent_id)
        return finished
