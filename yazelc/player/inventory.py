from yazelc.components import Pickable
from yazelc.items import PickableItemType


class Inventory:
    def __init__(self, n_keys: int = 0, n_bombs: int = 0, n_arrows: int = 0, n_coins: int = 0):
        self.n_keys = n_keys
        self.n_bombs = n_bombs
        self.n_arrows = n_arrows
        self.n_coins = n_coins
        # Here we may include weapons, etc., perhaps some other stuff like how many levels one has passed, etc, i.e., the current
        # state of the player. Or perhaps we should include this in another instance??

    def add_pickable(self, pickable: Pickable) -> int:
        if pickable.item_type == PickableItemType.COIN:
            self.n_coins += pickable.value
            return self.n_coins
        if pickable.item_type == PickableItemType.BOMB:
            self.n_bombs += pickable.value
            return self.n_bombs
        if pickable.item_type == PickableItemType.ARROW:
            self.n_arrows += pickable.value
            return self.n_arrows
        if pickable.item_type == PickableItemType.KEY:
            self.n_keys += pickable.value
            return self.n_keys
