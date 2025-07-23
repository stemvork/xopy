"""
Data classes for xoxo^2 game
"""

from dataclasses import dataclass
from typing import Optional, List
from .enums import TileColor, GamePhase


@dataclass
class Position:
    """Represents a position on the game board"""
    row: int
    col: int
    
    def __post_init__(self):
        """Validate position bounds for 4x4 board"""
        if not (0 <= self.row <= 3):
            raise ValueError(f"Row must be between 0 and 3, got {self.row}")
        if not (0 <= self.col <= 3):
            raise ValueError(f"Column must be between 0 and 3, got {self.col}")
    
    def is_adjacent_orthogonal(self, other: 'Position') -> bool:
        """Check if this position is orthogonally adjacent to another"""
        row_diff = abs(self.row - other.row)
        col_diff = abs(self.col - other.col)
        return (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1)
    
    def __lt__(self, other: 'Position') -> bool:
        """Less than comparison for sorting"""
        if self.row != other.row:
            return self.row < other.row
        return self.col < other.col
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if not isinstance(other, Position):
            return False
        return self.row == other.row and self.col == other.col
    
    def __hash__(self) -> int:
        """Hash for use in sets and dicts"""
        return hash((self.row, self.col))


@dataclass
class Move:
    """Represents a complete move in the game"""
    flip_position: Optional[Position]
    move_to_position: Optional[Position]
    place_position: Position
    
    def __post_init__(self):
        """Validate move structure"""
        # For first move, only place_position should be set
        if self.flip_position is None and self.move_to_position is not None:
            raise ValueError("Cannot have move_to_position without flip_position")
        
        # If flipping, must also move
        if self.flip_position is not None and self.move_to_position is None:
            raise ValueError("Must specify move_to_position when flipping a tile")
        
        # Validate orthogonal movement
        if (self.flip_position is not None and self.move_to_position is not None 
            and not self.flip_position.is_adjacent_orthogonal(self.move_to_position)):
            raise ValueError("Move must be orthogonal (adjacent horizontally or vertically)")


@dataclass
class ThreeInRowResult:
    """Represents a three-in-a-row formation on the board"""
    positions: List[Position]
    color: TileColor
    direction: str  # "horizontal", "vertical", "diagonal"
    
    def __post_init__(self):
        """Validate three-in-a-row result"""
        if len(self.positions) != 3:
            raise ValueError("Three-in-a-row must have exactly 3 positions")
        if self.direction not in ["horizontal", "vertical", "diagonal"]:
            raise ValueError(f"Invalid direction: {self.direction}")


@dataclass
class GameEvent:
    """Represents a user input event"""
    event_type: str  # "click", "key", "quit"
    position: Optional[Position] = None
    key: Optional[str] = None
    
    def __post_init__(self):
        """Validate game event"""
        valid_types = ["click", "key", "quit", "button_click", "ui_click"]
        if self.event_type not in valid_types:
            raise ValueError(f"Invalid event type: {self.event_type}")
        
        if self.event_type == "click" and self.position is None:
            raise ValueError("Click events must have a position")
        
        if self.event_type in ["key", "button_click", "ui_click"] and self.key is None:
            raise ValueError(f"{self.event_type} events must have a key")


@dataclass
class GameState:
    """Represents the current state of the game"""
    current_player: 'Player'  # Forward reference
    phase: GamePhase
    move_count: int
    winner: Optional['Player'] = None  # Forward reference
    
    def __post_init__(self):
        """Validate game state"""
        if self.move_count < 0:
            raise ValueError("Move count cannot be negative")
        
        if self.winner is not None and self.phase != GamePhase.GAME_OVER:
            raise ValueError("Game must be in GAME_OVER phase if there's a winner")