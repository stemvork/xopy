"""
Tile class for xoxo^2 game
"""

from .enums import TileShape, TileColor


class Tile:
    """Represents a game tile with shape, color, and owner"""
    
    def __init__(self, shape: TileShape, initial_color: TileColor, owner: 'Player'):
        """
        Initialize a tile
        
        Args:
            shape: The shape of the tile (HEXAGON or STAR)
            initial_color: The initial color side facing up
            owner: The player who owns this tile
        """
        if shape is None:
            raise ValueError("Tile shape cannot be None")
        if initial_color is None:
            raise ValueError("Tile initial color cannot be None")
        if owner is None:
            raise ValueError("Tile owner cannot be None")
            
        self._shape = shape
        self._current_color = initial_color
        self._owner = owner
    
    def flip(self) -> None:
        """Flip the tile to show the opposite color"""
        if self._current_color is None:
            raise ValueError(f"Cannot flip tile - current color is None for tile {self}")
        try:
            self._current_color = self._current_color.opposite()
        except AttributeError as e:
            raise ValueError(f"Error flipping tile - current color {self._current_color} has no opposite method: {e}")
    
    def get_current_color(self) -> TileColor:
        """Get the current color side facing up"""
        return self._current_color
    
    def get_shape(self) -> TileShape:
        """Get the shape of the tile"""
        return self._shape
    
    def get_owner(self) -> 'Player':
        """Get the player who owns this tile"""
        return self._owner
    
    def __repr__(self) -> str:
        """String representation of the tile"""
        return f"Tile({self._shape.value}, {self._current_color.value}, owner={self._owner.name})"
    
    def __eq__(self, other) -> bool:
        """Check equality with another tile"""
        if not isinstance(other, Tile):
            return False
        return (self._shape == other._shape and 
                self._current_color == other._current_color and
                self._owner == other._owner)