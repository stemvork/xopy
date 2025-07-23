"""
Tests for Game class move validation and execution
"""

import pytest
from xoxo_squared.models import Game, Position, Move, TileColor, TileShape, GamePhase


class TestGameMoves:
    def test_first_move_validation(self):
        """Test validation of first moves"""
        game = Game()
        
        # Valid first move - placement only
        move = Move(None, None, Position(1, 1))
        result = game.make_move(move)
        assert result.success
        assert game.get_game_state().move_count == 1
        
        # Invalid first move - with flip
        game.start_game()
        move = Move(Position(0, 0), Position(0, 1), Position(1, 1))
        result = game.make_move(move)
        assert not result.success
        assert "First move must be placement only" in result.message
    
    def test_regular_move_validation(self):
        """Test validation of regular moves after first two moves"""
        game = Game()
        
        # Set up initial state with two tiles placed
        game.make_phase_move(Position(1, 1))  # Player 1 first move
        game.make_phase_move(Position(2, 2))  # Player 2 first move
        
        # Now Player 1 should make a regular move (flip-move-place)
        # Invalid: no flip position
        move = Move(None, None, Position(0, 0))
        result = game.make_move(move)
        assert not result.success
        assert "Must flip a tile" in result.message
        
        # Invalid: flip empty position
        move = Move(Position(0, 0), Position(0, 1), Position(3, 3))
        result = game.make_move(move)
        assert not result.success
        assert "Cannot flip empty position" in result.message
        
        # Invalid: tile cannot be moved (surrounded)
        board = game.get_board()
        player = game.get_current_player()
        # Surround the tile at (1,1)
        board.place_tile(Position(0, 1), player.use_tile(TileColor.GREEN))
        board.place_tile(Position(1, 0), player.use_tile(TileColor.GREEN))
        board.place_tile(Position(1, 2), player.use_tile(TileColor.GREEN))
        board.place_tile(Position(2, 1), player.use_tile(TileColor.GREEN))
        
        move = Move(Position(1, 1), Position(0, 1), Position(3, 3))
        result = game.make_move(move)
        assert not result.success
        assert "cannot be moved" in result.message.lower()
    
    def test_move_destination_validation(self):
        """Test validation of move destinations"""
        game = Game()
        
        # Set up initial state
        game.make_phase_move(Position(1, 1))  # Player 1
        game.make_phase_move(Position(2, 2))  # Player 2
        
        # Invalid: non-orthogonal move (should fail at Move creation)
        with pytest.raises(ValueError, match="orthogonal"):
            Move(Position(1, 1), Position(2, 2), Position(3, 3))
        
        # Invalid: move to occupied position (orthogonal but occupied)
        move = Move(Position(1, 1), Position(2, 1), Position(3, 3))  # Down from (1,1) to (2,1)
        # First place a tile at (2,1) to make it occupied
        board = game.get_board()
        board.place_tile(Position(2, 1), game.get_current_player().use_tile(TileColor.GREEN))
        
        result = game.make_move(move)
        assert not result.success
        assert "Invalid move destination" in result.message
        
        # Valid orthogonal move to empty position
        move = Move(Position(1, 1), Position(0, 1), Position(3, 3))
        result = game.make_move(move)
        assert result.success
    
    def test_placement_position_validation(self):
        """Test validation of tile placement positions"""
        game = Game()
        
        # Set up initial state
        game.make_phase_move(Position(1, 1))  # Player 1
        game.make_phase_move(Position(2, 2))  # Player 2
        
        # Invalid: place on occupied position
        move = Move(Position(1, 1), Position(0, 1), Position(2, 2))
        result = game.make_move(move)
        assert not result.success
        assert "occupied position" in result.message.lower()
        
        # Valid: place on empty position
        move = Move(Position(1, 1), Position(0, 1), Position(3, 3))
        result = game.make_move(move)
        assert result.success
    
    def test_move_execution_sequence(self):
        """Test that moves are executed in correct sequence: flip, move, place"""
        game = Game()
        
        # Set up initial state
        game.make_phase_move(Position(1, 1))  # Player 1 - RED tile
        game.make_phase_move(Position(2, 2))  # Player 2 - RED tile
        
        # Get initial tile state
        board = game.get_board()
        original_tile = board.get_tile(Position(1, 1))
        original_color = original_tile.get_current_color()
        
        # Execute move: flip (1,1), move to (0,1), place at (3,3)
        move = Move(Position(1, 1), Position(0, 1), Position(3, 3))
        result = game.make_move(move)
        assert result.success
        
        # Verify flip occurred
        moved_tile = board.get_tile(Position(0, 1))
        assert moved_tile is not None
        assert moved_tile.get_current_color() != original_color  # Should be flipped
        
        # Verify original position is empty
        assert board.get_tile(Position(1, 1)) is None
        
        # Verify new tile was placed
        new_tile = board.get_tile(Position(3, 3))
        assert new_tile is not None
        assert new_tile.get_shape() == game.get_other_player().get_shape()  # Previous player's shape
    
    def test_move_with_no_tiles_remaining(self):
        """Test move execution when player has no tiles remaining"""
        game = Game()
        
        # Set up initial state
        game.make_phase_move(Position(1, 1))  # Player 1
        game.make_phase_move(Position(2, 2))  # Player 2
        
        # Exhaust current player's tiles
        current_player = game.get_current_player()
        while current_player.can_place_tile():
            current_player.use_tile(TileColor.RED)
        
        # Move should still work (flip and move), but no new tile placed
        board = game.get_board()
        tiles_before = len(board.get_all_tiles())
        
        move = Move(Position(1, 1), Position(0, 1), Position(3, 3))
        result = game.make_move(move)
        assert result.success
        
        # Should have same number of tiles (no new tile placed)
        tiles_after = len(board.get_all_tiles())
        assert tiles_after == tiles_before
        
        # Position (3,3) should still be empty
        assert board.get_tile(Position(3, 3)) is None
    
    def test_move_state_preservation_on_failure(self):
        """Test that game state is preserved when move fails"""
        game = Game()
        
        # Set up initial state
        game.make_phase_move(Position(1, 1))
        game.make_phase_move(Position(2, 2))
        
        # Capture initial state
        initial_move_count = game.get_game_state().move_count
        initial_player = game.get_current_player()
        initial_phase = game.get_game_state().phase
        board = game.get_board()
        initial_tiles = board.get_all_tiles().copy()
        
        # Attempt invalid move
        move = Move(Position(0, 0), Position(0, 1), Position(3, 3))  # Flip empty position
        result = game.make_move(move)
        assert not result.success
        
        # Verify state is unchanged
        assert game.get_game_state().move_count == initial_move_count
        assert game.get_current_player() == initial_player
        assert game.get_game_state().phase == initial_phase
        
        # Verify board state is unchanged
        current_tiles = board.get_all_tiles()
        assert len(current_tiles) == len(initial_tiles)
        for (pos, tile), (init_pos, init_tile) in zip(current_tiles, initial_tiles):
            assert pos == init_pos
            assert tile.get_current_color() == init_tile.get_current_color()
    
    def test_orthogonal_movement_enforcement(self):
        """Test that only orthogonal movements are allowed"""
        game = Game()
        
        # Set up initial state
        game.make_phase_move(Position(1, 1))
        game.make_phase_move(Position(2, 2))
        
        # Test all invalid diagonal moves - should fail at Move creation
        diagonal_moves = [
            Position(0, 0),  # Up-left
            Position(0, 2),  # Up-right
            Position(2, 0),  # Down-left
            Position(2, 2),  # Down-right
        ]
        
        for dest in diagonal_moves:
            with pytest.raises(ValueError, match="orthogonal"):
                Move(Position(1, 1), dest, Position(3, 3))
        
        # Test valid orthogonal moves
        valid_moves = [
            Position(0, 1),  # Up
            Position(1, 0),  # Left
            Position(1, 2),  # Right
            Position(2, 1),  # Down
        ]
        
        for dest in valid_moves:
            game.start_game()  # Reset for each test
            game.make_phase_move(Position(1, 1))
            game.make_phase_move(Position(2, 2))
            
            move = Move(Position(1, 1), dest, Position(3, 3))
            result = game.make_move(move)
            assert result.success, f"Move to {dest} should be valid"
    
    def test_move_validation_edge_cases(self):
        """Test edge cases in move validation"""
        game = Game()
        
        # Set up initial state
        game.make_phase_move(Position(1, 1))
        game.make_phase_move(Position(2, 2))
        
        # Test move where destination equals placement position
        move = Move(Position(1, 1), Position(0, 1), Position(0, 1))
        result = game.make_move(move)
        assert result.success  # This should be allowed - move tile and place new one in same spot
        
        # Verify the tile at (0,1) is the new tile, not the moved one
        board = game.get_board()
        tile_at_dest = board.get_tile(Position(0, 1))
        assert tile_at_dest is not None
        # The new tile should belong to the player who just moved
        expected_shape = game.get_other_player().get_shape()  # Previous player
        assert tile_at_dest.get_shape() == expected_shape
    
    def test_complete_move_vs_phase_moves(self):
        """Test that complete moves and phase moves produce same result"""
        # Set up two identical games
        game1 = Game()
        game2 = Game()
        
        # Both games: initial setup
        game1.make_phase_move(Position(1, 1))
        game1.make_phase_move(Position(2, 2))
        
        game2.make_phase_move(Position(1, 1))
        game2.make_phase_move(Position(2, 2))
        
        # Game 1: use complete move
        move = Move(Position(1, 1), Position(0, 1), Position(3, 3))
        result1 = game1.make_move(move)
        assert result1.success
        
        # Game 2: use phase moves
        result2a = game2.make_phase_move(Position(1, 1))  # Flip selection
        assert result2a.success
        result2b = game2.make_phase_move(Position(0, 1))  # Move selection
        assert result2b.success
        result2c = game2.make_phase_move(Position(3, 3))  # Tile placement
        assert result2c.success
        
        # Both games should have identical final state
        state1 = game1.get_game_state()
        state2 = game2.get_game_state()
        
        assert state1.move_count == state2.move_count
        assert state1.current_player.name == state2.current_player.name
        assert state1.phase == state2.phase
        
        # Board states should be identical
        board1 = game1.get_board()
        board2 = game2.get_board()
        
        tiles1 = board1.get_all_tiles()
        tiles2 = board2.get_all_tiles()
        
        assert len(tiles1) == len(tiles2)
        for (pos1, tile1), (pos2, tile2) in zip(sorted(tiles1, key=lambda x: (x[0].row, x[0].col)), 
                                                 sorted(tiles2, key=lambda x: (x[0].row, x[0].col))):
            assert pos1.row == pos2.row and pos1.col == pos2.col
            assert tile1.get_current_color() == tile2.get_current_color()
            assert tile1.get_shape() == tile2.get_shape()
    
    def test_move_count_tracking(self):
        """Test that move count is tracked correctly"""
        game = Game()
        
        assert game.get_game_state().move_count == 0
        
        # First move
        game.make_phase_move(Position(1, 1))
        assert game.get_game_state().move_count == 1
        
        # Second move
        game.make_phase_move(Position(2, 2))
        assert game.get_game_state().move_count == 2
        
        # Third move (complete flip-move-place)
        move = Move(Position(1, 1), Position(0, 1), Position(3, 3))
        game.make_move(move)
        assert game.get_game_state().move_count == 3
        
        # Failed move should not increment count
        invalid_move = Move(Position(0, 0), Position(0, 1), Position(1, 0))
        result = game.make_move(invalid_move)
        assert not result.success
        assert game.get_game_state().move_count == 3  # Unchanged
    
    def test_turn_switching_after_moves(self):
        """Test that turns switch correctly after successful moves"""
        game = Game()
        
        # Track player sequence
        players = []
        
        # First move - Player 1
        players.append(game.get_current_player().name)
        game.make_phase_move(Position(1, 1))
        
        # Second move - Player 2
        players.append(game.get_current_player().name)
        game.make_phase_move(Position(2, 2))
        
        # Third move - Player 1
        players.append(game.get_current_player().name)
        move = Move(Position(1, 1), Position(0, 1), Position(3, 3))
        game.make_move(move)
        
        # Fourth move - Player 2
        players.append(game.get_current_player().name)
        
        # Verify alternating pattern
        assert players == ["Player 1", "Player 2", "Player 1", "Player 2"]