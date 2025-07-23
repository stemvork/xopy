"""
Tests for game phase interaction logic
"""

import pytest
from unittest.mock import patch, MagicMock
from xoxo_squared.models import Game, Position, GameEvent, GamePhase, TileColor
from xoxo_squared.views import PygameView
from xoxo_squared.controllers import GameController


class TestGamePhaseInteractions:
    def test_controller_initialization(self):
        """Test game controller initialization"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            assert controller.game == game
            assert controller.view == view
            assert controller.interaction_state['selected_tile_position'] is None
            assert controller.visual_state['highlighted_positions'] == []
    
    def test_tile_placement_phase_interaction(self):
        """Test interactions during tile placement phase"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            # Test valid tile placement
            click_event = GameEvent("click", position=Position(1, 1))
            result = controller.handle_game_event(click_event)
            
            assert result['success'] == True
            assert result['phase_changed'] == True
            assert 'tile_placed' in result['visual_updates']
            
            # Verify game state changed
            game_state = game.get_game_state()
            assert game_state.move_count == 1
            assert game_state.current_player.name == "Player 2"
    
    def test_flip_selection_phase_interaction(self):
        """Test interactions during flip selection phase"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            # Set up game state for flip selection
            game.make_phase_move(Position(1, 1))  # Player 1
            game.make_phase_move(Position(2, 2))  # Player 2
            
            # Now Player 1 should be in flip selection phase
            assert game.get_game_state().phase == GamePhase.FLIP_SELECTION
            
            # Test valid flip selection
            click_event = GameEvent("click", position=Position(1, 1))
            result = controller.handle_game_event(click_event)
            
            assert result['success'] == True
            assert result['phase_changed'] == True
            assert 'show_preview' in result['visual_updates']
            
            # Check that tile position was stored
            assert controller.interaction_state['selected_tile_position'] == Position(1, 1)
            
            # Check preview state
            assert controller.visual_state['preview_tile_position'] == Position(1, 1)
            assert controller.visual_state['preview_tile_color'] is not None
    
    def test_move_selection_phase_interaction(self):
        """Test interactions during move selection phase"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            # Set up game state for move selection
            game.make_phase_move(Position(1, 1))  # Player 1
            game.make_phase_move(Position(2, 2))  # Player 2
            game.make_phase_move(Position(1, 1))  # Player 1 flip selection
            
            # Now should be in move selection phase
            assert game.get_game_state().phase == GamePhase.MOVE_SELECTION
            
            # Test valid move selection
            click_event = GameEvent("click", position=Position(0, 1))  # Valid orthogonal move
            result = controller.handle_game_event(click_event)
            
            assert result['success'] == True
            assert result['phase_changed'] == True
            assert 'animate_move' in result['visual_updates']
            
            # Check that move destination was stored
            assert controller.interaction_state['move_destination'] == Position(0, 1)
            
            # Check that preview was cleared
            assert controller.visual_state['preview_tile_position'] is None
    
    def test_invalid_position_handling(self):
        """Test handling of invalid position clicks"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            # Try to place tile on invalid position (outside valid moves)
            # First, place a tile to make position (1,1) invalid
            game.make_phase_move(Position(1, 1))
            
            # Now try to place on same position
            click_event = GameEvent("click", position=Position(1, 1))
            result = controller.handle_game_event(click_event)
            
            assert result['success'] == False
            assert 'not valid' in result['message']
            assert 'highlight_error' in result['visual_updates']
    
    def test_button_click_handling(self):
        """Test button click handling"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            # Test restart button
            restart_event = GameEvent("button_click", key="restart")
            result = controller.handle_game_event(restart_event)
            
            assert result['success'] == True
            assert result['message'] == 'Game restarted'
            assert result['phase_changed'] == True
            assert 'clear_all' in result['visual_updates']
            
            # Test quit button
            quit_event = GameEvent("button_click", key="quit")
            result = controller.handle_game_event(quit_event)
            
            assert result['success'] == True
            assert 'quit_game' in result['visual_updates']
    
    def test_keyboard_input_handling(self):
        """Test keyboard input handling"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            # Test escape key
            escape_event = GameEvent("key", key="escape")
            result = controller.handle_game_event(escape_event)
            
            assert result['success'] == True
            assert 'quit_game' in result['visual_updates']
            
            # Test restart key when game is over
            game._game_over = True
            game._phase = GamePhase.GAME_OVER
            
            restart_event = GameEvent("key", key="r")
            result = controller.handle_game_event(restart_event)
            
            assert result['success'] == True
            assert result['phase_changed'] == True
            assert 'clear_all' in result['visual_updates']
            
            # Test help key
            help_event = GameEvent("key", key="h")
            result = controller.handle_game_event(help_event)
            
            assert result['success'] == True
            assert 'show_help' in result['visual_updates']
    
    def test_ui_element_click_handling(self):
        """Test UI element click handling"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            # Test player panel clicks
            player1_event = GameEvent("ui_click", key="player1_panel")
            result = controller.handle_game_event(player1_event)
            
            assert result['success'] == True
            assert 'highlight_player1' in result['visual_updates']
            
            player2_event = GameEvent("ui_click", key="player2_panel")
            result = controller.handle_game_event(player2_event)
            
            assert result['success'] == True
            assert 'highlight_player2' in result['visual_updates']
            
            # Test instructions panel click
            instructions_event = GameEvent("ui_click", key="instructions_panel")
            result = controller.handle_game_event(instructions_event)
            
            assert result['success'] == True
            assert 'expand_instructions' in result['visual_updates']
    
    def test_error_message_system(self):
        """Test error message display and timing"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            # Trigger an error
            controller._set_error_message("Test error message")
            
            assert controller.interaction_state['error_message'] == "Test error message"
            assert controller.interaction_state['error_timer'] == 180
            
            # Test error timer countdown
            controller.update()
            assert controller.interaction_state['error_timer'] == 179
            
            # Test error clearing
            controller._clear_error_message()
            assert controller.interaction_state['error_message'] is None
            assert controller.interaction_state['error_timer'] == 0
    
    def test_context_help_system(self):
        """Test context-sensitive help system"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            # Test help for tile placement phase
            help_text = controller.get_context_help()
            assert len(help_text) > 0
            assert any("place" in text.lower() for text in help_text)
            
            # Test help for flip selection phase
            game.make_phase_move(Position(1, 1))  # Player 1
            game.make_phase_move(Position(2, 2))  # Player 2
            
            help_text = controller.get_context_help()
            assert any("flip" in text.lower() for text in help_text)
            
            # Test help for move selection phase
            game.make_phase_move(Position(1, 1))  # Flip selection
            
            help_text = controller.get_context_help()
            assert any("move" in text.lower() for text in help_text)
    
    def test_phase_description_system(self):
        """Test phase description generation"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            # Test initial phase description
            description = controller.get_phase_description()
            assert "Player 1" in description
            assert "Place a tile" in description
            
            # Test after phase change
            game.make_phase_move(Position(1, 1))
            description = controller.get_phase_description()
            assert "Player 2" in description
    
    def test_interaction_state_tracking(self):
        """Test interaction state tracking and debugging info"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            # Get initial state
            state = controller.get_interaction_state()
            assert state['game_phase'] == 'tile_placement'
            assert state['selected_tile'] is None
            assert state['highlighted_count'] >= 0
            
            # Make some moves and check state updates
            game.make_phase_move(Position(1, 1))
            game.make_phase_move(Position(2, 2))
            
            state = controller.get_interaction_state()
            assert state['game_phase'] == 'flip_selection'
    
    def test_visual_state_updates(self):
        """Test visual state updates and synchronization"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            # Test highlight updates
            result = {'visual_updates': ['update_highlights']}
            controller._update_visual_state(result)
            
            # Should have updated highlighted positions
            valid_positions = game.get_valid_positions_for_current_phase()
            assert controller.visual_state['highlighted_positions'] == valid_positions
            
            # Test error display
            result = {'success': False, 'message': 'Test error', 'visual_updates': ['show_error']}
            controller._update_visual_state(result)
            
            assert controller.interaction_state['error_message'] == 'Test error'
            assert controller.interaction_state['error_timer'] > 0
    
    def test_controller_update_loop(self):
        """Test controller update loop functionality"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            # Set up error state
            controller._set_error_message("Test error")
            initial_timer = controller.interaction_state['error_timer']
            
            # Run update
            controller.update()
            
            # Timer should have decremented
            assert controller.interaction_state['error_timer'] == initial_timer - 1
            
            # Test highlight synchronization
            # Change game state
            game.make_phase_move(Position(1, 1))
            
            # Update should sync highlights
            controller.update()
            
            current_valid = game.get_valid_positions_for_current_phase()
            assert controller.visual_state['highlighted_positions'] == current_valid
    
    def test_move_preview_system(self):
        """Test move preview functionality"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            # Initially no preview
            preview = controller.get_move_preview()
            assert preview is None
            
            # Set up preview state
            controller.visual_state['preview_tile_position'] = Position(1, 1)
            controller.visual_state['preview_tile_color'] = TileColor.GREEN
            
            preview = controller.get_move_preview()
            assert preview is not None
            assert preview['position'] == Position(1, 1)
            assert preview['color'] == TileColor.GREEN
            assert preview['type'] == 'flip_preview'
    
    def test_complete_game_flow_through_controller(self):
        """Test complete game flow through controller"""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            
            game = Game()
            view = PygameView()
            controller = GameController(game, view)
            
            # First move - Player 1
            event1 = GameEvent("click", position=Position(1, 1))
            result1 = controller.handle_game_event(event1)
            assert result1['success'] == True
            assert game.get_current_player().name == "Player 2"
            
            # Second move - Player 2
            event2 = GameEvent("click", position=Position(2, 2))
            result2 = controller.handle_game_event(event2)
            assert result2['success'] == True
            assert game.get_game_state().phase == GamePhase.FLIP_SELECTION
            
            # Third move - Player 1 flip selection
            event3 = GameEvent("click", position=Position(1, 1))
            result3 = controller.handle_game_event(event3)
            assert result3['success'] == True
            assert game.get_game_state().phase == GamePhase.MOVE_SELECTION
            
            # Fourth move - Player 1 move selection
            event4 = GameEvent("click", position=Position(0, 1))
            result4 = controller.handle_game_event(event4)
            assert result4['success'] == True
            assert game.get_game_state().phase == GamePhase.TILE_PLACEMENT
            
            # Fifth move - Player 1 tile placement
            event5 = GameEvent("click", position=Position(3, 3))
            result5 = controller.handle_game_event(event5)
            assert result5['success'] == True
            
            # Should have switched back to Player 2
            assert game.get_current_player().name == "Player 2"