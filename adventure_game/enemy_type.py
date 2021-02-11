from enum import Enum


class EnemyType(Enum):
    DRAGON = 'dragon'
    JELLY = 'jelly'

    @classmethod
    def get_type_from_value(cls, value):
        for enemy in cls:
            if enemy.value == value:
                return enemy
        raise ValueError('Value {} does not correspond to the enumeration value of an enemy type'.format(value))
