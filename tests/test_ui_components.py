"""
Tests for UI components and game state display
"""

import pytest
import pygame
from unittest.mock import patch, MagicMock
from xoxo_squared.views import PygameView
from xoxo_squared.models import Game, Position, GamePhase


class TestUIComponents:
    def test_enhanced_title_rendering(self):
        """Test enhanced title with background"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font') as mock_font, \
             patch('pygame.draw.rect') as mock_rect:
            
            mock_screen = MagicMock()
            mock_display.return_value = mock_screen
            mock_font_obj = MagicMock()
            mock_text_surface = MagicMock()
            mock_text_surface.get_rect.return_value = MagicMock()
            mock_font_obj.render.return_value = mock_text_surface
            mock_font.return_value = mock_font_obj
            
            view = PygameView()
            view._draw_title()
            
            # Should draw title background and border
            assert mock_rect.call_count >= 2  # Background + border
            assert mock_screen.blit.call_count >= 1  # Title text
    
    def test_game_info_panel_rendering(self):
        """Test game information panel"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font') as mock_font, \
             patch('pygame.draw.rect'):
            
            mock_screen = MagicMock()
            mock_display.return_value = mock_screen
            mock_font_obj = MagicMock()
            mock_text_surface = MagicMock()
            mock_text_surface.get_rect.return_value = MagicMock()
            mock_font_obj.render.return_value = mock_text_surface
            mock_font.return_value = mock_font_obj
            
            view = PygameView()
            game = Game()
            game_state = game.get_game_state()
            
            view._draw_game_info_panel(game_state, game._player1, game._player2)
            
            # Should render multiple text elements
            assert mock_font_obj.render.call_count >= 3  # Panel title, player, phase, move
    
    def test_player_panels_rendering(self):
        """Test individual player status panels"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font') as mock_font, \
             patch('pygame.draw.rect') as mock_rect, \
             patch('pygame.draw.polygon'), \
             patch('pygame.draw.circle'):
            
            mock_screen = MagicMock()
            mock_display.return_value = mock_screen
            mock_font_obj = MagicMock()
            mock_text_surface = MagicMock()
            mock_text_surface.get_rect.return_value = MagicMock()
            mock_font_obj.render.return_value = mock_text_surface
            mock_font.return_value = mock_font_obj
            
            view = PygameView()
            game = Game()
            game_state = game.get_game_state()
            
            view._draw_player_panels(game_state, game._player1, game._player2)
            
            # Should draw 2 player panels
            panel_rects = [call for call in mock_rect.call_args_list if len(call[0]) >= 2]
            assert len(panel_rects) >= 4  # 2 panels × 2 calls each (background + border)
            
            # Should render player names and tile counts
            assert mock_font_obj.render.call_count >= 4  # 2 players × 2 text elements each
    
    def test_control_buttons_rendering(self):
        """Test control buttons (restart, quit)"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font') as mock_font, \
             patch('pygame.draw.rect') as mock_rect:
            
            mock_screen = MagicMock()
            mock_display.return_value = mock_screen
            mock_font_obj = MagicMock()
            mock_text_surface = MagicMock()
            mock_text_surface.get_rect.return_value = MagicMock()
            mock_font_obj.render.return_value = mock_text_surface
            mock_font.return_value = mock_font_obj
            
            view = PygameView()
            game = Game()
            game_state = game.get_game_state()
            
            view._draw_control_buttons(game_state)
            
            # Should draw 2 buttons (restart + quit)
            button_rects = [call for call in mock_rect.call_args_list if len(call[0]) >= 2]
            assert len(button_rects) >= 4  # 2 buttons × 2 calls each (background + border)
            
            # Should render button text
            assert mock_font_obj.render.call_count >= 2  # "Restart" + "Quit"
            
            # Should store button rects for click detection
            assert hasattr(view, 'restart_button_rect')
            assert hasattr(view, 'quit_button_rect')
    
    def test_instructions_panel_rendering(self):
        """Test instructions panel with context-sensitive content"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font') as mock_font, \
             patch('pygame.draw.rect'):
            
            mock_screen = MagicMock()
            mock_display.return_value = mock_screen
            mock_font_obj = MagicMock()
            mock_text_surface = MagicMock()
            mock_text_surface.get_rect.return_value = MagicMock()
            mock_font_obj.render.return_value = mock_text_surface
            mock_font.return_value = mock_font_obj
            
            view = PygameView()
            game = Game()
            game_state = game.get_game_state()
            
            view._draw_instructions_panel(game_state)
            
            # Should render panel title and instructions
            assert mock_font_obj.render.call_count >= 2  # Title + at least one instruction
    
    def test_phase_specific_instructions(self):
        """Test that instructions change based on game phase"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            game = Game()
            
            # Test tile placement phase
            game_state = game.get_game_state()
            instructions = view._get_phase_instructions(game_state)
            assert len(instructions) > 0
            assert any("place" in inst.lower() for inst in instructions)
            
            # Test flip selection phase
            game.make_phase_move(Position(1, 1))  # Player 1
            game.make_phase_move(Position(2, 2))  # Player 2
            game_state = game.get_game_state()
            instructions = view._get_phase_instructions(game_state)
            assert any("flip" in inst.lower() for inst in instructions)
            
            # Test game over phase
            game._game_over = True
            game._phase = GamePhase.GAME_OVER
            game._winner = game._player1
            game_state = game.get_game_state()
            instructions = view._get_phase_instructions(game_state)
            assert any("wins" in inst.lower() for inst in instructions)
    
    def test_button_click_detection(self):
        """Test button click detection"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.draw.rect'):
            
            view = PygameView()
            game = Game()
            game_state = game.get_game_state()
            
            # Draw buttons to set up rects
            view._draw_control_buttons(game_state)
            
            # Test restart button click
            restart_center = view.restart_button_rect.center
            button_clicked = view.check_button_clicks(restart_center)
            assert button_clicked == "restart"
            
            # Test quit button click
            quit_center = view.quit_button_rect.center
            button_clicked = view.check_button_clicks(quit_center)
            assert button_clicked == "quit"
            
            # Test click outside buttons
            button_clicked = view.check_button_clicks((0, 0))
            assert button_clicked == ""
    
    def test_mouse_hover_effects(self):
        """Test mouse hover effects on buttons"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Test mouse over detection
            test_rect = pygame.Rect(100, 100, 50, 30)
            
            # Mouse inside rect
            view.mouse_pos = (125, 115)
            assert view._is_mouse_over_rect(test_rect) == True
            
            # Mouse outside rect
            view.mouse_pos = (50, 50)
            assert view._is_mouse_over_rect(test_rect) == False
    
    def test_complete_ui_rendering(self):
        """Test complete UI rendering with all components"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font') as mock_font, \
             patch('pygame.draw.rect'), \
             patch('pygame.draw.polygon'), \
             patch('pygame.draw.circle'):
            
            mock_screen = MagicMock()
            mock_display.return_value = mock_screen
            mock_font_obj = MagicMock()
            mock_text_surface = MagicMock()
            mock_text_surface.get_rect.return_value = MagicMock()
            mock_font_obj.render.return_value = mock_text_surface
            mock_font.return_value = mock_font_obj
            
            view = PygameView()
            game = Game()
            
            # Make some moves to create interesting game state
            game.make_phase_move(Position(1, 1))
            game.make_phase_move(Position(2, 2))
            
            game_state = game.get_game_state()
            
            # Should render without errors
            view.render_ui(game_state, game._player1, game._player2)
            
            # Should have rendered many text elements
            assert mock_font_obj.render.call_count >= 10  # Many UI elements
    
    def test_ui_with_different_game_states(self):
        """Test UI rendering with different game states"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.draw.rect'), \
             patch('pygame.draw.polygon'), \
             patch('pygame.draw.circle'):
            
            view = PygameView()
            
            # Test with new game
            game = Game()
            game_state = game.get_game_state()
            view.render_ui(game_state, game._player1, game._player2)
            
            # Test with game in progress
            game.make_phase_move(Position(0, 0))
            game.make_phase_move(Position(1, 1))
            game_state = game.get_game_state()
            view.render_ui(game_state, game._player1, game._player2)
            
            # Test with game over
            game._game_over = True
            game._phase = GamePhase.GAME_OVER
            game._winner = game._player1
            game_state = game.get_game_state()
            view.render_ui(game_state, game._player1, game._player2)
            
            # All should render without errors
    
    def test_player_visual_indicators(self):
        """Test visual indicators for current player"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font') as mock_font, \
             patch('pygame.draw.rect') as mock_rect, \
             patch('pygame.draw.polygon'), \
             patch('pygame.draw.circle'):
            
            mock_font_obj = MagicMock()
            mock_text_surface = MagicMock()
            mock_text_surface.get_rect.return_value = MagicMock()
            mock_font_obj.render.return_value = mock_text_surface
            mock_font.return_value = mock_font_obj
            
            view = PygameView()
            game = Game()
            game_state = game.get_game_state()
            
            view._draw_player_panels(game_state, game._player1, game._player2)
            
            # Should draw different border thickness for current player
            rect_calls = mock_rect.call_args_list
            border_calls = [call for call in rect_calls if len(call[0]) >= 3]  # Calls with border width
            
            # Should have some border calls (current player gets thicker border)
            assert len(border_calls) >= 2