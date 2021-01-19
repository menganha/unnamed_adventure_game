from pathlib import Path

import pygame


class Animation:
    """
    Class to create sprite animation
    """

    def __init__(self, sprite_sheet_data, animation_data, sprite_sheet_names):
        self.animation_data = animation_data
        self.sprite_sheet_data = self._check_sprite_sheet_data(sprite_sheet_data)
        self.sprite_sheets = self._load_sprite_sheets(sprite_sheet_names)
        self.surfaces_dict = self._get_surfaces_dict()
        self.counter = 0
        self.current_key = list(animation_data.keys())[0]
        self.current_sprite = self.surfaces_dict[self.current_key][0]

    @staticmethod
    def _check_sprite_sheet_data(sprite_sheet_data):
        if "sprite_size" not in sprite_sheet_data:
            raise ValueError(
                "The sprite sheet data dictionary does not contain the key sprite_size"
            )
        else:
            return sprite_sheet_data

    def _load_sprite_sheets(self, sprite_sheet_names):
        sprite_sheets = {}
        for key in self.animation_data:
            sprite_sheets.update(
                {key: pygame.image.load(sprite_sheet_names).convert_alpha()}
            )
        return sprite_sheets

    def _get_surfaces_dict(self):
        """
        Load all the sprites images as surfaces and store them in a
        dictionary where each key correspond to a list of surfaces which
        consist of frames in an animation
        """
        frame_dict = {}
        for key in self.animation_data:
            sheet_size = self.sprite_sheets[key].get_size()
            frames_x = []
            for idx in range(sheet_size[0] // self.sprite_sheet_data["sprite_size"]):
                rect = pygame.Rect(
                    idx * self.sprite_sheet_data["sprite_size"],
                    0,
                    self.sprite_sheet_data["sprite_size"],
                    self.sprite_sheet_data["sprite_size"],
                )
                frame = self.sprite_sheets[key].subsurface(rect)
                frames_x.append(frame)
            frame_dict.update({key: frames_x})
        return frame_dict

    def next_frame(self, animation_key):
        if self.current_key != animation_key:
            self.current_key = animation_key
            self.counter = 0
        frame_idx = self.animation_data[animation_key][self.counter]
        if "right" in animation_key:
            self.current_sprite = pygame.transform.flip(
                self.surfaces_dict[animation_key][frame_idx], True, False
            )
        else:
            self.current_sprite = self.surfaces_dict[animation_key][frame_idx]
        self.counter += 1
        if self.counter >= len(self.animation_data[animation_key]):
            self.counter = 0

    def reset(self):
        self.counter = 0
        frame_idx = self.animation_data[self.current_key][self.counter]
        if "right" in self.current_key:
            self.current_sprite = pygame.transform.flip(
                self.surfaces_dict[self.current_key][frame_idx], True, False
            )
        else:
            self.current_sprite = self.surfaces_dict[self.current_key][frame_idx]

    @staticmethod
    def _get_animation_data(frame_duration_data):
        animation_data = {}
        for key in frame_duration_data:
            frames_duration = frame_duration_data[key][0]
            frames_idx = []
            for idx, duration in enumerate(frames_duration):
                frames_idx.extend([idx for _ in range(duration)])
            animation_data.update({key: frames_idx})
        return animation_data


class EnemyAnimation(Animation):
    @classmethod
    def create_jelly_animation(cls):
        frame_data = {"walk": [(10, 10, 10), r"/assets/sprites/enemy/jelly.png"]}
        sprite_sheet_data = {"sprite_size": 16}
        animation_data = cls._get_animation_data(frame_data)
        sprite_sheet_names = r"./assets/sprites/enemy/jelly.png"
        return cls(sprite_sheet_data, animation_data, sprite_sheet_names)

    @classmethod
    def create_dragon_animation(cls):
        frame_data = {"walk": [(15, 15), r"/assets/sprites/enemy/dragon.png"]}
        sprite_sheet_data = {"sprite_size": 64}
        animation_data = cls._get_animation_data(frame_data)
        sprite_sheet_names = r"./assets/sprites/enemy/dragon.png"
        return cls(sprite_sheet_data, animation_data, sprite_sheet_names)


class PlayerAnimation(Animation):
    frame_duration_data = {
        "walk down": [20, 20, 20, 20, 20, 20],
        "walk right": [20, 20, 20, 20, 20, 20],
        "walk up": [20, 20, 20, 20, 20, 20],
        "walk left": [20, 20, 20, 20, 20, 20],
        "attack down": [3, 3, 3, 3, 3],
        "attack right": [3, 3, 3, 3, 3],
        "attack up": [3, 3, 3, 3, 3],
        "attack left": [3, 3, 3, 3, 3],
    }
    sprite_sheet_data = {"sprite_size": 32}
    path = Path("./assets/sprites/player")

    def __init__(self):
        animation_data = self._get_animation_data()
        sprite_sheet_names = self._get_sprite_sheet_names(animation_data)
        super().__init__(self.sprite_sheet_data, animation_data, sprite_sheet_names)

    def _get_animation_data(self):
        animation_data = {}
        for key in self.frame_duration_data:
            frames_duration = self.frame_duration_data[key]
            frames_idx = []
            for idx, duration in enumerate(frames_duration):
                frames_idx.extend([idx for _ in range(duration)])
            # if 'right' in key:
            #     frames_idx.reverse()
            if "attack" in key:
                frames_idx.extend([0])
            animation_data.update({key: frames_idx})
        return animation_data

    def _get_sprite_sheet_names(self, animation_data):
        sprite_sheet_names = {}
        for key in animation_data:
            folder, name = key.split(" ")
            if "right" in key:
                name = "left"
            file = self.path.joinpath(folder, name + ".png")
            if not file.is_file():
                raise ValueError("File: {:} was not found".format(file))
            sprite_sheet_names.update({key: file})
        return sprite_sheet_names

    def _load_sprite_sheets(self, sprite_sheet_names):
        sprite_sheets = {}
        for key in sprite_sheet_names:
            sprite_sheets.update(
                {key: pygame.image.load(str(sprite_sheet_names[key])).convert_alpha()}
            )
        return sprite_sheets

    def _get_surfaces_dict(self):
        frame_dict = {}
        for key, sprite_sheet in self.sprite_sheets.items():
            sheet_size = sprite_sheet.get_size()
            frames = []
            for idx in range(sheet_size[0] // self.sprite_sheet_data["sprite_size"]):
                rect = pygame.Rect(
                    idx * self.sprite_sheet_data["sprite_size"],
                    0,
                    self.sprite_sheet_data["sprite_size"],
                    self.sprite_sheet_data["sprite_size"],
                )
                frames.append(sprite_sheet.subsurface(rect))
            frame_dict.update({key: frames})
        return frame_dict
