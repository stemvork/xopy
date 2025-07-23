"""
Board class for xoxo^2 game
"""

from typing import Optional, List
from .data_classes import Position, ThreeInRowResult
from .tile import Tile
from .enums import TileColor


class Board:
    """Represents the 4x4 game board"""
    
    def __init__(self, size: int = 4):
        """
        Initialize the board
        
        Args:
            size: Size of the square board (default 4 for 4x4)
        """
        if size <= 0:
            raise ValueError("Board size must be positive")
        
        self._size = size
        self._grid = [[None for _ in range(size)] for _ in range(size)]
    
    @property
    def size(self) -> int:
        """Get the board size"""
        return self._size
    
    def place_tile(self, position: Position, tile: Tile) -> bool:
        """
        Place a tile on the board
        
        Args:
            position: Where to place the tile
            tile: The tile to place
            
        Returns:
            True if placement was successful, False otherwise
        """
        if not self._is_valid_position(position):
            return False
        
        if not self.is_position_empty(position):
            return False
        
        self._grid[position.row][position.col] = tile
        return True
    
    def remove_tile(self, position: Position) -> Optional[Tile]:
        """
        Remove a tile from the board
        
        Args:
            position: Position to remove tile from
            
        Returns:
            The removed tile, or None if no tile was there
        """
        if not self._is_valid_position(position):
            return None
        
        tile = self._grid[position.row][position.col]
        self._grid[position.row][position.col] = None
        return tile
    
    def get_tile(self, position: Position) -> Optional[Tile]:
        """
        Get the tile at a position
        
        Args:
            position: Position to check
            
        Returns:
            The tile at that position, or None if empty
        """
        if not self._is_valid_position(position):
            return None
        
        return self._grid[position.row][position.col]
    
    def is_position_empty(self, position: Position) -> bool:
        """
        Check if a position is empty
        
        Args:
            position: Position to check
            
        Returns:
            True if position is empty, False otherwise
        """
        return self.get_tile(position) is None
    
    def get_valid_moves(self, position: Position) -> List[Position]:
        """
        Get valid orthogonal moves from a position
        
        Args:
            position: Starting position
            
        Returns:
            List of valid adjacent positions that are empty
        """
        if not self._is_valid_position(position):
            return []
        
        valid_moves = []
        
        # Check all four orthogonal directions
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        
        for row_delta, col_delta in directions:
            new_row = position.row + row_delta
            new_col = position.col + col_delta
            
            # Check if new position is within bounds
            if 0 <= new_row < self._size and 0 <= new_col < self._size:
                new_position = Position(new_row, new_col)
                if self.is_position_empty(new_position):
                    valid_moves.append(new_position)
        
        return valid_moves
    
    def is_full(self) -> bool:
        """
        Check if the board is full
        
        Returns:
            True if all positions are occupied, False otherwise
        """
        for row in range(self._size):
            for col in range(self._size):
                if self._grid[row][col] is None:
                    return False
        return True
    
    def get_all_tiles(self) -> List[tuple[Position, Tile]]:
        """
        Get all tiles on the board with their positions
        
        Returns:
            List of (position, tile) tuples
        """
        tiles = []
        for row in range(self._size):
            for col in range(self._size):
                tile = self._grid[row][col]
                if tile is not None:
                    tiles.append((Position(row, col), tile))
        return tiles
    
    def check_three_in_row(self) -> List[ThreeInRowResult]:
        """
        Check for three-in-a-row formations of the same color
        
        Returns:
            List of ThreeInRowResult objects for all found three-in-a-row formations
        """
        results = []
        
        # Check horizontal lines
        for row in range(self._size):
            for col in range(self._size - 2):  # Need at least 3 positions
                positions = [Position(row, col + i) for i in range(3)]
                result = self._check_line_for_three_in_row(positions, "horizontal")
                if result:
                    results.append(result)
        
        # Check vertical lines
        for col in range(self._size):
            for row in range(self._size - 2):  # Need at least 3 positions
                positions = [Position(row + i, col) for i in range(3)]
                result = self._check_line_for_three_in_row(positions, "vertical")
                if result:
                    results.append(result)
        
        # Check diagonal lines (top-left to bottom-right)
        for row in range(self._size - 2):
            for col in range(self._size - 2):
                positions = [Position(row + i, col + i) for i in range(3)]
                result = self._check_line_for_three_in_row(positions, "diagonal")
                if result:
                    results.append(result)
        
        # Check diagonal lines (top-right to bottom-left)
        for row in range(self._size - 2):
            for col in range(2, self._size):
                positions = [Position(row + i, col - i) for i in range(3)]
                result = self._check_line_for_three_in_row(positions, "diagonal")
                if result:
                    results.append(result)
        
        return results
    
    def _check_line_for_three_in_row(self, positions: List[Position], direction: str) -> Optional[ThreeInRowResult]:
        """
        Check if a line of positions has three tiles of the same color
        
        Args:
            positions: List of 3 positions to check
            direction: Direction type ("horizontal", "vertical", "diagonal")
            
        Returns:
            ThreeInRowResult if three-in-a-row found, None otherwise
        """
        if len(positions) != 3:
            return None
        
        # Get tiles at all positions
        tiles = []
        for pos in positions:
            tile = self.get_tile(pos)
            if tile is None:
                return None  # Empty position, no three-in-a-row
            tiles.append(tile)
        
        # Check if all tiles have the same color AND same shape (symbol)
        first_color = tiles[0].get_current_color()
        first_shape = tiles[0].get_shape()
        
        if (all(tile.get_current_color() == first_color for tile in tiles) and
            all(tile.get_shape() == first_shape for tile in tiles)):
            return ThreeInRowResult(positions=positions, color=first_color, direction=direction)
        
        return None
    
    def can_opponent_break_three_in_row(self, three_in_row: ThreeInRowResult, opponent: 'Player') -> bool:
        """
        Check if an opponent can break a three-in-a-row formation on their next turn
        
        Args:
            three_in_row: The three-in-a-row formation to check
            opponent: The opponent player
            
        Returns:
            True if opponent can break the formation, False otherwise
        """
        # For each tile in the three-in-a-row, check if opponent can flip and move it
        for position in three_in_row.positions:
            tile = self.get_tile(position)
            if tile is None:
                continue
            
            # Check if this tile has valid moves (can be flipped and moved)
            valid_moves = self.get_valid_moves(position)
            if len(valid_moves) > 0:
                # Simulate flipping the tile
                original_color = tile.get_current_color()
                tile.flip()
                new_color = tile.get_current_color()
                
                # If flipping changes the color, the three-in-a-row can be broken
                if new_color != original_color:
                    # Flip back to restore original state
                    tile.flip()
                    return True
                
                # Flip back to restore original state
                tile.flip()
        
        return False
    
    def simulate_all_opponent_moves(self, opponent: 'Player') -> List[ThreeInRowResult]:
        """
        Simulate all possible opponent moves and return any three-in-a-row they could create
        
        Args:
            opponent: The opponent player
            
        Returns:
            List of three-in-a-row formations opponent could create
        """
        potential_three_in_rows = []
        
        # Get all tiles on the board that can be moved
        all_tiles = self.get_all_tiles()
        
        for position, tile in all_tiles:
            valid_moves = self.get_valid_moves(position)
            
            for move_to in valid_moves:
                # Simulate the flip and move
                original_color = tile.get_current_color()
                
                # Flip the tile
                tile.flip()
                flipped_color = tile.get_current_color()
                
                # Temporarily move the tile
                self._grid[position.row][position.col] = None
                self._grid[move_to.row][move_to.col] = tile
                
                # Check for three-in-a-row after this move
                three_in_rows = self.check_three_in_row()
                potential_three_in_rows.extend(three_in_rows)
                
                # Restore the board state
                self._grid[move_to.row][move_to.col] = None
                self._grid[position.row][position.col] = tile
                
                # Restore original color
                if tile.get_current_color() != original_color:
                    tile.flip()
        
        return potential_three_in_rows
    
    def _is_valid_position(self, position: Position) -> bool:
        """
        Check if a position is valid for this board
        
        Args:
            position: Position to validate
            
        Returns:
            True if position is within board bounds
        """
        return (0 <= position.row < self._size and 
                0 <= position.col < self._size)
    
    def __repr__(self) -> str:
        """String representation of the board"""
        lines = []
        for row in range(self._size):
            line = []
            for col in range(self._size):
                tile = self._grid[row][col]
                if tile is None:
                    line.append("  -  ")
                else:
                    color_char = "R" if tile.get_current_color() == TileColor.RED else "G"
                    shape_char = "◆" if tile.get_shape().value == "hexagon" else "★"
                    line.append(f" {color_char}{shape_char} ")
            lines.append("".join(line))
        return "\n".join(lines)