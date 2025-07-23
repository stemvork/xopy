"""
Tests for Tile class
"""

import pytest
from xoxo_squared.models import Tile, TileShape, TileColor


class MockPlayer:
    """Mock player for testing"""
    def __init__(self, name: str):
        self.name = name


class TestTile:
    def test_tile_creation(self):
        """Test creating a tile"""
        player = MockPlayer("Player1")
        tile = Tile(TileShape.HEXAGON, TileColor.RED, player)
        
        assert tile.get_shape() == TileShape.HEXAGON
        assert tile.get_current_color() == TileColor.RED
        assert tile.get_owner() == player
    
    def test_tile_flipping(self):
        """Test flipping tile colors"""
        player = MockPlayer("Player1")
        tile = Tile(TileShape.STAR, TileColor.RED, player)
        
        # Initial color should be red
        assert tile.get_current_color() == TileColor.RED
        
        # After flipping, should be green
        tile.flip()
        assert tile.get_current_color() == TileColor.GREEN
        
        # After flipping again, should be red
        tile.flip()
        assert tile.get_current_color() == TileColor.RED
    
    def test_tile_immutable_properties(self):
        """Test that shape and owner cannot be changed"""
        player = MockPlayer("Player1")
        tile = Tile(TileShape.HEXAGON, TileColor.GREEN, player)
        
        # Shape and owner should remain constant
        original_shape = tile.get_shape()
        original_owner = tile.get_owner()
        
        # Flip the tile multiple times
        tile.flip()
        tile.flip()
        tile.flip()
        
        # Shape and owner should still be the same
        assert tile.get_shape() == original_shape
        assert tile.get_owner() == original_owner
    
    def test_tile_equality(self):
        """Test tile equality comparison"""
        player1 = MockPlayer("Player1")
        player2 = MockPlayer("Player2")
        
        tile1 = Tile(TileShape.HEXAGON, TileColor.RED, player1)
        tile2 = Tile(TileShape.HEXAGON, TileColor.RED, player1)
        tile3 = Tile(TileShape.STAR, TileColor.RED, player1)
        tile4 = Tile(TileShape.HEXAGON, TileColor.GREEN, player1)
        tile5 = Tile(TileShape.HEXAGON, TileColor.RED, player2)
        
        # Same tiles should be equal
        assert tile1 == tile2
        
        # Different shapes should not be equal
        assert tile1 != tile3
        
        # Different colors should not be equal
        assert tile1 != tile4
        
        # Different owners should not be equal
        assert tile1 != tile5
        
        # Tile should not equal non-tile objects
        assert tile1 != "not a tile"
        assert tile1 != 42
    
    def test_tile_string_representation(self):
        """Test tile string representation"""
        player = MockPlayer("TestPlayer")
        tile = Tile(TileShape.STAR, TileColor.GREEN, player)
        
        repr_str = repr(tile)
        assert "star" in repr_str
        assert "green" in repr_str
        assert "TestPlayer" in repr_str
    
    def test_tile_color_changes_with_flip(self):
        """Test that only color changes when flipping"""
        player = MockPlayer("Player1")
        tile = Tile(TileShape.HEXAGON, TileColor.RED, player)
        
        # Create a copy for comparison
        original_shape = tile.get_shape()
        original_owner = tile.get_owner()
        
        # Flip and verify only color changed
        tile.flip()
        
        assert tile.get_shape() == original_shape
        assert tile.get_owner() == original_owner
        assert tile.get_current_color() == TileColor.GREEN