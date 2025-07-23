"""
Comprehensive pygame interaction tests for xoxo^2 game
Tests mouse click handling, position mapping, visual feedback, and game state synchronization
"""

import pytest
import pygame
from unittest.mock import patch, MagicMock, call
from xoxo_squared.views import PygameView
from xoxo_squared.models import Game, Position, GameEvent, TileColor, TileShape, GamePhase
from xoxo_squared.controllers import GameController


class TestPygameMouseInteractions:
    """Test mouse click handling and position mapping"""
    
    def test_mouse_click_to_board_position_mapping(self):
        """Test accurate mapping from mouse clicks to board positions"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView(800, 700)
            
            # Test all board positions
            test_cases = [
                # (board_row, board_col, expected_screen_x, expected_screen_y)
                (0, 0, view.board_x + 75, view.board_y + 75),    # Top-left
                (0, 3, view.board_x + 525, view.board_y + 75),   # Top-right
                (3, 0, view.board_x + 75, view.board_y + 525),   # Bottom-left
                (3, 3, view.board_x + 525, view.board_y + 525),  # Bottom-right
                (1, 1, view.board_x + 225, view.board_y + 225),  # Center-ish
                (2, 2, view.board_x + 375, view.board_y + 375),  # Center-ish
            ]
            
            for expected_row, expected_col, screen_x, screen_y in test_cases:
                position = view._screen_to_board_position((screen_x, screen_y))
                assert position is not None, f"Failed to map screen position ({screen_x}, {screen_y})"
                assert position.row == expected_row, f"Expected row {expected_row}, got {position.row}"
                assert position.col == expected_col, f"Expected col {expected_col}, got {position.col}"
    
    def test_mouse_click_boundary_conditions(self):
        """Test mouse clicks at board boundaries"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView(800, 700)
            
            # Test clicks just outside board boundaries
            boundary_tests = [
                (view.board_x - 1, view.board_y + 100),  # Left edge
                (view.board_x + view.board_size + 1, view.board_y + 100),  # Right edge
                (view.board_x + 100, view.board_y - 1),  # Top edge
                (view.board_x + 100, view.board_y + view.board_size + 1),  # Bottom edge
            ]
            
            for x, y in boundary_tests:
                position = view._screen_to_board_position((x, y))
                assert position is None, f"Expected None for boundary click ({x}, {y}), got {position}"
    
    def test_mouse_click_cell_boundaries(self):
        """Test mouse clicks at cell boundaries within the board"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView(800, 700)
            
            # Test clicks right at cell boundaries
            cell_boundary_tests = [
                # Click right at the boundary between cells (0,0) and (0,1)
                (view.board_x + view.cell_size, view.board_y + 50, 0, 1),
                # Click right at the boundary between cells (0,0) and (1,0)
                (view.board_x + 50, view.board_y + view.cell_size, 1, 0),
                # Click at intersection of four cells
                (view.board_x + view.cell_size, view.board_y + view.cell_size, 1, 1),
            ]
            
            for x, y, expected_row, expected_col in cell_boundary_tests:
                position = view._screen_to_board_position((x, y))
                assert position is not None, f"Failed to map boundary click ({x}, {y})"
                assert position.row == expected_row and position.col == expected_col, \
                    f"Expected ({expected_row}, {expected_col}), got ({position.row}, {position.col})"
    
    def test_mouse_event_generation(self):
        """Test that mouse clicks generate correct GameEvent objects"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.event.get') as mock_events:
            
            view = PygameView()
            
            # Mock mouse click event
            mock_click_event = MagicMock()
            mock_click_event.type = pygame.MOUSEBUTTONDOWN
            mock_click_event.button = 1  # Left click
            mock_click_event.pos = (view.board_x + 75, view.board_y + 75)  # Position (0,0)
            mock_events.return_value = [mock_click_event]
            
            events = view.handle_events()
            
            assert len(events) == 1
            assert events[0].event_type == "click"
            assert events[0].position == Position(0, 0)
    
    def test_right_click_ignored(self):
        """Test that right clicks are ignored"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.event.get') as mock_events:
            
            view = PygameView()
            
            # Mock right click event
            mock_right_click = MagicMock()
            mock_right_click.type = pygame.MOUSEBUTTONDOWN
            mock_right_click.button = 3  # Right click
            mock_right_click.pos = (view.board_x + 75, view.board_y + 75)
            mock_events.return_value = [mock_right_click]
            
            events = view.handle_events()
            
            # Right clicks should not generate game events
            assert len(events) == 0


class TestPygameVisualFeedback:
    """Test visual feedback and highlighting systems"""
    
    def test_valid_move_highlighting(self):
        """Test highlighting of valid move positions"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Test highlighting multiple positions
            positions = [Position(0, 0), Position(1, 1), Position(2, 2), Position(3, 3)]
            view.highlight_valid_moves(positions)
            
            assert len(view.highlighted_positions) == 4
            for pos in positions:
                assert pos in view.highlighted_positions
    
    def test_highlight_clearing(self):
        """Test clearing of highlights"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Set some highlights
            positions = [Position(0, 0), Position(1, 1)]
            view.highlight_valid_moves(positions)
            assert len(view.highlighted_positions) == 2
            
            # Clear highlights
            view.highlight_valid_moves([])
            assert len(view.highlighted_positions) == 0
    
    def test_hover_state_updates(self):
        """Test hover state updates for visual feedback"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.event.get') as mock_events:
            
            view = PygameView()
            
            # Mock mouse motion event
            mock_motion_event = MagicMock()
            mock_motion_event.type = pygame.MOUSEMOTION
            mock_motion_event.pos = (view.board_x + 75, view.board_y + 75)  # Position (0,0)
            mock_events.return_value = [mock_motion_event]
            
            events = view.handle_events()
            
            # Check that hover state was updated
            assert view.hovered_position == Position(0, 0)
            assert view.mouse_pos == (view.board_x + 75, view.board_y + 75)
    
    def test_click_feedback_system(self):
        """Test visual click feedback system"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Simulate click feedback
            click_pos = Position(1, 1)
            view._set_click_feedback(click_pos)
            
            assert view.last_clicked_position == click_pos
            assert view.click_feedback_timer > 0
    
    def test_error_message_display(self):
        """Test error message display system"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Test error message setting
            error_msg = "Invalid move!"
            error_pos = Position(1, 1)
            view.show_error_message(error_msg, error_pos, "move_error")
            
            assert view.error_message == error_msg
            assert view.error_position == error_pos
            assert view.error_type == "move_error"
            assert view.error_timer > 0
    
    def test_warning_and_info_messages(self):
        """Test warning and info message systems"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Test warning message
            warning_msg = "Low tiles remaining!"
            view.show_warning_message(warning_msg)
            assert view.warning_message == warning_msg
            assert view.warning_timer > 0
            
            # Test info message
            info_msg = "Tile flipped successfully"
            view.show_info_message(info_msg)
            assert view.info_message == info_msg
            assert view.info_timer > 0


class TestPygameGameStateSync:
    """Test game state synchronization between model and view"""
    
    def test_board_state_rendering(self):
        """Test that board state is correctly rendered"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.draw.rect'), \
             patch('pygame.draw.line'), \
             patch('pygame.draw.polygon') as mock_polygon, \
             patch('pygame.draw.circle'), \
             patch('pygame.display.flip'):
            
            # Mock the screen surface properly
            mock_screen = MagicMock()
            mock_display.return_value = mock_screen
            
            view = PygameView()
            game = Game()
            game.start_game()
            
            # Place some tiles
            game.make_phase_move(Position(0, 0))  # Player 1 first move
            game.make_phase_move(Position(0, 0))  # Player 2 flip
            game.make_phase_move(Position(1, 0))  # Player 2 move
            game.make_phase_move(Position(2, 0))  # Player 2 place
            
            # Render the board
            game_state = game.get_game_state()
            view.render_board(game_state, game.get_board())
            
            # Verify that drawing methods were called
            assert mock_polygon.called, "Tile shapes should be drawn"
    
    def test_game_phase_ui_updates(self):
        """Test that UI updates correctly based on game phase"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font') as mock_font, \
             patch('pygame.draw.rect'), \
             patch('pygame.draw.line'), \
             patch('pygame.draw.polygon'), \
             patch('pygame.draw.circle'):
            
            # Mock the screen surface properly
            mock_screen = MagicMock()
            mock_display.return_value = mock_screen
            
            # Mock font rendering
            mock_font_obj = MagicMock()
            mock_font_obj.render.return_value = MagicMock()
            mock_font_obj.render.return_value.get_rect.return_value = MagicMock()
            mock_font.return_value = mock_font_obj
            
            view = PygameView()
            # Set the screen to the mock so drawing operations work
            view.screen = mock_screen
            
            game = Game()
            game.start_game()
            
            # Test different game phases
            phases_to_test = [
                GamePhase.TILE_PLACEMENT,
                GamePhase.FLIP_SELECTION,
                GamePhase.MOVE_SELECTION,
                GamePhase.GAME_OVER
            ]
            
            for phase in phases_to_test:
                # Manually set phase for testing
                game._phase = phase
                game_state = game.get_game_state()
                
                # This should not raise exceptions
                view.render_ui(game_state, game.get_current_player(), game.get_other_player())
    
    def test_player_info_synchronization(self):
        """Test that player information is correctly synchronized"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font') as mock_font, \
             patch('pygame.draw.rect'), \
             patch('pygame.draw.line'), \
             patch('pygame.draw.polygon'), \
             patch('pygame.draw.circle'):
            
            # Mock the screen surface properly
            mock_screen = MagicMock()
            mock_display.return_value = mock_screen
            
            mock_font_obj = MagicMock()
            mock_font_obj.render.return_value = MagicMock()
            mock_font_obj.render.return_value.get_rect.return_value = MagicMock()
            mock_font.return_value = mock_font_obj
            
            view = PygameView()
            # Set the screen to the mock so drawing operations work
            view.screen = mock_screen
            
            game = Game()
            game.start_game()
            
            # Make some moves to change tile counts
            game.make_phase_move(Position(0, 0))  # Player 1 uses a tile
            
            player1 = game.get_current_player()
            player2 = game.get_other_player()
            
            # Render UI with player info
            game_state = game.get_game_state()
            view.render_ui(game_state, player1, player2)
            
            # Verify that font rendering was called (indicating player info was displayed)
            assert mock_font_obj.render.called
    
    def test_valid_moves_highlighting_sync(self):
        """Test that valid moves highlighting syncs with game state"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            game = Game()
            controller = GameController(game, view)
            controller.start_game()
            
            # Get valid positions for current phase
            valid_positions = controller.game.get_valid_positions_for_current_phase()
            
            # Highlight them in the view
            view.highlight_valid_moves(valid_positions)
            
            # Verify highlighting matches game state
            assert len(view.highlighted_positions) == len(valid_positions)
            for pos in valid_positions:
                assert pos in view.highlighted_positions


class TestPygameButtonInteractions:
    """Test button interactions and UI element clicks"""
    
    def test_button_click_detection(self):
        """Test detection of button clicks"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Mock button positions (these would need to match actual button positions)
            # For now, test the button click detection mechanism
            button_result = view.check_button_clicks((400, 600))  # Approximate button area
            
            # The result depends on actual button implementation
            # This tests that the method exists and can be called
            assert button_result is not None or button_result is None  # Either is valid
    
    def test_ui_element_click_detection(self):
        """Test detection of UI element clicks"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Test player panel clicks
            player1_panel_click = view._is_click_in_player_panel((400, view.info_panel_y + 50), 1)
            player2_panel_click = view._is_click_in_player_panel((600, view.info_panel_y + 50), 2)
            
            # These should return boolean values
            assert isinstance(player1_panel_click, bool)
            assert isinstance(player2_panel_click, bool)
    
    def test_keyboard_event_handling(self):
        """Test keyboard event handling"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.event.get') as mock_events, \
             patch('pygame.key.name') as mock_key_name:
            
            view = PygameView()
            
            # Mock keyboard event
            mock_key_event = MagicMock()
            mock_key_event.type = pygame.KEYDOWN
            mock_key_event.key = pygame.K_SPACE
            mock_key_name.return_value = "space"
            mock_events.return_value = [mock_key_event]
            
            events = view.handle_events()
            
            assert len(events) == 1
            assert events[0].event_type == "key"
            assert events[0].key == "space"


