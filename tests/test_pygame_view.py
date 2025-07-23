"""
Tests for PygameView class
"""

import pytest
import pygame
from unittest.mock import patch, MagicMock
from xoxo_squared.views import PygameView
from xoxo_squared.models import Game, Position, GameEvent, TileColor, TileShape


class TestPygameView:
    def test_pygame_view_initialization(self):
        """Test that PygameView initializes correctly"""
        # Mock pygame to avoid actual window creation in tests
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.time.Clock') as mock_clock, \
             patch('pygame.font.Font') as mock_font:
            
            mock_display.return_value = MagicMock()
            mock_clock.return_value = MagicMock()
            mock_font.return_value = MagicMock()
            
            view = PygameView(800, 700)
            
            assert view.width == 800
            assert view.height == 700
            assert view.board_size == 600
            assert view.cell_size == 150  # 600 / 4
            assert view.running == True
            
            # Verify pygame initialization was called
            mock_display.assert_called_once_with((800, 700))
    
    def test_screen_to_board_position_conversion(self):
        """Test conversion from screen coordinates to board positions"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView(800, 700)
            
            # Test valid positions
            # Top-left cell
            pos = view._screen_to_board_position((view.board_x + 50, view.board_y + 50))
            assert pos == Position(0, 0)
            
            # Bottom-right cell
            pos = view._screen_to_board_position((view.board_x + 550, view.board_y + 550))
            assert pos == Position(3, 3)
            
            # Center cell
            pos = view._screen_to_board_position((view.board_x + 300, view.board_y + 300))
            assert pos == Position(2, 2)
            
            # Test invalid positions (outside board)
            pos = view._screen_to_board_position((0, 0))
            assert pos is None
            
            pos = view._screen_to_board_position((1000, 1000))
            assert pos is None
    
    def test_board_position_to_screen_conversion(self):
        """Test conversion from board positions to screen coordinates"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView(800, 700)
            
            # Test position (0, 0) - top-left
            x, y = view._board_position_to_screen(Position(0, 0))
            expected_x = view.board_x + view.cell_size // 2
            expected_y = view.board_y + view.cell_size // 2
            assert x == expected_x
            assert y == expected_y
            
            # Test position (3, 3) - bottom-right
            x, y = view._board_position_to_screen(Position(3, 3))
            expected_x = view.board_x + 3 * view.cell_size + view.cell_size // 2
            expected_y = view.board_y + 3 * view.cell_size + view.cell_size // 2
            assert x == expected_x
            assert y == expected_y
    
    def test_highlight_valid_moves(self):
        """Test highlighting valid move positions"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            positions = [Position(0, 0), Position(1, 1), Position(2, 2)]
            view.highlight_valid_moves(positions)
            
            assert len(view.highlighted_positions) == 3
            assert Position(0, 0) in view.highlighted_positions
            assert Position(1, 1) in view.highlighted_positions
            assert Position(2, 2) in view.highlighted_positions
    
    def test_event_handling_mock(self):
        """Test event handling with mocked pygame events"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.event.get') as mock_events:
            
            view = PygameView()
            
            # Mock quit event
            mock_quit_event = MagicMock()
            mock_quit_event.type = pygame.QUIT
            mock_events.return_value = [mock_quit_event]
            
            events = view.handle_events()
            
            assert len(events) == 1
            assert events[0].event_type == "quit"
            assert view.running == False
    
    def test_game_state_rendering_structure(self):
        """Test that rendering methods can be called without errors"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font') as mock_font, \
             patch('pygame.draw.rect'), \
             patch('pygame.draw.line'), \
             patch('pygame.draw.polygon'), \
             patch('pygame.draw.circle'), \
             patch('pygame.display.flip'):
            
            # Mock screen and font objects
            mock_screen = MagicMock()
            mock_display.return_value = mock_screen
            mock_font_obj = MagicMock()
            mock_font_obj.render.return_value = MagicMock()
            mock_font_obj.render.return_value.get_rect.return_value = MagicMock()
            mock_font.return_value = mock_font_obj
            
            view = PygameView()
            game = Game()
            game_state = game.get_game_state()
            
            # These should not raise exceptions
            view.render_board(game_state)
            view.render_ui(game_state)
            view.update_display()
    
    def test_game_over_display(self):
        """Test game over screen display"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font') as mock_font:
            
            mock_screen = MagicMock()
            mock_display.return_value = mock_screen
            mock_font.return_value = MagicMock()
            
            view = PygameView()
            
            # Test with winner
            view.show_game_over("Player 1")
            
            # Test with draw
            view.show_game_over(None)
            
            # Should not raise exceptions
    
    def test_cleanup(self):
        """Test proper cleanup when quitting"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.quit') as mock_quit:
            
            view = PygameView()
            assert view.running == True
            
            view.quit()
            
            assert view.running == False
            mock_quit.assert_called_once()
    
    def test_color_constants(self):
        """Test that color constants are properly defined"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Check that all required colors are defined
            required_colors = [
                'background', 'grid_line', 'board_bg', 'red', 'green',
                'highlight', 'text', 'button', 'button_hover'
            ]
            
            for color_name in required_colors:
                assert color_name in view.COLORS
                color = view.COLORS[color_name]
                assert isinstance(color, tuple)
                assert len(color) == 3
                assert all(0 <= c <= 255 for c in color)
    
    def test_layout_calculations(self):
        """Test that layout calculations are correct"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView(800, 700)
            
            # Board should be centered horizontally
            expected_board_x = (800 - 600) // 2
            assert view.board_x == expected_board_x
            
            # Board should start at y=50
            assert view.board_y == 50
            
            # Cell size should be board_size / 4
            assert view.cell_size == 600 // 4
            
            # Info panel should be below board
            expected_info_y = view.board_y + view.board_size + 20
            assert view.info_panel_y == expected_info_y