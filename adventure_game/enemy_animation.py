from adventure_game.animation import Animation


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
