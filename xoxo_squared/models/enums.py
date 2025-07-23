"""
Enumerations for xoxo^2 game
"""

from enum import Enum


class TileShape(Enum):
    """Represents the shape of a tile"""
    HEXAGON = "hexagon"
    STAR = "star"


class TileColor(Enum):
    """Represents the color of a tile side"""
    RED = "red"
    GREEN = "green"
    
    def opposite(self) -> 'TileColor':
        """Return the opposite color"""
        return TileColor.GREEN if self == TileColor.RED else TileColor.RED


class GamePhase(Enum):
    """Represents the current phase of the game"""
    FLIP_SELECTION = "flip_selection"
    MOVE_SELECTION = "move_selection"
    COLOR_SELECTION = "color_selection"
    TILE_PLACEMENT = "tile_placement"
    GAME_OVER = "game_over"