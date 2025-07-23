"""
Tests for enhanced click detection and position mapping
"""

import pytest
from unittest.mock import patch, MagicMock
from xoxo_squared.views import PygameView
from xoxo_squared.models import Game, Position, GameEvent


class TestClickDetection:
    def test_enhanced_mouse_click_handling(self):
        """Test enhanced mouse click handling with different click types"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Test board click
            board_click_pos = (view.board_x + 50, view.board_y + 50)
            result = view._handle_mouse_click(board_click_pos)
            
            assert result is not None
            assert result.event_type == "click"
            assert result.position == Position(0, 0)
    
    def test_button_click_detection(self):
        """Test button click detection with enhanced system"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.draw.rect'):
            
            view = PygameView()
            game = Game()
            game_state = game.get_game_state()
            
            # Set up buttons
            view._draw_control_buttons(game_state)
            
            # Test restart button click
            restart_center = view.restart_button_rect.center
            result = view._handle_mouse_click(restart_center)
            
            assert result is not None
            assert result.event_type == "button_click"
            assert result.key == "restart"
            
            # Test quit button click
            quit_center = view.quit_button_rect.center
            result = view._handle_mouse_click(quit_center)
            
            assert result is not None
            assert result.event_type == "button_click"
            assert result.key == "quit"
    
    def test_ui_element_click_detection(self):
        """Test UI element click detection"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Test player panel clicks
            player1_panel_pos = (400, view.info_panel_y + 50)  # Inside player 1 panel
            result = view._handle_mouse_click(player1_panel_pos)
            
            assert result is not None
            assert result.event_type == "ui_click"
            assert result.key == "player1_panel"
            
            player2_panel_pos = (600, view.info_panel_y + 50)  # Inside player 2 panel
            result = view._handle_mouse_click(player2_panel_pos)
            
            assert result is not None
            assert result.event_type == "ui_click"
            assert result.key == "player2_panel"
    
    def test_hover_state_updates(self):
        """Test hover state updates for visual feedback"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Test hover over board position
            board_hover_pos = (view.board_x + 75, view.board_y + 75)
            view._update_hover_state(board_hover_pos)
            
            assert view.hovered_position == Position(0, 0)
            
            # Test hover outside board
            outside_hover_pos = (10, 10)
            view._update_hover_state(outside_hover_pos)
            
            assert view.hovered_position is None
    
    def test_click_feedback_system(self):
        """Test visual click feedback system"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Add click feedback
            test_position = Position(1, 1)
            view.add_click_feedback(test_position)
            
            assert view.last_clicked_position == test_position
            assert view.click_feedback_timer == 30
            
            # Test feedback timer countdown (simulated in _draw_highlights)
            initial_timer = view.click_feedback_timer
            # Simulate one frame of drawing
            view.click_feedback_timer -= 1
            assert view.click_feedback_timer == initial_timer - 1
    
    def test_detailed_click_info(self):
        """Test detailed click information gathering"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.draw.rect'):
            
            view = PygameView()
            game = Game()
            game_state = game.get_game_state()
            
            # Set up UI elements
            view._draw_control_buttons(game_state)
            
            # Test board click info
            board_click_pos = (view.board_x + 100, view.board_y + 100)
            info = view.get_detailed_click_info(board_click_pos)
            
            assert info['type'] == 'board'
            assert info['position'] == Position(0, 0)
            assert info['coordinates'] == board_click_pos
            
            # Test button click info
            restart_center = view.restart_button_rect.center
            info = view.get_detailed_click_info(restart_center)
            
            assert info['type'] == 'button'
            assert info['button'] == 'restart'
            
            # Test empty area click info
            empty_click_pos = (10, 10)
            info = view.get_detailed_click_info(empty_click_pos)
            
            assert info['type'] == 'none'
            assert info['position'] is None
    
    def test_position_clickability_check(self):
        """Test position clickability validation"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            valid_positions = [Position(0, 0), Position(1, 1), Position(2, 2)]
            
            # Test valid position
            assert view.is_position_clickable(Position(0, 0), valid_positions) == True
            assert view.is_position_clickable(Position(1, 1), valid_positions) == True
            
            # Test invalid position
            assert view.is_position_clickable(Position(3, 3), valid_positions) == False
            assert view.is_position_clickable(Position(0, 1), valid_positions) == False
    
    def test_click_precision_analysis(self):
        """Test click precision analysis for user feedback"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Test center click (high precision)
            center_x, center_y = view._board_position_to_screen(Position(1, 1))
            precision_info = view.get_click_precision_info((center_x, center_y))
            
            assert precision_info['board_pos'] == Position(1, 1)
            assert precision_info['precision'] == 'center'
            assert precision_info['distance_from_center'] < view.cell_size * 0.2
            
            # Test edge click (lower precision)
            edge_x = view.board_x + view.cell_size - 5  # Near edge of first cell
            edge_y = view.board_y + 5
            precision_info = view.get_click_precision_info((edge_x, edge_y))
            
            assert precision_info['board_pos'] == Position(0, 0)
            assert precision_info['precision'] == 'edge'
            
            # Test outside board click
            outside_info = view.get_click_precision_info((10, 10))
            assert outside_info['precision'] == 'outside_board'
            assert outside_info['board_pos'] is None
    
    def test_enhanced_event_handling_integration(self):
        """Test integration of enhanced event handling"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.event.get') as mock_events:
            
            view = PygameView()
            
            # Mock mouse click event
            mock_click_event = MagicMock()
            mock_click_event.type = 1025  # pygame.MOUSEBUTTONDOWN
            mock_click_event.button = 1
            mock_click_event.pos = (view.board_x + 50, view.board_y + 50)
            
            # Mock mouse motion event
            mock_motion_event = MagicMock()
            mock_motion_event.type = 1024  # pygame.MOUSEMOTION
            mock_motion_event.pos = (view.board_x + 75, view.board_y + 75)
            
            mock_events.return_value = [mock_click_event, mock_motion_event]
            
            events = view.handle_events()
            
            # Should have processed the click
            click_events = [e for e in events if e.event_type == "click"]
            assert len(click_events) == 1
            assert click_events[0].position == Position(0, 0)
            
            # Should have updated hover state
            assert view.hovered_position == Position(0, 0)
    
    def test_multiple_click_types_priority(self):
        """Test that click types are handled with correct priority"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.draw.rect'):
            
            view = PygameView()
            game = Game()
            game_state = game.get_game_state()
            
            # Set up buttons
            view._draw_control_buttons(game_state)
            
            # Test that button clicks take priority over board clicks
            # (if a button overlapped with board, which it shouldn't, but for testing)
            button_pos = view.restart_button_rect.center
            result = view._handle_mouse_click(button_pos)
            
            # Should be button click, not board click
            assert result.event_type == "button_click"
            assert result.key == "restart"
    
    def test_hover_visual_effects_integration(self):
        """Test that hover effects integrate properly with highlighting"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.draw.rect') as mock_rect, \
             patch('pygame.Surface') as mock_surface:
            
            mock_surface_instance = MagicMock()
            mock_surface.return_value = mock_surface_instance
            
            view = PygameView()
            
            # Set up hover and highlight states
            view.hovered_position = Position(1, 1)
            view.highlighted_positions = [Position(0, 0), Position(2, 2)]
            view.last_clicked_position = Position(0, 1)
            view.click_feedback_timer = 15
            
            # Draw highlights (should include hover and click feedback)
            view._draw_highlights()
            
            # Should have drawn multiple rectangles for different effects
            assert mock_rect.call_count >= 3  # Highlights + hover + click feedback setup
    
    def test_click_detection_edge_cases(self):
        """Test edge cases in click detection"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView()
            
            # Test click exactly on board boundary
            boundary_x = view.board_x
            boundary_y = view.board_y
            result = view._handle_mouse_click((boundary_x, boundary_y))
            
            # Should register as board click for position (0,0)
            assert result is not None
            assert result.event_type == "click"
            assert result.position == Position(0, 0)
            
            # Test click just outside board
            outside_x = view.board_x - 1
            outside_y = view.board_y - 1
            result = view._handle_mouse_click((outside_x, outside_y))
            
            # Should not register as board click
            assert result is None or result.event_type != "click"