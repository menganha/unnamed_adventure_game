from unnamed_adventure_game.scenes import GameplayScene


class OverWorldScene(GameplayScene):

    @property
    def map_data_file(self):
        return 'data/overworld_map.tmx'