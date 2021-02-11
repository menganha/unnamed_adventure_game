from typing import List, Dict

from adventure_game.direction import Direction


class AnimationData:
    def __init__(self, number_of_frames: int, frame_duration: int, frame_index: Dict[Direction, List[int]] = None):
        self.number_of_frames = number_of_frames
        self.frame_duration = frame_duration
        if frame_index:
            self.frame_index = frame_index
        else:
            self.frame_index = {
                Direction.LEFT: self.expand_animation_data(),
                Direction.UP: self.expand_animation_data(),
                Direction.DOWN: self.expand_animation_data(),
                Direction.RIGHT: self.expand_animation_data()
            }

    def expand_animation_data(self) -> List[int]:
        data = []
        for idx in range(self.number_of_frames):
            data.extend([idx] * self.frame_duration)
        return data
