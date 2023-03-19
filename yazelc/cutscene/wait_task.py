from yazelc.cutscene.task import Task
from yazelc.zesper import World


class WaitTask(Task):

    def __init__(self, duration_frames: int):
        self.duration_frames = duration_frames

    def update(self, world: World):
        self.duration_frames -= 1

    def is_finished(self, world: World) -> bool:
        return self.duration_frames <= 0
