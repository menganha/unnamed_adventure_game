from yazelc import zesper
from yazelc.components import Tween, Velocity, TweenType


class TweenSystem(zesper.Processor):

    def process(self):
        for ent, (tween, velocity) in self.world.get_components(Tween, Velocity):
            if tween.frame_counter == tween.n_frames:
                if tween.rest_frames == 0:
                    self.world.remove_component(ent, Tween)
                else:
                    tween.rest_frames -= 1
            else:
                time = tween.frame_counter / tween.n_frames
                new_relative_position = self._position(time, tween.type) * tween.length
                abs_vel = new_relative_position - tween.previous_relative_position
                velocity.update(tween.direction.value.x * abs_vel, tween.direction.value.y * abs_vel)
                tween.frame_counter += 1
                tween.previous_relative_position = new_relative_position

    @staticmethod
    def _position(time: float, tween_type: TweenType):
        if tween_type == TweenType.EASE_OUT_CUBIC:
            return TweenSystem.ease_out_cubic(time)
        elif tween_type == TweenType.EASE_OUT_QUINT:
            return TweenSystem.ease_out_quint(time)
        elif tween_type == TweenType.EASE_OUT_EXPO:
            return TweenSystem.ease_out_expo(time)
        else:
            raise NotImplementedError(f'Tween type {tween_type.name} not implemented')

    @staticmethod
    def ease_out_cubic(time: float):
        """ tween function with argument from 0.0 to 1.0 """
        time = time - 1
        return time ** 3 + 1

    @staticmethod
    def ease_out_quint(time: float):
        """ tween function with argument from 0.0 to 1.0 """
        time = time - 1
        return time ** 5 + 1

    @staticmethod
    def ease_out_expo(time: float):
        """ tween function with argument from 0.0 to 1.0 """
        if time == 1:
            return 1
        else:
            return -(2 ** (-10 * time)) + 1
