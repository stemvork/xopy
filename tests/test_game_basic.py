"""
Tests for Game class basic functionality
"""

import pytest
from xoxo_squared.models import Game, Position, Move, TileColor, TileShape, GamePhase


class TestGameBasic:
    def test_game_initialization(self):
        """Test game initializes correctly"""
        game = Game()
        
        assert not game.is_game_over()
        assert game.get_winner() is None
        assert game.get_current_player().name == "Player 1"
        assert game.get_current_player().get_shape() == TileShape.HEXAGON
        
        other_player = game.get_other_player()
        assert other_player.name == "Player 2"
        assert other_player.get_shape() == TileShape.STAR
        
        game_state = game.get_game_state()
        assert game_state.move_count == 0
        assert game_state.phase == GamePhase.TILE_PLACEMENT
        assert game_state.winner is None
    
    def test_start_game_resets_state(self):
        """Test that start_game resets all game state"""
        game = Game()
        
        # Make a move to change state
        result = game.make_phase_move(Position(0, 0))
        assert result.success
        assert game.get_game_state().move_count == 1
        
        # Start new game
        game.start_game()
        
        # Verify reset
        assert not game.is_game_over()
        assert game.get_winner() is None
        assert game.get_current_player().name == "Player 1"
        assert game.get_game_state().move_count == 0
        assert game.get_game_state().phase == GamePhase.TILE_PLACEMENT
    
    def test_first_move_placement_only(self):
        """Test that first move is placement only"""
        game = Game()
        
        # First move should be successful
        result = game.make_phase_move(Position(1, 1))
        assert result.success
        assert "First move completed" in result.message
        
        # Game state should update
        game_state = game.get_game_state()
        assert game_state.move_count == 1
        assert game_state.current_player.name == "Player 2"  # Should switch
        assert game_state.phase == GamePhase.TILE_PLACEMENT  # Player 2's first move
        
        # Board should have the tile
        board = game.get_board()
        tile = board.get_tile(Position(1, 1))
        assert tile is not None
        assert tile.get_shape() == TileShape.HEXAGON
        assert tile.get_current_color() == TileColor.RED
    
    def test_first_move_invalid_position(self):
        """Test first move on invalid position"""
        game = Game()
        
        # Place a tile first
        result = game.make_phase_move(Position(0, 0))
        assert result.success
        
        # Now it's Player 2's turn, but let's manually place a tile to test occupied position
        board = game.get_board()
        current_player = game.get_current_player()
        board.place_tile(Position(1, 1), current_player.use_tile(TileColor.RED))
        
        # Try to place on occupied position
        result = game.make_phase_move(Position(1, 1))
        assert not result.success
        assert "occupied" in result.message.lower() or "empty position" in result.message.lower()
    
    def test_complete_move_validation(self):
        """Test complete move validation"""
        game = Game()
        
        # First move with flip should fail
        move = Move(Position(0, 0), Position(0, 1), Position(1, 1))
        result = game.make_move(move)
        assert not result.success
        assert "First move must be placement only" in result.message
        
        # Valid first move
        move = Move(None, None, Position(1, 1))
        result = game.make_move(move)
        assert result.success
    
    def test_turn_switching(self):
        """Test that turns switch correctly"""
        game = Game()
        
        # Player 1 makes first move
        assert game.get_current_player().name == "Player 1"
        result = game.make_phase_move(Position(0, 0))
        assert result.success
        
        # Should switch to Player 2
        assert game.get_current_player().name == "Player 2"
        
        # Player 2 should be in tile placement phase (their first move)
        game_state = game.get_game_state()
        assert game_state.phase == GamePhase.TILE_PLACEMENT
    
    def test_valid_positions_for_phases(self):
        """Test getting valid positions for different phases"""
        game = Game()
        
        # Initial phase - should return all empty positions
        valid_positions = game.get_valid_positions_for_current_phase()
        assert len(valid_positions) == 16  # 4x4 board, all empty
        
        # Make first move
        game.make_phase_move(Position(1, 1))
        
        # Now in tile placement phase for Player 2 - should return empty positions
        valid_positions = game.get_valid_positions_for_current_phase()
        assert Position(1, 1) not in valid_positions  # The tile we just placed (occupied)
        assert Position(2, 2) in valid_positions  # Should be empty
        
        # Make Player 2's first move to get to flip selection phase
        game.make_phase_move(Position(2, 2))
        
        # Now should be in flip selection phase - should return positions with movable tiles
        valid_positions = game.get_valid_positions_for_current_phase()
        assert Position(1, 1) in valid_positions  # Player 1's tile
        assert Position(2, 2) in valid_positions  # Player 2's tile
        
        # Select tile for flipping
        game.make_phase_move(Position(1, 1))
        
        # Now in move selection phase - should return valid move destinations
        valid_positions = game.get_valid_positions_for_current_phase()
        expected_moves = [Position(0, 1), Position(1, 0), Position(1, 2), Position(2, 1)]
        for pos in expected_moves:
            assert pos in valid_positions
    
    def test_game_over_prevents_moves(self):
        """Test that moves are prevented when game is over"""
        game = Game()
        
        # Manually set game over
        game._game_over = True
        game._phase = GamePhase.GAME_OVER
        
        result = game.make_phase_move(Position(0, 0))
        assert not result.success
        assert "already over" in result.message.lower()
        
        move = Move(None, None, Position(0, 0))
        result = game.make_move(move)
        assert not result.success
        assert "already over" in result.message.lower()
    
    def test_phase_move_sequence(self):
        """Test complete phase move sequence"""
        game = Game()
        
        # First move - Player 1
        result = game.make_phase_move(Position(1, 1))
        assert result.success
        assert game.get_game_state().phase == GamePhase.TILE_PLACEMENT  # Player 2's first move
        
        # Second move - Player 2's first move
        result = game.make_phase_move(Position(2, 2))
        assert result.success
        assert game.get_game_state().phase == GamePhase.FLIP_SELECTION  # Now regular moves start
        
        # Now Player 1 should flip a tile
        result = game.make_phase_move(Position(1, 1))
        assert result.success
        assert game.get_game_state().phase == GamePhase.MOVE_SELECTION
        
        # Move the tile
        result = game.make_phase_move(Position(0, 1))
        assert result.success
        assert game.get_game_state().phase == GamePhase.TILE_PLACEMENT
        
        # Place new tile
        result = game.make_phase_move(Position(3, 3))
        assert result.success
        
        # Should switch back to other player
        assert game.get_current_player().name == "Player 2"
    
    def test_invalid_flip_selection(self):
        """Test invalid flip selections"""
        game = Game()
        
        # Make first moves for both players
        game.make_phase_move(Position(1, 1))  # Player 1
        game.make_phase_move(Position(2, 2))  # Player 2
        
        # Player 1 tries to flip empty position
        result = game.make_phase_move(Position(0, 0))
        assert not result.success
        assert "empty position" in result.message.lower()
        
        # Fill board around a tile to make it unmovable
        board = game.get_board()
        player = game.get_current_player()
        
        # Place tiles around position (1,1) to block movement
        board.place_tile(Position(0, 1), player.use_tile(TileColor.GREEN))
        board.place_tile(Position(1, 0), player.use_tile(TileColor.GREEN))
        board.place_tile(Position(1, 2), player.use_tile(TileColor.GREEN))
        board.place_tile(Position(2, 1), player.use_tile(TileColor.GREEN))
        
        # Try to flip the blocked tile
        result = game.make_phase_move(Position(1, 1))
        assert not result.success
        assert "cannot be moved" in result.message.lower()
    
    def test_invalid_move_selection(self):
        """Test invalid move selections"""
        game = Game()
        
        # Set up for move selection phase
        game.make_phase_move(Position(1, 1))  # Player 1 first move
        game.make_phase_move(Position(2, 2))  # Player 2 first move
        game.make_phase_move(Position(1, 1))  # Player 1 selects tile to flip
        
        # Try invalid move destination
        result = game.make_phase_move(Position(3, 3))  # Too far
        assert not result.success
        assert "Invalid move destination" in result.message
        
        # Try diagonal move
        result = game.make_phase_move(Position(2, 2))  # Diagonal, but occupied
        assert not result.success
        assert "Invalid move destination" in result.message
    
    def test_board_access(self):
        """Test that game provides access to board"""
        game = Game()
        board = game.get_board()
        
        assert board is not None
        assert board.size == 4
        assert not board.is_full()
        
        # Make a move and verify board state
        game.make_phase_move(Position(1, 1))
        tile = board.get_tile(Position(1, 1))
        assert tile is not None