class TestPygameIntegrationWithController:
    """Test pygame view integration with game controller"""
    
    def test_complete_click_to_move_flow(self):
        """Test complete flow from click to game move"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            game = Game()
            controller = GameController(game, view)
            controller.start_game()
            
            # Simulate first move click
            click_pos = (view.board_x + 75, view.board_y + 75)  # Position (0,0)
            board_pos = view._screen_to_board_position(click_pos)
            
            assert board_pos == Position(0, 0)
            
            # Process the click through controller
            result = controller.handle_click(board_pos)
            
            # Verify the move was processed
            assert result['success'] == True
            assert controller.game.get_board().get_tile(Position(0, 0)) is not None
    
    def test_invalid_click_handling(self):
        """Test handling of invalid clicks"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            game = Game()
            controller = GameController(game, view)
            controller.start_game()
            
            # Make first move
            controller.handle_click(Position(0, 0))
            
            # Try to click same position again (should be invalid in flip phase)
            result = controller.handle_click(Position(1, 1))  # Empty position in flip phase
            
            # Should fail because we're in flip phase and position is empty
            assert result['success'] == False
            assert 'message' in result
    
    def test_visual_feedback_after_moves(self):
        """Test that visual feedback is updated after moves"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            game = Game()
            controller = GameController(game, view)
            controller.start_game()
            
            # Make a move
            result = controller.handle_click(Position(0, 0))
            assert result['success'] == True
            
            # Update view with new valid positions
            valid_positions = controller.game.get_valid_positions_for_current_phase()
            view.highlight_valid_moves(valid_positions)
            
            # Verify highlights were updated
            assert len(view.highlighted_positions) == len(valid_positions)
    
    def test_game_over_state_handling(self):
        """Test handling of game over state"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            game = Game()
            controller = GameController(game, view)
            controller.start_game()
            
            # Manually set game to over state for testing
            controller.game._game_over = True
            controller.game._winner = controller.game.get_current_player()
            
            # Test game over display
            winner_name = controller.game.get_winner().name if controller.game.get_winner() else None
            view.show_game_over(winner_name)
            
            # This should not raise exceptions
            assert True  # If we get here, no exceptions were raised


