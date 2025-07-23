"""
Tests for core data models
"""

import pytest
from xoxo_squared.models import Position, Move, TileColor, GamePhase, ThreeInRowResult, GameEvent


class TestPosition:
    def test_valid_position(self):
        """Test creating valid positions"""
        pos = Position(0, 0)
        assert pos.row == 0
        assert pos.col == 0
        
        pos = Position(3, 3)
        assert pos.row == 3
        assert pos.col == 3
    
    def test_invalid_position_bounds(self):
        """Test position validation"""
        with pytest.raises(ValueError, match="Row must be between 0 and 3"):
            Position(-1, 0)
        
        with pytest.raises(ValueError, match="Row must be between 0 and 3"):
            Position(4, 0)
        
        with pytest.raises(ValueError, match="Column must be between 0 and 3"):
            Position(0, -1)
        
        with pytest.raises(ValueError, match="Column must be between 0 and 3"):
            Position(0, 4)
    
    def test_orthogonal_adjacency(self):
        """Test orthogonal adjacency checking"""
        center = Position(1, 1)
        
        # Adjacent positions
        assert center.is_adjacent_orthogonal(Position(0, 1))  # Up
        assert center.is_adjacent_orthogonal(Position(2, 1))  # Down
        assert center.is_adjacent_orthogonal(Position(1, 0))  # Left
        assert center.is_adjacent_orthogonal(Position(1, 2))  # Right
        
        # Non-adjacent positions
        assert not center.is_adjacent_orthogonal(Position(0, 0))  # Diagonal
        assert not center.is_adjacent_orthogonal(Position(2, 2))  # Diagonal
        assert not center.is_adjacent_orthogonal(Position(3, 1))  # Too far
        assert not center.is_adjacent_orthogonal(Position(1, 1))  # Same position


class TestMove:
    def test_first_move(self):
        """Test first move (placement only)"""
        move = Move(None, None, Position(1, 1))
        assert move.flip_position is None
        assert move.move_to_position is None
        assert move.place_position == Position(1, 1)
    
    def test_standard_move(self):
        """Test standard move with flip, move, and place"""
        move = Move(Position(0, 0), Position(0, 1), Position(2, 2))
        assert move.flip_position == Position(0, 0)
        assert move.move_to_position == Position(0, 1)
        assert move.place_position == Position(2, 2)
    
    def test_invalid_move_structure(self):
        """Test invalid move combinations"""
        # Cannot have move without flip
        with pytest.raises(ValueError, match="Cannot have move_to_position without flip_position"):
            Move(None, Position(0, 1), Position(2, 2))
        
        # Must have move if flipping
        with pytest.raises(ValueError, match="Must specify move_to_position when flipping"):
            Move(Position(0, 0), None, Position(2, 2))
    
    def test_non_orthogonal_movement(self):
        """Test validation of orthogonal movement"""
        # Diagonal movement should be invalid
        with pytest.raises(ValueError, match="Move must be orthogonal"):
            Move(Position(0, 0), Position(1, 1), Position(2, 2))
        
        # Too far movement should be invalid
        with pytest.raises(ValueError, match="Move must be orthogonal"):
            Move(Position(0, 0), Position(2, 0), Position(1, 1))


class TestTileColor:
    def test_opposite_colors(self):
        """Test color flipping"""
        assert TileColor.RED.opposite() == TileColor.GREEN
        assert TileColor.GREEN.opposite() == TileColor.RED


class TestThreeInRowResult:
    def test_valid_three_in_row(self):
        """Test valid three-in-a-row result"""
        positions = [Position(0, 0), Position(0, 1), Position(0, 2)]
        result = ThreeInRowResult(positions, TileColor.RED, "horizontal")
        assert len(result.positions) == 3
        assert result.color == TileColor.RED
        assert result.direction == "horizontal"
    
    def test_invalid_position_count(self):
        """Test validation of position count"""
        with pytest.raises(ValueError, match="Three-in-a-row must have exactly 3 positions"):
            ThreeInRowResult([Position(0, 0)], TileColor.RED, "horizontal")
    
    def test_invalid_direction(self):
        """Test validation of direction"""
        positions = [Position(0, 0), Position(0, 1), Position(0, 2)]
        with pytest.raises(ValueError, match="Invalid direction"):
            ThreeInRowResult(positions, TileColor.RED, "invalid")


class TestGameEvent:
    def test_click_event(self):
        """Test click event creation"""
        event = GameEvent("click", Position(1, 1))
        assert event.event_type == "click"
        assert event.position == Position(1, 1)
        assert event.key is None
    
    def test_key_event(self):
        """Test key event creation"""
        event = GameEvent("key", key="space")
        assert event.event_type == "key"
        assert event.key == "space"
        assert event.position is None
    
    def test_quit_event(self):
        """Test quit event creation"""
        event = GameEvent("quit")
        assert event.event_type == "quit"
        assert event.position is None
        assert event.key is None
    
    def test_invalid_event_type(self):
        """Test validation of event type"""
        with pytest.raises(ValueError, match="Invalid event type"):
            GameEvent("invalid")
    
    def test_click_without_position(self):
        """Test click event validation"""
        with pytest.raises(ValueError, match="Click events must have a position"):
            GameEvent("click")
    
    def test_key_without_key(self):
        """Test key event validation"""
        with pytest.raises(ValueError, match="Key events must have a key"):
            GameEvent("key")