from yazelc.components import Velocity, Position
from yazelc.cutscene.task import Task
from yazelc.utils.game_utils import IVec, Direction
from yazelc.zesper import World


class MoveTask(Task):
    """ Moves from initial position to final one in the closes direction to the 8 moving possible ones """

    def __init__(self, entity: int, final_pos: IVec, duration_frames: int):
        self.entity = entity
        self.final_pos = final_pos
        self.duration_frames = duration_frames
        self._velocity_calculated = False

    def update(self, world: World):
        if not self._velocity_calculated:
            velocity = self._get_velocity(world)
            world.add_component(self.entity, velocity)
            self._velocity_calculated = True
        self.duration_frames -= 1

    def is_finished(self, world: World) -> bool:
        if self.duration_frames <= 0:
            world.remove_component(self.entity, Velocity)
            return True
        else:
            return False

    def _get_velocity(self, world: World):
        initial_pos = world.component_for_entity(self.entity, Position)
        diff_vec = IVec.sub(self.final_pos, initial_pos)
        direction = Direction.closest_direction(diff_vec)
        # self.actual_final_pos = direction.to_ivec(diff_vec.length)
        return Velocity.from_direction(direction, diff_vec.length / self.duration_frames)
