"""
Tests for tile graphics and board rendering
"""

import pytest
from unittest.mock import patch, MagicMock
from xoxo_squared.views import PygameView
from xoxo_squared.models import Game, Position, TileColor, TileShape


class TestTileGraphics:
    def test_board_tile_rendering(self):
        """Test rendering tiles from actual board"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font') as mock_font, \
             patch('pygame.draw.rect'), \
             patch('pygame.draw.line'), \
             patch('pygame.draw.polygon'), \
             patch('pygame.draw.circle'), \
             patch('pygame.display.flip'):
            
            # Mock setup
            mock_screen = MagicMock()
            mock_display.return_value = mock_screen
            mock_font_obj = MagicMock()
            mock_font_obj.render.return_value = MagicMock()
            mock_font_obj.render.return_value.get_rect.return_value = MagicMock()
            mock_font.return_value = mock_font_obj
            
            view = PygameView()
            game = Game()
            
            # Place some tiles on the board
            game.make_phase_move(Position(1, 1))  # Player 1 - hexagon
            game.make_phase_move(Position(2, 2))  # Player 2 - star
            
            game_state = game.get_game_state()
            board = game.get_board()
            
            # Should render without errors
            view.render_board(game_state, board)
            
            # Verify tiles are on the board
            all_tiles = board.get_all_tiles()
            assert len(all_tiles) == 2
            
            # Verify tile properties
            pos1, tile1 = all_tiles[0]
            pos2, tile2 = all_tiles[1]
            
            assert tile1.get_shape() == TileShape.HEXAGON
            assert tile2.get_shape() == TileShape.STAR
            assert tile1.get_current_color() == TileColor.RED  # Default first color
            assert tile2.get_current_color() == TileColor.RED
    
    def test_tile_shape_rendering(self):
        """Test that different tile shapes are rendered correctly"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.draw.polygon') as mock_polygon, \
             patch('pygame.draw.circle') as mock_circle:
            
            view = PygameView()
            
            # Test hexagon rendering
            view._draw_hexagon(100, 100, 30, (255, 0, 0))
            assert mock_polygon.call_count >= 2  # Main shape + highlight
            
            # Reset mock
            mock_polygon.reset_mock()
            mock_circle.reset_mock()
            
            # Test star rendering
            view._draw_star(100, 100, 30, (0, 255, 0))
            assert mock_polygon.call_count >= 2  # Main shape + border
            assert mock_circle.call_count >= 2  # Center circle + border
    
    def test_position_indicators(self):
        """Test that position indicators are drawn"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font') as mock_font:
            
            mock_screen = MagicMock()
            mock_display.return_value = mock_screen
            mock_font_obj = MagicMock()
            mock_text_surface = MagicMock()
            mock_text_surface.get_rect.return_value = MagicMock()
            mock_font_obj.render.return_value = mock_text_surface
            mock_font.return_value = mock_font_obj
            
            view = PygameView()
            view._draw_position_indicators()
            
            # Should render 4 row numbers + 4 column numbers = 8 calls
            assert mock_font_obj.render.call_count == 8
            assert mock_screen.blit.call_count == 8
    
    def test_tile_size_calculation(self):
        """Test that tile sizes are calculated correctly based on cell size"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            view = PygameView(800, 700)
            
            # Cell size should be board_size / 4
            expected_cell_size = 600 // 4  # 150
            assert view.cell_size == expected_cell_size
            
            # Tile radius should be min(cell_size // 3, 40)
            expected_tile_radius = min(expected_cell_size // 3, 40)  # min(50, 40) = 40
            
            # We can't directly test the radius calculation since it's inside _draw_tile,
            # but we can verify the cell size is correct
            assert view.cell_size == 150
    
    def test_color_rendering(self):
        """Test that tile colors are rendered correctly"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.draw.polygon') as mock_polygon, \
             patch('pygame.draw.circle'):
            
            view = PygameView()
            
            # Test red tile
            view._draw_tile(Position(0, 0), TileColor.RED, TileShape.HEXAGON)
            
            # Check that red color was used (first call should be the main shape)
            calls = mock_polygon.call_args_list
            assert len(calls) >= 1
            # The second argument should be the color
            red_color_used = any(call[0][1] == view.COLORS['red'] for call in calls)
            assert red_color_used
            
            # Reset and test green tile
            mock_polygon.reset_mock()
            view._draw_tile(Position(1, 1), TileColor.GREEN, TileShape.STAR)
            
            calls = mock_polygon.call_args_list
            green_color_used = any(call[0][1] == view.COLORS['green'] for call in calls)
            assert green_color_used
    
    def test_enhanced_ui_with_player_info(self):
        """Test UI rendering with actual player information"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font') as mock_font:
            
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
            
            # Render UI with player info
            view.render_ui(game_state, game._player1, game._player2)
            
            # Check that player tile counts are rendered
            render_calls = [call[0][0] for call in mock_font_obj.render.call_args_list]
            
            # Should include tile count information
            tile_count_rendered = any("tiles" in call for call in render_calls)
            assert tile_count_rendered
    
    def test_board_integration_with_game_state(self):
        """Test that board rendering integrates properly with game state"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.draw.rect'), \
             patch('pygame.draw.line'), \
             patch('pygame.draw.polygon'), \
             patch('pygame.draw.circle'), \
             patch('pygame.display.flip'):
            
            view = PygameView()
            game = Game()
            
            # Make several moves to create a more complex board state
            game.make_phase_move(Position(0, 0))  # Player 1
            game.make_phase_move(Position(1, 1))  # Player 2
            game.make_phase_move(Position(2, 2))  # Player 1 (flip selection)
            game.make_phase_move(Position(2, 1))  # Player 1 (move selection)
            game.make_phase_move(Position(3, 3))  # Player 1 (tile placement)
            
            game_state = game.get_game_state()
            board = game.get_board()
            
            # Should render without errors
            view.render_board(game_state, board)
            view.render_ui(game_state, game._player1, game._player2)
            
            # Verify board has tiles
            all_tiles = board.get_all_tiles()
            assert len(all_tiles) >= 2  # Should have at least the tiles we placed
    
    def test_highlight_integration_with_tiles(self):
        """Test that highlights work correctly with actual tiles"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.draw.rect') as mock_rect, \
             patch('pygame.draw.line'), \
             patch('pygame.draw.polygon'), \
             patch('pygame.draw.circle'), \
             patch('pygame.display.flip'):
            
            view = PygameView()
            game = Game()
            
            # Place some tiles
            game.make_phase_move(Position(1, 1))
            game.make_phase_move(Position(2, 2))
            
            # Get valid positions for current phase
            valid_positions = game.get_valid_positions_for_current_phase()
            view.highlight_valid_moves(valid_positions)
            
            game_state = game.get_game_state()
            board = game.get_board()
            
            # Render board with highlights
            view.render_board(game_state, board)
            
            # Should have called rect drawing for highlights
            highlight_calls = [call for call in mock_rect.call_args_list 
                             if len(call[0]) >= 3 and call[0][1] == view.COLORS['highlight']]
            
            # Should have highlight rectangles if there are valid positions
            if len(valid_positions) > 0:
                assert len(highlight_calls) > 0
    
    def test_empty_board_rendering(self):
        """Test rendering an empty board"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'), \
             patch('pygame.draw.rect'), \
             patch('pygame.draw.line'), \
             patch('pygame.display.flip'):
            
            view = PygameView()
            game = Game()
            game_state = game.get_game_state()
            board = game.get_board()
            
            # Empty board should render without errors
            view.render_board(game_state, board)
            
            # Verify board is actually empty
            all_tiles = board.get_all_tiles()
            assert len(all_tiles) == 0