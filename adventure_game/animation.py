import pygame
from pathlib import Path


class Animation():
    """
    Class to create sprite animation
    """
    def __init__(self, sprite_sheet_data, animation_data, sprite_sheet_names):
        self.sprite_sheet_data = self._check_sprite_sheet_data(sprite_sheet_data)
        self.sprite_sheets = self._load_sprite_sheets(sprite_sheet_names)
        self.surfaces_dict = self._get_surfaces_dict()
        self.animation_data = animation_data
        self.counter = 0
        self.current_key = list(animation_data.keys())[0]
        self.current_sprite = self.surfaces_dict[self.current_key][0]

    def _check_sprite_sheet_data(self, sprite_sheet_data):
        if 'sprite_size' not in sprite_sheet_data:
            raise ValueError("The sprite sheet data dictionary does not contain the key sprite_size")
        else:
            return sprite_sheet_data

    def _load_sprite_sheets(self, sprite_sheet_names):
        return pygame.image.load(sprite_sheet_names).convert_alpha()

    def _get_surfaces_dict(self):
        """
        Load all the sprites images as surfaces and store them in a
        dictionary where each key correspond to a list of surfaces which
        consist of frames in an animation
        """
        sheet_size = self.sprite_sheets.get_size()
        frame_dict = {}
        for iy in range(sheet_size[1]//self.sprite_sheet_data['sprite_size']):
            frames_x = []
            for ix in range(sheet_size[0]//self.sprite_sheet_data['sprite_size']):
                rect = pygame.Rect(ix*self.sprite_sheet_data['sprite_size'], iy*self.sprite_sheet_data['sprite_size'], self.sprite_sheet_data['sprite_size'], self.sprite_sheet_data['sprite_size'])
                frame = self.sprite_sheets.subsurface(rect)
                frames_x.append(frame)
            frame_dict.update({self.sprite_sheet_data[iy]: frames_x})
        return frame_dict

    def next_frame(self, animation_key):
        if self.current_key != animation_key:
            self.current_key = animation_key
            self.counter = 0
        frame_idx = self.animation_data[animation_key][self.counter]
        self.current_sprite = self.surfaces_dict[animation_key][frame_idx]
        self.counter += 1
        if self.counter >= len(self.animation_data[animation_key]):
            self.counter = 0


class PlayerAnimation(Animation):
    frame_duration_data = {
            "walk down": [20, 20, 20, 20, 20, 20],
            "walk right": [20, 20, 20, 20, 20, 20],
            "walk up": [20, 20, 20, 20, 20, 20],
            "walk left": [20, 20, 20, 20, 20, 20],
            "idle down": [20, 20, 20, 20, 20, 20]
        }
    sprite_sheet_data = {
            "sprite_size": 16
        }
    path = Path('./assets/sprites/player')

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
            animation_data.update({key: frames_idx})
        return animation_data

    def _get_sprite_sheet_names(self, animation_data):
        sprite_sheet_names = {}
        for key in animation_data:
            folder, name = key.split(' ')
            file = self.path.joinpath(folder, name + ".png")
            if not file.is_file():
                raise ValueError("File: {:} was not found".format(file))
            sprite_sheet_names.update({key: file})
        return sprite_sheet_names

    def _load_sprite_sheets(self, sprite_sheet_names):
        sprite_sheets = {}
        for key in sprite_sheet_names:
            sprite_sheets.update({
                key: pygame.image.load(str(sprite_sheet_names[key])).convert_alpha()})
        return sprite_sheets

    def _get_surfaces_dict(self):
        frame_dict = {}
        for key, sprite_sheet in self.sprite_sheets.items():
            sheet_size = sprite_sheet.get_size()
            frames = []
            if 'idle' in key:
                extra_pixel_row = 0
            else:
                extra_pixel_row = 1
            for ix in range(sheet_size[0]//self.sprite_sheet_data['sprite_size']):
                rect = pygame.Rect(
                    ix*self.sprite_sheet_data['sprite_size'],
                    0,
                    self.sprite_sheet_data['sprite_size'],
                    self.sprite_sheet_data['sprite_size'] + extra_pixel_row
                    )
                frames.append(sprite_sheet.subsurface(rect))
            frame_dict.update({key: frames})
        return frame_dict
