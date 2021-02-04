from pathlib import Path

import pygame

from adventure_game.animation import Animation


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
