from yazelc import zesper
from yazelc.components import TweenPosition, Velocity
from yazelc.tween import tweening


class TweenSystem(zesper.Processor):

    def process(self):
        for ent, (tween, velocity) in self.world.get_components(TweenPosition, Velocity):
            if tween.frame_counter == tween.n_frames:
                if tween.rest_frames == 0:
                    self.world.remove_component(ent, TweenPosition)
                else:
                    tween.rest_frames -= 1
            else:
                time = tween.frame_counter / tween.n_frames
                new_relative_position = tweening(time, tween.function) * tween.length
                abs_vel = new_relative_position - tween.previous_relative_position
                velocity.update(tween.direction.value.x * abs_vel, tween.direction.value.y * abs_vel)
                tween.frame_counter += 1
                tween.previous_relative_position = new_relative_position
