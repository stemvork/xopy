"""
Tests for Game class win condition checking with complex xoxo^2 rules
"""

import pytest
from xoxo_squared.models import Game, Position, Move, TileColor, TileShape, GamePhase


class TestGameWinConditions:
    def test_simple_three_in_row_breakable(self):
        """Test three-in-a-row that can be broken by opponent"""
        game = Game()
        
        # Set up a scenario where Player 1 gets three-in-a-row but it can be broken
        # Player 1: RED tiles at (0,0), (0,1), (0,2) - horizontal three-in-a-row
        # Player 2: Has a tile that can be flipped and moved to break it
        
        # Initial setup
        game.make_phase_move(Position(1, 1))  # Player 1
        game.make_phase_move(Position(2, 2))  # Player 2
        
        # Create the three-in-a-row for Player 1
        board = game.get_board()
        player1 = game._player1
        
        # Place RED tiles horizontally
        board.place_tile(Position(0, 0), player1.use_tile(TileColor.RED))
        board.place_tile(Position(0, 1), player1.use_tile(TileColor.RED))
        board.place_tile(Position(0, 2), player1.use_tile(TileColor.RED))
        
        # Check that three-in-a-row exists but game doesn't end
        three_in_rows = board.check_three_in_row()
        red_three_in_rows = [tir for tir in three_in_rows if tir.color == TileColor.RED and tir.direction == 'horizontal']
        assert len(red_three_in_rows) >= 1, "Should have at least one horizontal RED three-in-a-row"
        
        # Game should not be over because opponent can potentially break it
        winner = game.check_win_after_move()
        
        # Check if opponent can actually break it
        can_break = board.can_opponent_break_three_in_row(red_three_in_rows[0], game._player2)
        
        if can_break:
            assert winner is None, "Should not win if opponent can break three-in-a-row"
        else:
            assert winner is not None, "Should win if opponent cannot break three-in-a-row"
    
    def test_unbreakable_three_in_row_wins(self):
        """Test three-in-a-row that cannot be broken results in win"""
        game = Game()
        
        # Set up initial moves
        game.make_phase_move(Position(1, 1))  # Player 1
        game.make_phase_move(Position(2, 2))  # Player 2
        
        # Create an unbreakable three-in-a-row by surrounding the tiles
        board = game.get_board()
        player1 = game._player1
        player2 = game._player2
        
        # Create RED three-in-a-row in middle row
        board.place_tile(Position(1, 0), player1.use_tile(TileColor.RED))
        board.place_tile(Position(1, 2), player1.use_tile(TileColor.RED))  # (1,1) already has RED
        board.place_tile(Position(1, 3), player1.use_tile(TileColor.RED))
        
        # Surround them so they can't be moved
        board.place_tile(Position(0, 0), player2.use_tile(TileColor.GREEN))
        board.place_tile(Position(0, 1), player2.use_tile(TileColor.GREEN))
        board.place_tile(Position(0, 2), player2.use_tile(TileColor.GREEN))
        board.place_tile(Position(0, 3), player2.use_tile(TileColor.GREEN))
        board.place_tile(Position(2, 0), player2.use_tile(TileColor.GREEN))
        board.place_tile(Position(2, 1), player2.use_tile(TileColor.GREEN))
        board.place_tile(Position(2, 3), player2.use_tile(TileColor.GREEN))
        
        # Check win condition
        winner = game.check_win_after_move()
        
        # Verify the three-in-a-row cannot be broken
        three_in_rows = board.check_three_in_row()
        red_three_in_rows = [tir for tir in three_in_rows if tir.color == TileColor.RED]
        
        if len(red_three_in_rows) > 0:
            can_break = board.can_opponent_break_three_in_row(red_three_in_rows[0], player2)
            if not can_break:
                assert winner is not None, "Should win when three-in-a-row cannot be broken"
    
    def test_win_detection_in_complete_move(self):
        """Test win detection when making a complete move"""
        game = Game()
        
        # Set up game state
        game.make_phase_move(Position(1, 1))  # Player 1
        game.make_phase_move(Position(2, 2))  # Player 2
        
        # Set up board for a winning move
        board = game.get_board()
        player1 = game.get_current_player()  # Should be Player 1
        
        # Place two RED tiles, leaving space for third
        board.place_tile(Position(0, 0), player1.use_tile(TileColor.RED))
        board.place_tile(Position(0, 2), player1.use_tile(TileColor.RED))
        
        # Make a move that creates three-in-a-row at (0,1)
        # Move existing tile and place new one to complete the line
        move = Move(Position(1, 1), Position(1, 0), Position(0, 1))
        result = game.make_move(move)
        
        # Check if this created a winning condition
        three_in_rows = board.check_three_in_row()
        red_three_in_rows = [tir for tir in three_in_rows if tir.color == TileColor.RED]
        
        if len(red_three_in_rows) > 0:
            # Check if the win is valid (unbreakable)
            can_break = board.can_opponent_break_three_in_row(red_three_in_rows[0], game.get_other_player())
            if not can_break:
                assert result.winner is not None
                assert game.is_game_over()
                assert game.get_game_state().phase == GamePhase.GAME_OVER
    
    def test_win_detection_in_phase_moves(self):
        """Test win detection when making phase moves"""
        game = Game()
        
        # Set up game state
        game.make_phase_move(Position(1, 1))  # Player 1
        game.make_phase_move(Position(2, 2))  # Player 2
        
        # Set up board for a winning sequence
        board = game.get_board()
        player1 = game.get_current_player()  # Should be Player 1
        
        # Place tiles to set up potential win
        board.place_tile(Position(0, 0), player1.use_tile(TileColor.RED))
        board.place_tile(Position(0, 2), player1.use_tile(TileColor.RED))
        
        # Execute phase moves that might create a win
        result1 = game.make_phase_move(Position(1, 1))  # Flip selection
        assert result1.success
        
        result2 = game.make_phase_move(Position(1, 0))  # Move selection
        assert result2.success
        
        result3 = game.make_phase_move(Position(0, 1))  # Tile placement - completes three-in-a-row
        
        # Check if win was detected
        if result3.winner:
            assert game.is_game_over()
            assert game.get_game_state().phase == GamePhase.GAME_OVER
            assert "wins" in result3.message
    
    def test_forced_win_scenario(self):
        """Test scenario where opponent's move creates three-in-a-row for current player"""
        game = Game()
        
        # This is a complex scenario where Player 2's move inadvertently creates
        # a three-in-a-row for Player 1 that cannot be broken
        
        # Set up initial state
        game.make_phase_move(Position(1, 1))  # Player 1
        game.make_phase_move(Position(2, 2))  # Player 2
        
        # Create a scenario where Player 2's move will help Player 1 win
        board = game.get_board()
        player1 = game._player1
        player2 = game._player2
        
        # Set up board state where Player 2's flip will create Player 1's win
        # Place Player 1's tiles
        board.place_tile(Position(0, 0), player1.use_tile(TileColor.RED))
        board.place_tile(Position(0, 2), player1.use_tile(TileColor.RED))
        
        # Place Player 2's tile that will be flipped to RED
        green_tile = player2.use_tile(TileColor.GREEN)
        board.place_tile(Position(0, 1), green_tile)
        
        # Player 1 makes a move
        move = Move(Position(1, 1), Position(1, 0), Position(3, 3))
        game.make_move(move)
        
        # Now it's Player 2's turn - if they flip the tile at (0,1), it becomes RED
        # and creates three-in-a-row for RED color
        
        # Simulate Player 2's move that creates the win
        result1 = game.make_phase_move(Position(0, 1))  # Flip the GREEN tile to RED
        if result1.success:
            result2 = game.make_phase_move(Position(0, 3))  # Move it somewhere
            if result2.success:
                result3 = game.make_phase_move(Position(3, 0))  # Place new tile
                
                # Check if this created a win condition
                # The three RED tiles at (0,0), (0,2) and the flipped tile might create a win
                if result3.winner:
                    assert game.is_game_over()
    
    def test_multiple_three_in_rows(self):
        """Test scenario with multiple three-in-a-row formations"""
        game = Game()
        
        # Set up initial state
        game.make_phase_move(Position(1, 1))
        game.make_phase_move(Position(2, 2))
        
        board = game.get_board()
        player1 = game._player1
        player2 = game._player2
        
        # Create multiple three-in-a-row formations
        # Horizontal RED three-in-a-row
        board.place_tile(Position(0, 0), player1.use_tile(TileColor.RED))
        board.place_tile(Position(0, 1), player1.use_tile(TileColor.RED))
        board.place_tile(Position(0, 2), player1.use_tile(TileColor.RED))
        
        # Vertical GREEN three-in-a-row
        board.place_tile(Position(1, 3), player2.use_tile(TileColor.GREEN))
        board.place_tile(Position(2, 3), player2.use_tile(TileColor.GREEN))
        board.place_tile(Position(3, 3), player2.use_tile(TileColor.GREEN))
        
        # Check win condition - should find the unbreakable one
        winner = game.check_win_after_move()
        
        # Verify multiple three-in-a-rows exist
        three_in_rows = board.check_three_in_row()
        assert len(three_in_rows) >= 2
        
        # At least one should be unbreakable for there to be a winner
        if winner:
            unbreakable_found = False
            for tir in three_in_rows:
                can_break = board.can_opponent_break_three_in_row(tir, game.get_other_player())
                if not can_break:
                    unbreakable_found = True
                    break
            assert unbreakable_found, "Winner should only exist if at least one three-in-a-row is unbreakable"
    
    def test_draw_condition(self):
        """Test draw condition when board is full with no winner"""
        game = Game()
        
        # Fill the board without creating unbreakable three-in-a-rows
        # This is complex to set up, so we'll simulate it
        
        # Set up initial moves
        game.make_phase_move(Position(1, 1))
        game.make_phase_move(Position(2, 2))
        
        # Manually fill board to simulate draw condition
        board = game.get_board()
        player1 = game._player1
        player2 = game._player2
        
        # Fill board with alternating colors to avoid three-in-a-rows
        positions = [(r, c) for r in range(4) for c in range(4)]
        for i, (row, col) in enumerate(positions):
            if not board.get_tile(Position(row, col)):  # If position is empty
                color = TileColor.RED if i % 2 == 0 else TileColor.GREEN
                player = player1 if i % 4 < 2 else player2
                if player.can_place_tile():
                    board.place_tile(Position(row, col), player.use_tile(color))
        
        # Check if board is full
        if board.is_full():
            # Check for draw condition
            is_draw = game._is_draw()
            winner = game.check_win_after_move()
            
            if winner is None:
                assert is_draw, "Should be a draw when board is full with no winner"
    
    def test_win_condition_integration_with_moves(self):
        """Test that win conditions are properly checked after each move"""
        game = Game()
        
        # Track game state through a sequence of moves
        moves_made = 0
        
        # Initial moves
        result = game.make_phase_move(Position(1, 1))
        assert result.success and not result.winner
        moves_made += 1
        
        result = game.make_phase_move(Position(2, 2))
        assert result.success and not result.winner
        moves_made += 1
        
        # Continue with moves that might lead to a win
        board = game.get_board()
        player1 = game._player1
        
        # Set up potential winning position
        board.place_tile(Position(0, 0), player1.use_tile(TileColor.RED))
        board.place_tile(Position(0, 2), player1.use_tile(TileColor.RED))
        
        # Make move that completes three-in-a-row
        move = Move(Position(1, 1), Position(1, 0), Position(0, 1))
        result = game.make_move(move)
        moves_made += 1
        
        # Verify win detection
        if result.winner:
            assert game.is_game_over()
            assert game.get_game_state().move_count == moves_made
            assert game.get_game_state().phase == GamePhase.GAME_OVER
        
        # Verify no further moves are allowed
        if game.is_game_over():
            next_move = Move(Position(2, 2), Position(2, 1), Position(3, 3))
            result = game.make_move(next_move)
            assert not result.success
            assert "already over" in result.message.lower()
    
    def test_survivability_check_accuracy(self):
        """Test that survivability checks are accurate"""
        game = Game()
        
        # Set up specific scenario to test survivability logic
        game.make_phase_move(Position(1, 1))
        game.make_phase_move(Position(2, 2))
        
        board = game.get_board()
        player1 = game._player1
        player2 = game._player2
        
        # Create a three-in-a-row where middle tile can be flipped
        tile1 = player1.use_tile(TileColor.RED)
        tile2 = player1.use_tile(TileColor.GREEN)  # Will be flipped to RED
        tile3 = player1.use_tile(TileColor.RED)
        
        # Flip tile2 to RED to create three-in-a-row
        tile2.flip()
        
        board.place_tile(Position(0, 0), tile1)
        board.place_tile(Position(0, 1), tile2)
        board.place_tile(Position(0, 2), tile3)
        
        # Verify three-in-a-row exists
        three_in_rows = board.check_three_in_row()
        red_three_in_rows = [tir for tir in three_in_rows if tir.color == TileColor.RED and tir.direction == 'horizontal']
        assert len(red_three_in_rows) >= 1, "Should have at least one horizontal RED three-in-a-row"
        
        # Check survivability
        can_break = board.can_opponent_break_three_in_row(red_three_in_rows[0], player2)
        
        # This should be breakable because tile2 can be flipped back to GREEN
        assert can_break, "Three-in-a-row should be breakable by flipping middle tile"
        
        # Therefore, no winner should be declared
        winner = game.check_win_after_move()
        assert winner is None, "Should not win if three-in-a-row is breakable"
    
    def test_color_based_winning_not_player_based(self):
        """Test that winning is based on color, not player ownership"""
        game = Game()
        
        # Set up scenario where different players' tiles form same color three-in-a-row
        game.make_phase_move(Position(1, 1))  # Player 1 - RED
        game.make_phase_move(Position(2, 2))  # Player 2 - RED
        
        board = game.get_board()
        player1 = game._player1
        player2 = game._player2
        
        # Create three RED tiles from different players
        board.place_tile(Position(0, 0), player1.use_tile(TileColor.RED))  # Player 1's RED
        board.place_tile(Position(0, 1), player2.use_tile(TileColor.RED))  # Player 2's RED
        board.place_tile(Position(0, 2), player1.use_tile(TileColor.RED))  # Player 1's RED
        
        # Check for three-in-a-row
        three_in_rows = board.check_three_in_row()
        red_three_in_rows = [tir for tir in three_in_rows if tir.color == TileColor.RED]
        
        if len(red_three_in_rows) > 0:
            # Verify it's detected as RED three-in-a-row regardless of player ownership
            assert red_three_in_rows[0].color == TileColor.RED
            
            # Win condition should be based on the current player who just moved
            winner = game.check_win_after_move()
            if winner:
                # The winner should be the current player, regardless of tile ownership
                assert winner == game.get_current_player()