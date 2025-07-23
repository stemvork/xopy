"""
Tests for basic Board operations
"""

import pytest
from xoxo_squared.models import Board, Position, Tile, Player, TileShape, TileColor


class TestBoardBasic:
    def test_board_creation(self):
        """Test creating a board"""
        board = Board()
        
        assert board.size == 4
        assert board.is_full() is False
        
        # All positions should be empty
        for row in range(4):
            for col in range(4):
                pos = Position(row, col)
                assert board.is_position_empty(pos) is True
                assert board.get_tile(pos) is None
    
    def test_board_custom_size(self):
        """Test creating a board with custom size"""
        board = Board(3)
        assert board.size == 3
        
        # Test that positions within bounds work
        assert board.is_position_empty(Position(2, 2)) is True
        
        # Test that positions outside bounds don't work
        assert board.get_tile(Position(3, 0)) is None
    
    def test_invalid_board_size(self):
        """Test validation of board size"""
        with pytest.raises(ValueError, match="Board size must be positive"):
            Board(0)
        
        with pytest.raises(ValueError, match="Board size must be positive"):
            Board(-1)
    
    def test_place_tile(self):
        """Test placing tiles on the board"""
        board = Board()
        player = Player("Alice", TileShape.HEXAGON)
        tile = player.use_tile(TileColor.RED)
        pos = Position(1, 1)
        
        # Place tile
        result = board.place_tile(pos, tile)
        assert result is True
        
        # Verify tile is placed
        assert board.get_tile(pos) == tile
        assert board.is_position_empty(pos) is False
    
    def test_place_tile_on_occupied_position(self):
        """Test placing tile on already occupied position"""
        board = Board()
        player = Player("Alice", TileShape.HEXAGON)
        tile1 = player.use_tile(TileColor.RED)
        tile2 = player.use_tile(TileColor.GREEN)
        pos = Position(2, 2)
        
        # Place first tile
        assert board.place_tile(pos, tile1) is True
        
        # Try to place second tile on same position
        assert board.place_tile(pos, tile2) is False
        
        # Original tile should still be there
        assert board.get_tile(pos) == tile1
    
    def test_place_tile_invalid_position(self):
        """Test placing tile on invalid position"""
        board = Board()
        player = Player("Alice", TileShape.HEXAGON)
        tile = player.use_tile(TileColor.RED)
        
        # This should fail because Position validation will catch it first
        with pytest.raises(ValueError):
            invalid_pos = Position(4, 0)  # Out of bounds for 4x4 board
    
    def test_remove_tile(self):
        """Test removing tiles from the board"""
        board = Board()
        player = Player("Bob", TileShape.STAR)
        tile = player.use_tile(TileColor.GREEN)
        pos = Position(0, 3)
        
        # Place and then remove tile
        board.place_tile(pos, tile)
        removed_tile = board.remove_tile(pos)
        
        assert removed_tile == tile
        assert board.is_position_empty(pos) is True
        assert board.get_tile(pos) is None
    
    def test_remove_tile_from_empty_position(self):
        """Test removing tile from empty position"""
        board = Board()
        pos = Position(1, 2)
        
        removed_tile = board.remove_tile(pos)
        assert removed_tile is None
    
    def test_get_valid_moves(self):
        """Test getting valid orthogonal moves"""
        board = Board()
        
        # Test center position (should have 4 valid moves)
        center_pos = Position(1, 1)
        valid_moves = board.get_valid_moves(center_pos)
        expected_moves = [Position(0, 1), Position(2, 1), Position(1, 0), Position(1, 2)]
        
        assert len(valid_moves) == 4
        for move in expected_moves:
            assert move in valid_moves
        
        # Test corner position (should have 2 valid moves)
        corner_pos = Position(0, 0)
        valid_moves = board.get_valid_moves(corner_pos)
        expected_moves = [Position(1, 0), Position(0, 1)]
        
        assert len(valid_moves) == 2
        for move in expected_moves:
            assert move in valid_moves
    
    def test_get_valid_moves_with_obstacles(self):
        """Test getting valid moves when some positions are occupied"""
        board = Board()
        player = Player("Charlie", TileShape.HEXAGON)
        
        # Place tiles to block some moves
        center_pos = Position(1, 1)
        board.place_tile(Position(0, 1), player.use_tile(TileColor.RED))  # Block up
        board.place_tile(Position(1, 0), player.use_tile(TileColor.GREEN))  # Block left
        
        valid_moves = board.get_valid_moves(center_pos)
        expected_moves = [Position(2, 1), Position(1, 2)]  # Only down and right
        
        assert len(valid_moves) == 2
        for move in expected_moves:
            assert move in valid_moves
    
    def test_is_full(self):
        """Test checking if board is full"""
        board = Board(2)  # Use smaller board for easier testing
        player = Player("Diana", TileShape.STAR)
        
        assert board.is_full() is False
        
        # Fill the board
        for row in range(2):
            for col in range(2):
                board.place_tile(Position(row, col), player.use_tile(TileColor.RED))
        
        assert board.is_full() is True
    
    def test_get_all_tiles(self):
        """Test getting all tiles on the board"""
        board = Board()
        player1 = Player("Eve", TileShape.HEXAGON)
        player2 = Player("Frank", TileShape.STAR)
        
        # Place some tiles
        tile1 = player1.use_tile(TileColor.RED)
        tile2 = player2.use_tile(TileColor.GREEN)
        pos1 = Position(0, 0)
        pos2 = Position(3, 3)
        
        board.place_tile(pos1, tile1)
        board.place_tile(pos2, tile2)
        
        all_tiles = board.get_all_tiles()
        assert len(all_tiles) == 2
        
        # Check that both tiles are in the result
        positions = [pos for pos, tile in all_tiles]
        tiles = [tile for pos, tile in all_tiles]
        
        assert pos1 in positions
        assert pos2 in positions
        assert tile1 in tiles
        assert tile2 in tiles
    
    def test_board_string_representation(self):
        """Test board string representation"""
        board = Board(2)  # Use smaller board for easier testing
        player1 = Player("Grace", TileShape.HEXAGON)
        player2 = Player("Henry", TileShape.STAR)
        
        # Place some tiles
        board.place_tile(Position(0, 0), player1.use_tile(TileColor.RED))
        board.place_tile(Position(1, 1), player2.use_tile(TileColor.GREEN))
        
        board_str = str(board)
        
        # Should contain representations of the tiles and empty spaces
        assert "R◆" in board_str  # Red hexagon
        assert "G★" in board_str  # Green star
        assert "-" in board_str   # Empty spaces