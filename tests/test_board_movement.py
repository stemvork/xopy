"""
Tests for Board movement validation and calculation
"""

import pytest
from xoxo_squared.models import Board, Position, Player, TileShape, TileColor


class TestBoardMovement:
    def test_orthogonal_movement_only(self):
        """Test that only orthogonal movements are allowed"""
        board = Board()
        center_pos = Position(2, 2)
        
        valid_moves = board.get_valid_moves(center_pos)
        
        # Should have exactly 4 orthogonal moves
        expected_moves = [
            Position(1, 2),  # Up
            Position(3, 2),  # Down
            Position(2, 1),  # Left
            Position(2, 3),  # Right
        ]
        
        assert len(valid_moves) == 4
        for move in expected_moves:
            assert move in valid_moves
        
        # Diagonal positions should NOT be in valid moves
        diagonal_positions = [
            Position(1, 1), Position(1, 3),  # Upper diagonals
            Position(3, 1), Position(3, 3),  # Lower diagonals
        ]
        
        for diagonal_pos in diagonal_positions:
            assert diagonal_pos not in valid_moves
    
    def test_movement_blocked_by_occupied_positions(self):
        """Test that occupied positions block movement"""
        board = Board()
        player = Player("Alice", TileShape.HEXAGON)
        center_pos = Position(2, 2)
        
        # Block some directions
        up_pos = Position(1, 2)
        right_pos = Position(2, 3)
        
        board.place_tile(up_pos, player.use_tile(TileColor.RED))
        board.place_tile(right_pos, player.use_tile(TileColor.GREEN))
        
        valid_moves = board.get_valid_moves(center_pos)
        
        # Should only have down and left available
        expected_moves = [
            Position(3, 2),  # Down
            Position(2, 1),  # Left
        ]
        
        assert len(valid_moves) == 2
        for move in expected_moves:
            assert move in valid_moves
        
        # Blocked positions should not be in valid moves
        assert up_pos not in valid_moves
        assert right_pos not in valid_moves
    
    def test_edge_position_movement(self):
        """Test movement from edge positions"""
        board = Board()
        
        # Test top edge
        top_edge_pos = Position(0, 2)
        valid_moves = board.get_valid_moves(top_edge_pos)
        expected_moves = [
            Position(1, 2),  # Down
            Position(0, 1),  # Left
            Position(0, 3),  # Right
        ]
        assert len(valid_moves) == 3
        for move in expected_moves:
            assert move in valid_moves
        
        # Test left edge
        left_edge_pos = Position(2, 0)
        valid_moves = board.get_valid_moves(left_edge_pos)
        expected_moves = [
            Position(1, 0),  # Up
            Position(3, 0),  # Down
            Position(2, 1),  # Right
        ]
        assert len(valid_moves) == 3
        for move in expected_moves:
            assert move in valid_moves
    
    def test_corner_position_movement(self):
        """Test movement from corner positions"""
        board = Board()
        
        # Test all four corners
        corners_and_expected = [
            (Position(0, 0), [Position(1, 0), Position(0, 1)]),  # Top-left
            (Position(0, 3), [Position(1, 3), Position(0, 2)]),  # Top-right
            (Position(3, 0), [Position(2, 0), Position(3, 1)]),  # Bottom-left
            (Position(3, 3), [Position(2, 3), Position(3, 2)]),  # Bottom-right
        ]
        
        for corner_pos, expected_moves in corners_and_expected:
            valid_moves = board.get_valid_moves(corner_pos)
            assert len(valid_moves) == 2
            for move in expected_moves:
                assert move in valid_moves
    
    def test_no_valid_moves_when_surrounded(self):
        """Test when a position has no valid moves due to being surrounded"""
        board = Board()
        player = Player("Bob", TileShape.STAR)
        center_pos = Position(2, 2)
        
        # Surround the center position
        surrounding_positions = [
            Position(1, 2),  # Up
            Position(3, 2),  # Down
            Position(2, 1),  # Left
            Position(2, 3),  # Right
        ]
        
        for pos in surrounding_positions:
            board.place_tile(pos, player.use_tile(TileColor.RED))
        
        valid_moves = board.get_valid_moves(center_pos)
        assert len(valid_moves) == 0
    
    def test_movement_validation_with_mixed_occupancy(self):
        """Test movement validation with partially occupied board"""
        board = Board()
        player1 = Player("Charlie", TileShape.HEXAGON)
        player2 = Player("Diana", TileShape.STAR)
        
        # Create a more complex board state
        board.place_tile(Position(0, 0), player1.use_tile(TileColor.RED))
        board.place_tile(Position(0, 2), player2.use_tile(TileColor.GREEN))
        board.place_tile(Position(2, 0), player1.use_tile(TileColor.GREEN))
        board.place_tile(Position(2, 2), player2.use_tile(TileColor.RED))
        
        # Test movement from position (1, 1)
        test_pos = Position(1, 1)
        valid_moves = board.get_valid_moves(test_pos)
        
        # Should be able to move to empty adjacent positions
        expected_moves = [
            Position(0, 1),  # Up (empty)
            Position(2, 1),  # Down (empty)
            Position(1, 0),  # Left (empty)
            Position(1, 2),  # Right (empty)
        ]
        
        assert len(valid_moves) == 4
        for move in expected_moves:
            assert move in valid_moves
    
    def test_invalid_position_movement(self):
        """Test movement calculation for invalid positions"""
        board = Board()
        
        # Position outside board bounds should return empty list
        # Note: This will raise ValueError due to Position validation
        with pytest.raises(ValueError):
            Position(4, 0)  # Out of bounds
    
    def test_movement_destination_must_be_empty(self):
        """Test that movement destinations must be empty"""
        board = Board()
        player = Player("Eve", TileShape.HEXAGON)
        
        # Fill some positions
        board.place_tile(Position(1, 1), player.use_tile(TileColor.RED))
        board.place_tile(Position(1, 3), player.use_tile(TileColor.GREEN))
        
        # Test from position that has some blocked and some free moves
        test_pos = Position(1, 2)
        valid_moves = board.get_valid_moves(test_pos)
        
        # Should not include occupied positions
        assert Position(1, 1) not in valid_moves  # Occupied
        assert Position(1, 3) not in valid_moves  # Occupied
        
        # Should include empty positions
        assert Position(0, 2) in valid_moves  # Empty
        assert Position(2, 2) in valid_moves  # Empty