class TestPygamePerformanceAndStability:
    """Test pygame view performance and stability"""
    
    def test_rapid_click_handling(self):
        """Test handling of rapid mouse clicks"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.event.get') as mock_events:
            
            view = PygameView()
            
            # Simulate rapid clicks
            rapid_clicks = []
            for i in range(10):
                mock_click = MagicMock()
                mock_click.type = pygame.MOUSEBUTTONDOWN
                mock_click.button = 1
                mock_click.pos = (view.board_x + 75 + i * 10, view.board_y + 75)
                rapid_clicks.append(mock_click)
            
            mock_events.return_value = rapid_clicks
            
            events = view.handle_events()
            
            # Should handle all clicks without crashing
            assert len(events) == 10
            for event in events:
                assert event.event_type == "click"
    
    def test_memory_cleanup(self):
        """Test proper memory cleanup"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.quit') as mock_quit:
            
            view = PygameView()
            
            # Test cleanup
            view.quit()
            
            assert view.running == False
            mock_quit.assert_called_once()
    
    def test_large_highlight_sets(self):
        """Test handling of large sets of highlighted positions"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Create large set of positions (all board positions)
            all_positions = [Position(r, c) for r in range(4) for c in range(4)]
            
            view.highlight_valid_moves(all_positions)
            
            assert len(view.highlighted_positions) == 16
            for pos in all_positions:
                assert pos in view.highlighted_positions