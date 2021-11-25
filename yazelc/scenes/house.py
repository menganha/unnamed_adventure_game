from yazelc.scenes import GameplayScene


class HouseScene(GameplayScene):

    @property
    def map_data_file(self):
        return 'data/house.tmx'
