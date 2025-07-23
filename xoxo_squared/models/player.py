"""
Player class for xoxo^2 game
"""

from .enums import TileShape, TileColor
from .tile import Tile


class Player:
    """Represents a player in the xoxo^2 game"""
    
    def __init__(self, name: str, shape: TileShape, tiles_remaining: int = 8):
        """
        Initialize a player
        
        Args:
            name: The player's name
            shape: The shape of tiles this player uses (HEXAGON or STAR)
            tiles_remaining: Number of tiles the player starts with (default 8)
        """
        if tiles_remaining < 0:
            raise ValueError("Tiles remaining cannot be negative")
        
        self._name = name
        self._shape = shape
        self._tiles_remaining = tiles_remaining
    
    @property
    def name(self) -> str:
        """Get the player's name"""
        return self._name
    
    def use_tile(self, initial_color: TileColor) -> Tile:
        """
        Create and use a tile from the player's supply
        
        Args:
            initial_color: The initial color side to show
            
        Returns:
            A new Tile object
            
        Raises:
            ValueError: If no tiles remaining
        """
        if not self.can_place_tile():
            raise ValueError(f"Player {self._name} has no tiles remaining")
        
        self._tiles_remaining -= 1
        return Tile(self._shape, initial_color, self)
    
    def get_tiles_remaining(self) -> int:
        """Get the number of tiles remaining"""
        return self._tiles_remaining
    
    def can_place_tile(self) -> bool:
        """Check if the player can place a tile"""
        return self._tiles_remaining > 0
    
    def get_shape(self) -> TileShape:
        """Get the player's tile shape"""
        return self._shape
    
    def __repr__(self) -> str:
        """String representation of the player"""
        return f"Player({self._name}, {self._shape.value}, {self._tiles_remaining} tiles)"
    
    def __eq__(self, other) -> bool:
        """Check equality with another player"""
        if not isinstance(other, Player):
            return False
        return (self._name == other._name and 
                self._shape == other._shape and
                self._tiles_remaining == other._tiles_remaining)