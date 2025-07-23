"""
Tests for Board three-in-a-row detection
"""

import pytest
from xoxo_squared.models import Board, Position, Player, TileShape, TileColor, ThreeInRowResult


class TestBoardThreeInRow:
    def test_horizontal_three_in_row(self):
        """Test detection of horizontal three-in-a-row"""
        board = Board()
        player = Player("Alice", TileShape.HEXAGON)
        
        # Create horizontal three-in-a-row in first row
        positions = [Position(0, 0), Position(0, 1), Position(0, 2)]
        for pos in positions:
            board.place_tile(pos, player.use_tile(TileColor.RED))
        
        results = board.check_three_in_row()
        
        assert len(results) == 1
        result = results[0]
        assert result.color == TileColor.RED
        assert result.direction == "horizontal"
        assert len(result.positions) == 3
        for pos in positions:
            assert pos in result.positions
    
    def test_vertical_three_in_row(self):
        """Test detection of vertical three-in-a-row"""
        board = Board()
        player = Player("Bob", TileShape.STAR)
        
        # Create vertical three-in-a-row in first column
        positions = [Position(0, 0), Position(1, 0), Position(2, 0)]
        for pos in positions:
            board.place_tile(pos, player.use_tile(TileColor.GREEN))
        
        results = board.check_three_in_row()
        
        assert len(results) == 1
        result = results[0]
        assert result.color == TileColor.GREEN
        assert result.direction == "vertical"
        assert len(result.positions) == 3
        for pos in positions:
            assert pos in result.positions
    
    def test_diagonal_three_in_row_top_left_to_bottom_right(self):
        """Test detection of diagonal three-in-a-row (top-left to bottom-right)"""
        board = Board()
        player = Player("Charlie", TileShape.HEXAGON)
        
        # Create diagonal three-in-a-row
        positions = [Position(0, 0), Position(1, 1), Position(2, 2)]
        for pos in positions:
            board.place_tile(pos, player.use_tile(TileColor.RED))
        
        results = board.check_three_in_row()
        
        assert len(results) == 1
        result = results[0]
        assert result.color == TileColor.RED
        assert result.direction == "diagonal"
        assert len(result.positions) == 3
        for pos in positions:
            assert pos in result.positions
    
    def test_diagonal_three_in_row_top_right_to_bottom_left(self):
        """Test detection of diagonal three-in-a-row (top-right to bottom-left)"""
        board = Board()
        player = Player("Diana", TileShape.STAR)
        
        # Create diagonal three-in-a-row
        positions = [Position(0, 2), Position(1, 1), Position(2, 0)]
        for pos in positions:
            board.place_tile(pos, player.use_tile(TileColor.GREEN))
        
        results = board.check_three_in_row()
        
        assert len(results) == 1
        result = results[0]
        assert result.color == TileColor.GREEN
        assert result.direction == "diagonal"
        assert len(result.positions) == 3
        for pos in positions:
            assert pos in result.positions
    
    def test_multiple_three_in_row(self):
        """Test detection of multiple three-in-a-row formations"""
        board = Board()
        player1 = Player("Eve", TileShape.HEXAGON)
        player2 = Player("Frank", TileShape.STAR)
        
        # Create horizontal three-in-a-row
        horizontal_positions = [Position(0, 0), Position(0, 1), Position(0, 2)]
        for pos in horizontal_positions:
            board.place_tile(pos, player1.use_tile(TileColor.RED))
        
        # Create vertical three-in-a-row
        vertical_positions = [Position(1, 3), Position(2, 3), Position(3, 3)]
        for pos in vertical_positions:
            board.place_tile(pos, player2.use_tile(TileColor.GREEN))
        
        results = board.check_three_in_row()
        
        assert len(results) == 2
        
        # Check that we have both horizontal and vertical results
        directions = [result.direction for result in results]
        assert "horizontal" in directions
        assert "vertical" in directions
        
        # Check colors
        colors = [result.color for result in results]
        assert TileColor.RED in colors
        assert TileColor.GREEN in colors
    
    def test_no_three_in_row_with_mixed_colors(self):
        """Test that mixed colors don't create three-in-a-row"""
        board = Board()
        player = Player("Grace", TileShape.HEXAGON)
        
        # Place tiles with different colors in a row
        board.place_tile(Position(0, 0), player.use_tile(TileColor.RED))
        board.place_tile(Position(0, 1), player.use_tile(TileColor.GREEN))
        board.place_tile(Position(0, 2), player.use_tile(TileColor.RED))
        
        results = board.check_three_in_row()
        
        assert len(results) == 0
    
    def test_no_three_in_row_with_gaps(self):
        """Test that gaps prevent three-in-a-row detection"""
        board = Board()
        player = Player("Henry", TileShape.STAR)
        
        # Place tiles with a gap
        board.place_tile(Position(0, 0), player.use_tile(TileColor.RED))
        # Skip Position(0, 1) - leave empty
        board.place_tile(Position(0, 2), player.use_tile(TileColor.RED))
        board.place_tile(Position(0, 3), player.use_tile(TileColor.RED))
        
        results = board.check_three_in_row()
        
        assert len(results) == 0
    
    def test_three_in_row_color_based_not_player_based(self):
        """Test that three-in-a-row is based on color, not player"""
        board = Board()
        player1 = Player("Iris", TileShape.HEXAGON)
        player2 = Player("Jack", TileShape.STAR)
        
        # Different players but same color
        board.place_tile(Position(0, 0), player1.use_tile(TileColor.RED))
        board.place_tile(Position(0, 1), player2.use_tile(TileColor.RED))
        board.place_tile(Position(0, 2), player1.use_tile(TileColor.RED))
        
        results = board.check_three_in_row()
        
        assert len(results) == 1
        result = results[0]
        assert result.color == TileColor.RED
        assert result.direction == "horizontal"
    
    def test_flipped_tiles_affect_three_in_row(self):
        """Test that flipped tiles affect three-in-a-row detection"""
        board = Board()
        player = Player("Kate", TileShape.HEXAGON)
        
        # Place tiles that would form three-in-a-row if all same color
        tile1 = player.use_tile(TileColor.RED)
        tile2 = player.use_tile(TileColor.GREEN)  # Different color initially
        tile3 = player.use_tile(TileColor.RED)
        
        board.place_tile(Position(0, 0), tile1)
        board.place_tile(Position(0, 1), tile2)
        board.place_tile(Position(0, 2), tile3)
        
        # Should not have three-in-a-row initially
        results = board.check_three_in_row()
        assert len(results) == 0
        
        # Flip the middle tile to match
        tile2.flip()  # Now RED
        
        # Should now have three-in-a-row
        results = board.check_three_in_row()
        assert len(results) == 1
        assert results[0].color == TileColor.RED
    
    def test_all_possible_horizontal_positions(self):
        """Test three-in-a-row detection in all possible horizontal positions"""
        board = Board()
        player = Player("Liam", TileShape.STAR)
        
        # Test each possible horizontal three-in-a-row in row 1
        # Positions: (1,0)-(1,1)-(1,2) and (1,1)-(1,2)-(1,3)
        
        # First horizontal three-in-a-row
        positions1 = [Position(1, 0), Position(1, 1), Position(1, 2)]
        for pos in positions1:
            board.place_tile(pos, player.use_tile(TileColor.GREEN))
        
        results = board.check_three_in_row()
        assert len(results) == 1
        
        # Add one more tile to create overlapping three-in-a-row
        board.place_tile(Position(1, 3), player.use_tile(TileColor.GREEN))
        
        results = board.check_three_in_row()
        # Should now have 2 overlapping horizontal three-in-a-row formations
        assert len(results) == 2
        assert all(result.direction == "horizontal" for result in results)
        assert all(result.color == TileColor.GREEN for result in results)
    
    def test_empty_board_no_three_in_row(self):
        """Test that empty board has no three-in-a-row"""
        board = Board()
        
        results = board.check_three_in_row()
        
        assert len(results) == 0
    
    def test_board_with_less_than_three_tiles(self):
        """Test board with insufficient tiles for three-in-a-row"""
        board = Board()
        player = Player("Maya", TileShape.HEXAGON)
        
        # Place only 2 tiles
        board.place_tile(Position(0, 0), player.use_tile(TileColor.RED))
        board.place_tile(Position(0, 1), player.use_tile(TileColor.RED))
        
        results = board.check_three_in_row()
        
        assert len(results) == 0