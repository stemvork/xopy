"""
Tests for Player class
"""

import pytest
from xoxo_squared.models import Player, TileShape, TileColor, Tile


class TestPlayer:
    def test_player_creation(self):
        """Test creating a player"""
        player = Player("Alice", TileShape.HEXAGON)
        
        assert player.name == "Alice"
        assert player.get_shape() == TileShape.HEXAGON
        assert player.get_tiles_remaining() == 8
        assert player.can_place_tile() is True
    
    def test_player_creation_with_custom_tiles(self):
        """Test creating a player with custom tile count"""
        player = Player("Bob", TileShape.STAR, 5)
        
        assert player.name == "Bob"
        assert player.get_shape() == TileShape.STAR
        assert player.get_tiles_remaining() == 5
        assert player.can_place_tile() is True
    
    def test_invalid_tile_count(self):
        """Test validation of tile count"""
        with pytest.raises(ValueError, match="Tiles remaining cannot be negative"):
            Player("Invalid", TileShape.HEXAGON, -1)
    
    def test_use_tile(self):
        """Test using a tile"""
        player = Player("Alice", TileShape.HEXAGON, 3)
        
        # Use a tile
        tile = player.use_tile(TileColor.RED)
        
        # Check tile properties
        assert isinstance(tile, Tile)
        assert tile.get_shape() == TileShape.HEXAGON
        assert tile.get_current_color() == TileColor.RED
        assert tile.get_owner() == player
        
        # Check player state
        assert player.get_tiles_remaining() == 2
        assert player.can_place_tile() is True
    
    def test_use_all_tiles(self):
        """Test using all tiles"""
        player = Player("Bob", TileShape.STAR, 2)
        
        # Use first tile
        tile1 = player.use_tile(TileColor.GREEN)
        assert player.get_tiles_remaining() == 1
        assert player.can_place_tile() is True
        
        # Use second tile
        tile2 = player.use_tile(TileColor.RED)
        assert player.get_tiles_remaining() == 0
        assert player.can_place_tile() is False
        
        # Verify tiles are different objects but same owner
        assert tile1 != tile2
        assert tile1.get_owner() == player
        assert tile2.get_owner() == player
    
    def test_use_tile_when_none_remaining(self):
        """Test using a tile when none remaining"""
        player = Player("Charlie", TileShape.HEXAGON, 0)
        
        assert player.can_place_tile() is False
        
        with pytest.raises(ValueError, match="Player Charlie has no tiles remaining"):
            player.use_tile(TileColor.RED)
    
    def test_tile_creation_with_different_colors(self):
        """Test creating tiles with different initial colors"""
        player = Player("Diana", TileShape.STAR, 2)
        
        red_tile = player.use_tile(TileColor.RED)
        green_tile = player.use_tile(TileColor.GREEN)
        
        assert red_tile.get_current_color() == TileColor.RED
        assert green_tile.get_current_color() == TileColor.GREEN
        assert red_tile.get_shape() == TileShape.STAR
        assert green_tile.get_shape() == TileShape.STAR
    
    def test_player_equality(self):
        """Test player equality comparison"""
        player1 = Player("Alice", TileShape.HEXAGON, 8)
        player2 = Player("Alice", TileShape.HEXAGON, 8)
        player3 = Player("Bob", TileShape.HEXAGON, 8)
        player4 = Player("Alice", TileShape.STAR, 8)
        player5 = Player("Alice", TileShape.HEXAGON, 7)
        
        # Same players should be equal
        assert player1 == player2
        
        # Different names should not be equal
        assert player1 != player3
        
        # Different shapes should not be equal
        assert player1 != player4
        
        # Different tile counts should not be equal
        assert player1 != player5
        
        # Player should not equal non-player objects
        assert player1 != "not a player"
        assert player1 != 42
    
    def test_player_string_representation(self):
        """Test player string representation"""
        player = Player("TestPlayer", TileShape.STAR, 5)
        
        repr_str = repr(player)
        assert "TestPlayer" in repr_str
        assert "star" in repr_str
        assert "5 tiles" in repr_str
    
    def test_player_state_after_tile_usage(self):
        """Test that player state changes correctly after using tiles"""
        player = Player("Eve", TileShape.HEXAGON, 3)
        
        original_tiles = player.get_tiles_remaining()
        
        # Use a tile
        tile = player.use_tile(TileColor.RED)
        
        # Verify state change
        assert player.get_tiles_remaining() == original_tiles - 1
        
        # Verify tile is correctly associated with player
        assert tile.get_owner() == player
        assert tile.get_shape() == player.get_shape()