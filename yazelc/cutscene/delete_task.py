from yazelc.cutscene.task import Task
from yazelc.zesper import World


class DeleteTask(Task):
    """ Moves from initial position to final one in the closes direction to the 8 moving possible ones """

    def __init__(self, entity: int):
        self.entity = entity
        self.finished = False

    def update(self, world: World):
        world.delete_entity(self.entity)
        self.finished = True

    def is_finished(self, world: World) -> bool:
        return self.finished
