from yazelc.components import Renderable
from yazelc.cutscene.task import Task
from yazelc.tween import TweenFunction, tweening
from yazelc.zesper import World


class FadeInTask(Task):
    """ Moves from initial position to final one in the closes direction to the 8 moving possible ones """
    MAX_ALPHA = 255

    def __init__(self, entity: int, tween_function: TweenFunction, duration_frames: int):
        self.entity = entity
        self.tween_function = tween_function
        self.frame_counter = 0
        self.duration_frames = duration_frames

    def update(self, world: World):
        time = self.frame_counter / (self.duration_frames - 1)
        alpha_value = tweening(time, self.tween_function) * self.MAX_ALPHA
        image = world.component_for_entity(self.entity, Renderable).image
        image.set_alpha(alpha_value)
        self.frame_counter += 1

    def is_finished(self, world: World) -> bool:
        return self.frame_counter >= self.duration_frames

class FadeOutTask(FadeInTask):
    """ Moves from initial position to final one in the closes direction to the 8 moving possible ones """

    def update(self, world: World):
        time = self.frame_counter / (self.duration_frames - 1)
        alpha_value = tweening(1 - time, self.tween_function) * self.MAX_ALPHA
        image = world.component_for_entity(self.entity, Renderable).image
        image.set_alpha(alpha_value)
        self.frame_counter += 1
