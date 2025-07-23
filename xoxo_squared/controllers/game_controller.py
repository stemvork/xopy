"""
Game Controller for xoxo^2 - Handles phase-based interaction logic
"""

from typing import Optional, List, Dict, Any
from ..models import Game, Position, GamePhase, GameEvent, TileColor
from ..views import PygameView


class GameController:
    """
    Controller that manages game phase interactions and coordinates between
    the game model and view for complex xoxo^2 gameplay
    """
    
    def __init__(self, game: Game, view: PygameView):
        """
        Initialize the game controller
        
        Args:
            game: Game model instance
            view: View instance for rendering and input
        """
        self.game = game
        self.view = view
        
        # Phase interaction state
        self.interaction_state = {
            'selected_tile_position': None,
            'move_destination': None,
            'awaiting_confirmation': False,
            'last_action': None,
            'error_message': None,
            'error_timer': 0
        }
        
        # Visual feedback state
        self.visual_state = {
            'highlighted_positions': [],
            'preview_tile_position': None,
            'preview_tile_color': None,
            'animation_state': None
        }
    
    def handle_game_event(self, event: GameEvent) -> Dict[str, Any]:
        """
        Handle a game event based on current phase
        
        Args:
            event: Game event to process
            
        Returns:
            Dictionary with result information
        """
        result = {
            'success': False,
            'message': '',
            'phase_changed': False,
            'game_over': False,
            'winner': None,
            'visual_updates': []
        }
        
        try:
            if event.event_type == "click" and event.position:
                result = self._handle_board_click(event.position)
            elif event.event_type == "button_click":
                result = self._handle_button_click(event.key)
            elif event.event_type == "ui_click":
                result = self._handle_ui_click(event.key)
            elif event.event_type == "key":
                result = self._handle_key_press(event.key)
            
            # Update visual state based on result
            self._update_visual_state(result)
            
        except Exception as e:
            result['success'] = False
            result['message'] = f"Error handling event: {str(e)}"
            self._set_error_message(result['message'])
            
            # Show user-friendly error message
            self.view.show_error_message(f"An error occurred: {str(e)}", error_type="system")
            
            # Log detailed error for debugging
            import traceback
            print(f"Error in game controller: {str(e)}")
            print(traceback.format_exc())
        
        return result
    
    def _handle_board_click(self, position: Position) -> Dict[str, Any]:
        """Handle board position clicks based on current game phase"""
        current_phase = self.game.get_game_state().phase
        
        if current_phase == GamePhase.TILE_PLACEMENT:
            return self._handle_tile_placement_click(position)
        elif current_phase == GamePhase.FLIP_SELECTION:
            return self._handle_flip_selection_click(position)
        elif current_phase == GamePhase.MOVE_SELECTION:
            return self._handle_move_selection_click(position)
        elif current_phase == GamePhase.GAME_OVER:
            self.view.show_constraint_violation('game_over', position)
            return {'success': False, 'message': 'Game is over. Press R to restart.'}
        else:
            return {'success': False, 'message': f'Unknown game phase: {current_phase}'}
    
    def _handle_tile_placement_click(self, position: Position) -> Dict[str, Any]:
        """Handle clicks during tile placement phase"""
        # Check if position is valid for placement
        valid_positions = self.game.get_valid_positions_for_current_phase()
        
        if position not in valid_positions:
            # Provide specific error feedback based on why position is invalid
            if not self.game.get_board().is_position_empty(position):
                self.view.show_constraint_violation('occupied_position', position)
                error_msg = f'Position ({position.row},{position.col}) is already occupied'
            else:
                # Check if player is out of tiles
                current_player = self.game.get_current_player()
                if not current_player.can_place_tile():
                    self.view.show_constraint_violation('out_of_tiles', position)
                    error_msg = f'No tiles remaining! You can only flip and move existing tiles.'
                else:
                    self.view.show_constraint_violation('invalid_phase', position)
                    error_msg = f'Position ({position.row},{position.col}) is not valid for tile placement'
            
            # Show visual feedback for invalid move with shake animation
            self.view.show_invalid_move_feedback(position)
            self.view.add_error_shake_animation(position)
            
            return {
                'success': False,
                'message': error_msg,
                'visual_updates': ['highlight_error', 'show_error', 'animate_error']
            }
        
        # Get the selected color from visual state
        selected_color = self.visual_state.get('preview_tile_color', 'red')
        if not isinstance(selected_color, str) or selected_color not in ['red', 'green']:
            selected_color = 'red'
            
        # Set the color in the game's partial move state
        color_enum = TileColor.RED if selected_color == 'red' else TileColor.GREEN
        self.game._partial_move['selected_color'] = color_enum
        
        # Attempt to place tile
        result = self.game.make_phase_move(position)
        
        if result.success:
            # Add visual feedback for successful placement
            self.view.add_click_feedback(position)
            
            # Add placement animation
            current_player = self.game.get_current_player()
            
            # Use the selected color from visual state if available
            selected_color = self.visual_state.get('preview_tile_color', 'red')
            if not isinstance(selected_color, str) or selected_color not in ['red', 'green']:
                selected_color = 'red'
                
            tile_data = {
                'shape': current_player.get_shape().value,
                'color': selected_color,  # Use selected color
                'owner': current_player.name
            }
            self.view.add_tile_placement_animation(position, tile_data)
            
            response = {
                'success': True,
                'message': result.message,
                'phase_changed': True,
                'visual_updates': ['tile_placed', 'update_highlights', 'animate_placement']
            }
            
            # Check for game over
            if result.winner:
                response['game_over'] = True
                response['winner'] = result.winner
                response['visual_updates'].append('show_winner')
                
                # Add win celebration animation if there's a three-in-a-row
                board = self.game.get_board()
                three_in_rows = board.check_three_in_row()
                if three_in_rows:
                    # Find the winning three-in-a-row that can't be broken
                    for tir in three_in_rows:
                        if not board.can_opponent_break_three_in_row(tir, self.game.get_other_player()):
                            self.view.add_win_celebration_animation(tir.positions)
                            break
            
            # Additional check for game over condition (board full or no valid moves)
            elif self.game.is_game_over():
                response['game_over'] = True
                response['winner'] = self.game.get_game_state().winner
                response['visual_updates'].append('show_winner')
            
            return response
        else:
            # Show error message on screen
            self.view.show_error_message(result.message, position)
            
            return {
                'success': False,
                'message': result.message,
                'visual_updates': ['show_error']
            }
    
    def _handle_flip_selection_click(self, position: Position) -> Dict[str, Any]:
        """Handle clicks during flip selection phase"""
        valid_positions = self.game.get_valid_positions_for_current_phase()
        
        if position not in valid_positions:
            # Provide specific error feedback
            if self.game.get_board().is_position_empty(position):
                self.view.show_constraint_violation('empty_position_flip', position)
                error_msg = f'Position ({position.row},{position.col}) is empty - select a tile to flip'
            else:
                self.view.show_constraint_violation('no_valid_moves', position)
                error_msg = f'Tile at ({position.row},{position.col}) cannot be moved (no adjacent empty spaces)'
            
            # Show visual feedback for invalid selection
            self.view.show_invalid_move_feedback(position)
            
            return {
                'success': False,
                'message': error_msg,
                'visual_updates': ['highlight_error', 'show_error']
            }
        
        # Store selected tile and proceed to move selection
        self.interaction_state['selected_tile_position'] = position
        
        result = self.game.make_phase_move(position)
        
        if result.success:
            # Show preview of flipped tile and add flip animation
            board = self.game.get_board()
            tile = board.get_tile(position)
            if tile:
                # Preview what the tile will look like after flipping
                current_color = tile.get_current_color()
                preview_color = TileColor.GREEN if current_color == TileColor.RED else TileColor.RED
                self.visual_state['preview_tile_position'] = position
                self.visual_state['preview_tile_color'] = preview_color
                
                # Add flip animation
                self.view.add_tile_flip_animation(position, current_color, preview_color)
            
            # Add click feedback for successful selection
            self.view.add_click_feedback(position)
            
            return {
                'success': True,
                'message': f'Tile selected at {position.row},{position.col}. Choose where to move it.',
                'phase_changed': True,
                'visual_updates': ['update_highlights', 'show_preview', 'refresh_board', 'animate_flip']
            }
        else:
            # Show error message on screen
            self.view.show_error_message(result.message, position)
            
            return {
                'success': False,
                'message': result.message,
                'visual_updates': ['show_error']
            }
    
    def _handle_move_selection_click(self, position: Position) -> Dict[str, Any]:
        """Handle clicks during move selection phase"""
        valid_positions = self.game.get_valid_positions_for_current_phase()
        
        if position not in valid_positions:
            # Provide specific error feedback for move selection
            selected_pos = self.interaction_state['selected_tile_position']
            self.view.show_constraint_violation('invalid_move_direction', position)
            
            if selected_pos:
                error_msg = f'Cannot move tile from ({selected_pos.row},{selected_pos.col}) to ({position.row},{position.col}). Only orthogonal moves allowed.'
            else:
                error_msg = f'Cannot move tile to ({position.row},{position.col}). Only orthogonal moves allowed.'
            
            # Show visual feedback for invalid move
            self.view.show_invalid_move_feedback(position)
            
            return {
                'success': False,
                'message': error_msg,
                'visual_updates': ['highlight_error', 'show_error']
            }
        
        # Store move destination
        self.interaction_state['move_destination'] = position
        
        result = self.game.make_phase_move(position)
        
        if result.success:
            # Add click feedback for successful move
            self.view.add_click_feedback(position)
            
            # Add move animation
            selected_pos = self.interaction_state['selected_tile_position']
            if selected_pos:
                board = self.game.get_board()
                tile = board.get_tile(position)  # Tile is now at destination
                if tile:
                    tile_data = {
                        'shape': tile.get_shape().value,
                        'color': tile.get_current_color().value,
                        'owner': tile.get_owner().name
                    }
                    self.view.add_tile_move_animation(selected_pos, position, tile_data)
            
            # Clear preview state
            self.visual_state['preview_tile_position'] = None
            self.visual_state['preview_tile_color'] = None
            
            return {
                'success': True,
                'message': f'Tile moved to {position.row},{position.col}. Now place your new tile.',
                'phase_changed': True,
                'visual_updates': ['clear_preview', 'update_highlights', 'animate_move', 'refresh_board']
            }
        else:
            # Show error message on screen
            self.view.show_error_message(result.message, position)
            
            return {
                'success': False,
                'message': result.message,
                'visual_updates': ['show_error']
            }
    
    def _handle_button_click(self, button: str) -> Dict[str, Any]:
        """Handle button clicks"""
        if button == "restart":
            self.game.start_game()
            self._reset_interaction_state()
            return {
                'success': True,
                'message': 'Game restarted',
                'phase_changed': True,
                'visual_updates': ['clear_all', 'update_highlights']
            }
        elif button == "quit":
            # Ensure view knows to quit
            self.view.running = False
            return {
                'success': True,
                'message': 'Quitting game',
                'visual_updates': ['quit_game']
            }
        else:
            return {'success': False, 'message': f'Unknown button: {button}'}
    
    def _handle_ui_click(self, ui_element: str) -> Dict[str, Any]:
        """Handle UI element clicks"""
        if ui_element == "player1_panel":
            return {
                'success': True,
                'message': 'Player 1 panel clicked',
                'visual_updates': ['highlight_player1']
            }
        elif ui_element == "player2_panel":
            return {
                'success': True,
                'message': 'Player 2 panel clicked',
                'visual_updates': ['highlight_player2']
            }
        elif ui_element == "instructions_panel":
            return {
                'success': True,
                'message': 'Instructions panel clicked',
                'visual_updates': ['expand_instructions']
            }
        else:
            return {'success': False, 'message': f'Unknown UI element: {ui_element}'}
    
    def _handle_key_press(self, key: str) -> Dict[str, Any]:
        """Handle keyboard input with enhanced shortcuts"""
        if key == "escape":
            # Cancel restart confirmation if active
            if self.view.restart_confirmation_active:
                self.view.hide_restart_confirmation()
                return {
                    'success': True,
                    'message': 'Restart cancelled',
                    'visual_updates': ['hide_restart_confirmation']
                }
            # Hide help overlay if active
            elif self.view.show_help_overlay:
                self.view.toggle_help_overlay()
                return {
                    'success': True,
                    'message': 'Help overlay hidden',
                    'visual_updates': ['hide_help']
                }
            else:
                # Ensure view knows to quit
                self.view.running = False
                return {
                    'success': True,
                    'message': 'Escape pressed - quitting',
                    'visual_updates': ['quit_game']
                }
        
        elif key == "r":
            # Handle restart with confirmation
            if self.view.restart_confirmation_active:
                # Confirm restart
                self.game.start_game()
                self._reset_interaction_state()
                self.view.hide_restart_confirmation()
                return {
                    'success': True,
                    'message': 'Game restarted',
                    'phase_changed': True,
                    'visual_updates': ['clear_all', 'update_highlights', 'hide_restart_confirmation']
                }
            else:
                # Show restart confirmation
                self.view.show_restart_confirmation()
                return {
                    'success': True,
                    'message': 'Press R again to confirm restart',
                    'visual_updates': ['show_restart_confirmation']
                }
        
        elif key == "shift+r":
            # Force restart without confirmation
            self.game.start_game()
            self._reset_interaction_state()
            self.view.hide_restart_confirmation()
            return {
                'success': True,
                'message': 'Game force restarted',
                'phase_changed': True,
                'visual_updates': ['clear_all', 'update_highlights', 'hide_restart_confirmation']
            }
        
        elif key == "ctrl+r":
            # Quick restart (no confirmation needed)
            self.game.start_game()
            self._reset_interaction_state()
            self.view.hide_restart_confirmation()
            return {
                'success': True,
                'message': 'Game quick restarted',
                'phase_changed': True,
                'visual_updates': ['clear_all', 'update_highlights']
            }
        
        elif key == "ctrl+q":
            # Quick quit
            return {
                'success': True,
                'message': 'Quick quit',
                'visual_updates': ['quit_game']
            }
        
        elif key == "h" or key == "ctrl+h":
            self.view.toggle_help_overlay()
            help_status = "shown" if self.view.show_help_overlay else "hidden"
            return {
                'success': True,
                'message': f'Help overlay {help_status}',
                'visual_updates': ['show_help' if self.view.show_help_overlay else 'hide_help']
            }
        
        elif key == "f1":
            # Show detailed help
            self.view.show_help_overlay = True
            return {
                'success': True,
                'message': 'Detailed help shown',
                'visual_updates': ['show_help']
            }
        
        elif key == "u":
            # Undo last action (if implemented)
            return self._handle_undo()
        
        elif key == "space":
            # Show contextual help
            game_state = self.game.get_game_state()
            board = self.game.get_board()
            self.view.show_contextual_help(game_state, board)
            return {
                'success': True,
                'message': 'Contextual help shown',
                'visual_updates': ['show_help']
            }
        
        elif key == "tab":
            # Show game statistics or advanced info
            self._show_game_statistics()
            return {
                'success': True,
                'message': 'Game statistics shown',
                'visual_updates': ['show_stats']
            }
        
        elif key == "a":
            # Toggle animations on/off
            enabled = self.view.toggle_animations()
            status_text = "enabled" if enabled else "disabled"
            self.view.show_info_message(f"Animations {status_text}", 120)
            return {
                'success': True,
                'message': f'Animations {status_text}',
                'visual_updates': ['toggle_animations']
            }
        
        elif key == "s":
            # Toggle animation speed (when animations are enabled)
            if self.view.are_animations_enabled():
                new_speed = 2.0 if self.view.animation_speed == 1.0 else 1.0
                self.view.set_animation_speed(new_speed)  # Use setter to save settings
                speed_text = "fast" if new_speed == 2.0 else "normal"
                self.view.show_info_message(f"Animation speed: {speed_text}", 120)
                return {
                    'success': True,
                    'message': f'Animation speed set to {speed_text}',
                    'visual_updates': ['update_animation_speed']
                }
            else:
                self.view.show_info_message("Enable animations first (press A)", 120)
                return {
                    'success': False,
                    'message': 'Animations are disabled',
                    'visual_updates': ['show_info']
                }
        
        elif key == "p":
            # Pause/unpause (for future implementation)
            return {
                'success': False,
                'message': 'Pause functionality not yet implemented',
                'visual_updates': ['show_info']
            }
        
        elif key == "c":
            # Toggle tile color for preview (red/green)
            if self.game.get_game_state().phase == GamePhase.TILE_PLACEMENT:
                current_player = self.game.get_current_player()
                if current_player.can_place_tile():
                    # Get current preview color, default to red if not set or invalid
                    current_color = self.visual_state.get('preview_tile_color', 'red')
                    if not isinstance(current_color, str) or current_color not in ['red', 'green']:
                        current_color = 'red'
                    
                    # Toggle between red and green
                    new_color = 'green' if current_color == 'red' else 'red'
                    
                    # Update cursor preview
                    tile_data = {
                        'shape': current_player.get_shape().value,
                        'color': new_color,
                        'owner': current_player.name
                    }
                    self.view.set_cursor_preview(tile_data, enabled=True)
                    
                    # Store new color in visual state
                    self.visual_state['preview_tile_color'] = new_color
                    
                    # Show feedback message
                    self.view.show_info_message(f"Tile color changed to {new_color.upper()}", 60)
                    
                    return {
                        'success': True,
                        'message': f'Tile color changed to {new_color}',
                        'visual_updates': ['update_cursor_preview']
                    }
            
            return {
                'success': False,
                'message': 'Can only change color during tile placement phase',
                'visual_updates': ['show_info']
            }
        
        else:
            return {'success': False, 'message': f'Unknown key: {key}'}
    
    def _handle_undo(self) -> Dict[str, Any]:
        """Handle undo functionality (placeholder for future implementation)"""
        return {
            'success': False,
            'message': 'Undo not yet implemented',
            'visual_updates': ['show_info']
        }
    
    def _show_game_statistics(self) -> None:
        """Show detailed game statistics and information"""
        game_state = self.game.get_game_state()
        board = self.game.get_board()
        
        # Calculate statistics
        total_tiles = sum(1 for r in range(4) for c in range(4) 
                         if not board.is_position_empty(Position(r, c)))
        empty_spaces = 16 - total_tiles
        
        player1 = self.game._player1
        player2 = self.game._player2
        
        p1_tiles_used = 8 - player1.get_tiles_remaining()
        p2_tiles_used = 8 - player2.get_tiles_remaining()
        
        # Count tiles by color on board
        red_tiles = 0
        green_tiles = 0
        for r in range(4):
            for c in range(4):
                tile = board.get_tile(Position(r, c))
                if tile:
                    if tile.get_current_color().value == 'red':
                        red_tiles += 1
                    else:
                        green_tiles += 1
        
        # Create statistics message
        stats_lines = [
            f"📊 Game Statistics (Move {game_state.move_count})",
            "",
            f"🎮 Players:",
            f"  {player1.name}: {p1_tiles_used}/8 tiles used, {player1.get_tiles_remaining()} remaining",
            f"  {player2.name}: {p2_tiles_used}/8 tiles used, {player2.get_tiles_remaining()} remaining",
            "",
            f"🎨 Board Colors:",
            f"  Red tiles: {red_tiles}",
            f"  Green tiles: {green_tiles}",
            f"  Empty spaces: {empty_spaces}",
            "",
            f"⚡ Current Phase: {game_state.phase.value.replace('_', ' ').title()}",
            f"🎯 Current Player: {game_state.current_player.name}"
        ]
        
        # Check for potential wins
        three_in_rows = board.check_three_in_row()
        if three_in_rows:
            stats_lines.append("")
            stats_lines.append("🏆 Three-in-a-row formations:")
            for tir in three_in_rows:
                can_break = board.can_opponent_break_three_in_row(tir, game_state.current_player)
                status = "Breakable" if can_break else "WINNING!"
                stats_lines.append(f"  {tir.color.value.title()} {tir.direction} - {status}")
        
        # Show as info message
        stats_text = "\n".join(stats_lines)
        self.view.show_info_message(stats_text, 300)  # 5 seconds
    
    def _update_cursor_preview(self, current_phase) -> None:
        """Update cursor preview based on current game phase"""
        if current_phase == GamePhase.TILE_PLACEMENT:
            # Enable cursor preview for tile placement
            current_player = self.game.get_current_player()
            if current_player.can_place_tile():
                # Use color from visual state if available, otherwise default to red
                preview_color = self.visual_state.get('preview_tile_color', 'red')
                
                # Ensure preview_color is a valid string
                if not isinstance(preview_color, str) or preview_color not in ['red', 'green']:
                    preview_color = 'red'
                
                tile_data = {
                    'shape': current_player.get_shape().value,
                    'color': preview_color,
                    'owner': current_player.name
                }
                self.view.set_cursor_preview(tile_data, enabled=True)
            else:
                # No tiles to place
                self.view.set_cursor_preview({}, enabled=False)
        else:
            # Disable cursor preview for other phases
            self.view.set_cursor_preview({}, enabled=False)
    
    def _update_visual_state(self, result: Dict[str, Any]) -> None:
        """Update visual state based on interaction result"""
        # Update highlighted positions with phase-specific highlighting
        if 'update_highlights' in result.get('visual_updates', []):
            valid_positions = self.game.get_valid_positions_for_current_phase()
            self.visual_state['highlighted_positions'] = valid_positions
            self._apply_phase_specific_highlighting(valid_positions)
        
        # Handle error display with visual feedback
        if 'show_error' in result.get('visual_updates', []):
            self._set_error_message(result.get('message', 'Unknown error'))
        
        # Handle error highlighting for invalid positions
        if 'highlight_error' in result.get('visual_updates', []):
            error_message = result.get('message', 'Invalid move')
            self._set_error_message(error_message)
            # Could add position-specific error highlighting here if needed
        
        # Handle visual feedback for successful moves
        if 'tile_placed' in result.get('visual_updates', []):
            # Check for resource warnings after tile placement
            self._check_resource_warnings()
        
        if 'show_preview' in result.get('visual_updates', []):
            # Preview effects are handled in the phase-specific handlers
            pass
        
        if 'clear_preview' in result.get('visual_updates', []):
            self.visual_state['preview_tile_position'] = None
            self.visual_state['preview_tile_color'] = None
        
        if 'animate_move' in result.get('visual_updates', []):
            # Set up animation state for tile movement
            if self.interaction_state['selected_tile_position'] and self.interaction_state['move_destination']:
                self.visual_state['animation_state'] = {
                    'type': 'move',
                    'from_position': self.interaction_state['selected_tile_position'],
                    'to_position': self.interaction_state['move_destination'],
                    'frames_remaining': 15,  # 15 frames for animation
                    'progress': 0.0
                }
        
        # Clear error if successful
        if result.get('success', False):
            self._clear_error_message()
    
    def _check_resource_warnings(self) -> None:
        """Check for resource-related warnings and display them"""
        current_player = self.game.get_current_player()
        other_player = self.game.get_other_player()
        
        # Warn when player is running low on tiles
        if current_player.get_tiles_remaining() == 2:
            self.view.show_warning_message(f"{current_player.name}: Only 2 tiles remaining!")
        elif current_player.get_tiles_remaining() == 1:
            self.view.show_warning_message(f"{current_player.name}: Last tile!")
        elif current_player.get_tiles_remaining() == 0:
            self.view.show_info_message(f"{current_player.name}: No tiles left - flip and move only")
        
        # Show info about opponent's resources
        if other_player.get_tiles_remaining() == 0:
            self.view.show_info_message(f"{other_player.name} has no tiles remaining")
    
    def _provide_move_guidance(self, game_state) -> None:
        """Provide contextual move guidance based on game state"""
        current_phase = game_state.phase
        current_player = game_state.current_player
        
        if current_phase == GamePhase.FLIP_SELECTION:
            # Count available flip options and provide detailed guidance
            valid_positions = self.game.get_valid_positions_for_current_phase()
            
            if len(valid_positions) == 0:
                self.view.show_constraint_violation('no_tiles_to_flip')
                self.view.show_rule_explanation('flip_move_place')
            elif len(valid_positions) == 1:
                self.view.show_info_message("Only one tile can be moved - it's highlighted in yellow")
                # Show tooltip for the single valid position
                pos = valid_positions[0]
                tooltip_msg = self.view.get_position_tooltip(pos, game_state, self.game.get_board())
                screen_pos = self.view._board_position_to_screen(pos)
                self.view.show_tooltip(tooltip_msg, screen_pos, 180)
            else:
                # Show constraints for flip selection
                constraints = self._get_flip_selection_constraints()
                if constraints:
                    self.view.show_move_constraints(constraints)
        
        elif current_phase == GamePhase.MOVE_SELECTION:
            # Show movement constraints and guidance
            selected_pos = self.interaction_state.get('selected_tile_position')
            if selected_pos:
                valid_moves = self.game.get_board().get_valid_moves(selected_pos)
                
                if len(valid_moves) == 0:
                    self.view.show_constraint_violation('no_valid_moves', selected_pos)
                    # This should trigger a return to flip selection
                elif len(valid_moves) == 1:
                    self.view.show_info_message("Only one move possible - position is highlighted")
                    # Show rule explanation about orthogonal movement
                    self.view.show_rule_explanation('orthogonal_only')
                else:
                    # Show movement constraints
                    constraints = self._get_movement_constraints(selected_pos)
                    if constraints:
                        self.view.show_move_constraints(constraints, selected_pos)
        
        elif current_phase == GamePhase.TILE_PLACEMENT:
            # Provide placement guidance with resource awareness
            if not current_player.can_place_tile():
                self.view.show_info_message("No tiles to place - turn will end after this phase")
                self.view.show_rule_explanation('resource_management')
            else:
                empty_positions = self.game.get_valid_positions_for_current_phase()
                tiles_remaining = current_player.get_tiles_remaining()
                
                if len(empty_positions) <= 3:
                    self.view.show_warning_message(f"Board getting full - only {len(empty_positions)} spaces left")
                
                if tiles_remaining <= 2:
                    self.view.show_warning_message(f"Only {tiles_remaining} tiles remaining - plan carefully!")
                
                # Show strategic guidance
                if game_state.move_count < 4:  # Early game
                    self.view.show_rule_explanation('first_moves')
                else:
                    # Show winning condition reminder
                    self.view.show_rule_explanation('three_in_row')
    
    def _get_flip_selection_constraints(self) -> List[str]:
        """Get constraints that apply to flip selection phase"""
        constraints = []
        
        # Basic flip selection rules
        constraints.append("Only tiles that can move are highlighted")
        constraints.append("Tiles must have adjacent empty spaces to be flippable")
        constraints.append("Flipping changes tile color (red ↔ green)")
        
        # Resource-based constraints
        current_player = self.game.get_current_player()
        if current_player.get_tiles_remaining() == 0:
            constraints.append("No tiles remaining - focus on strategic positioning")
        
        return constraints
    
    def _get_movement_constraints(self, selected_position: Position) -> List[str]:
        """Get constraints that apply to movement phase"""
        constraints = []
        
        # Basic movement rules
        constraints.append("Only orthogonal moves allowed (up, down, left, right)")
        constraints.append("Cannot move diagonally")
        constraints.append("Destination must be empty")
        
        # Position-specific constraints
        board = self.game.get_board()
        valid_moves = board.get_valid_moves(selected_position)
        
        if len(valid_moves) < 4:  # Less than all directions available
            blocked_directions = []
            pos = selected_position
            
            # Check each direction
            directions = [
                ((-1, 0), "up"),
                ((1, 0), "down"),
                ((0, -1), "left"),
                ((0, 1), "right")
            ]
            
            for (dr, dc), direction in directions:
                new_pos = Position(pos.row + dr, pos.col + dc)
                if (new_pos.row < 0 or new_pos.row >= 4 or 
                    new_pos.col < 0 or new_pos.col >= 4):
                    blocked_directions.append(f"{direction} (board edge)")
                elif not board.is_position_empty(new_pos):
                    blocked_directions.append(f"{direction} (occupied)")
            
            if blocked_directions:
                constraints.append(f"Blocked directions: {', '.join(blocked_directions)}")
        
        return constraints
    
    def _check_edge_cases(self, valid_positions: List[Position], current_phase) -> None:
        """Check for edge cases and provide appropriate guidance"""
        # Check for no valid moves
        if len(valid_positions) == 0:
            if current_phase == GamePhase.FLIP_SELECTION:
                self.view.show_edge_case_guidance('no_valid_moves', {
                    'phase': 'flip_selection',
                    'board_full': self.game.get_board().is_full()
                })
                self.view.show_constraint_violation('no_tiles_to_flip')
            elif current_phase == GamePhase.MOVE_SELECTION:
                self.view.show_edge_case_guidance('no_valid_moves', {
                    'phase': 'move_selection'
                })
                self.view.show_constraint_violation('invalid_sequence')
            elif current_phase == GamePhase.TILE_PLACEMENT:
                if self.game.get_board().is_full():
                    self.view.show_edge_case_guidance('board_nearly_full', {
                        'board_full': True
                    })
                    self.view.show_constraint_violation('board_full')
                else:
                    self.view.show_constraint_violation('invalid_phase')
        
        # Check for very limited options
        elif len(valid_positions) == 1:
            self.view.show_edge_case_guidance('forced_move', {
                'phase': current_phase.value,
                'positions_available': 1
            })
        
        # Check for resource depletion and warnings
        current_player = self.game.get_current_player()
        other_player = self.game.get_other_player()
        
        current_tiles = current_player.get_tiles_remaining()
        other_tiles = other_player.get_tiles_remaining()
        
        # Both players out of tiles
        if current_tiles == 0 and other_tiles == 0:
            self.view.show_edge_case_guidance('no_valid_moves', {
                'both_players_out': True
            })
        
        # Current player running low on tiles
        elif current_tiles <= 2 and current_tiles > 0:
            self.view.show_edge_case_guidance('low_tiles', {
                'tiles_remaining': current_tiles
            })
            # Show strategic tip for resource conservation
            self.view.show_strategic_tip('resource_conservation', {
                'tiles_remaining': current_tiles
            })
        
        # Board getting full
        board_empty_spaces = len([pos for pos in [Position(r, c) for r in range(4) for c in range(4)] 
                                if self.game.get_board().is_position_empty(pos)])
        
        if board_empty_spaces <= 3 and board_empty_spaces > 0:
            self.view.show_edge_case_guidance('board_nearly_full', {
                'positions_available': board_empty_spaces
            })
        
        # Check for potential stalemate conditions
        if current_phase == GamePhase.FLIP_SELECTION and len(valid_positions) <= 2:
            if board_empty_spaces <= 2:
                self.view.show_edge_case_guidance('no_valid_moves', {
                    'near_stalemate': True,
                    'positions_available': board_empty_spaces
                })
        
        # Check for potential winning opportunities
        self._check_winning_opportunities()
    
    def _check_winning_opportunities(self) -> None:
        """Check for potential winning opportunities and threats"""
        board = self.game.get_board()
        current_player = self.game.get_current_player()
        
        # Check for existing three-in-a-row formations
        three_in_rows = board.check_three_in_row()
        
        if three_in_rows:
            for three_in_row in three_in_rows:
                # Check if current player can defend against this threat
                can_break = board.can_opponent_break_three_in_row(three_in_row, current_player)
                
                if not can_break:
                    # This is a winning position for the opponent
                    self.view.show_edge_case_guidance('opponent_threat', {
                        'color': three_in_row.color.value,
                        'direction': three_in_row.direction
                    })
                else:
                    # Current player can potentially break this
                    self.view.show_edge_case_guidance('potential_win', {
                        'defensive_opportunity': True
                    })
        
        # Additional analysis could be added here for:
        # - Potential two-in-a-row formations
        # - Strategic positioning opportunities
        # - Blocking opportunities
    
    def _set_error_message(self, message: str) -> None:
        """Set error message with timer"""
        self.interaction_state['error_message'] = message
        self.interaction_state['error_timer'] = 180  # 3 seconds at 60 FPS
    
    def _clear_error_message(self) -> None:
        """Clear error message"""
        self.interaction_state['error_message'] = None
        self.interaction_state['error_timer'] = 0
    
    def _apply_phase_specific_highlighting(self, valid_positions: List[Position]) -> None:
        """Apply phase-specific highlighting based on current game phase"""
        current_phase = self.game.get_game_state().phase
        
        if current_phase == GamePhase.TILE_PLACEMENT:
            # Highlight empty positions for tile placement
            self.view.highlight_empty_positions(valid_positions)
            # Add subtle pulse animation for placement positions
            if valid_positions:
                self.view.add_highlight_pulse_animation(valid_positions, 120)
        
        elif current_phase == GamePhase.FLIP_SELECTION:
            # Highlight tiles that can be flipped
            self.view.highlight_flip_candidates(valid_positions)
            # Add more prominent pulse for flip selection
            if valid_positions:
                self.view.add_highlight_pulse_animation(valid_positions, 90)
        
        elif current_phase == GamePhase.MOVE_SELECTION:
            # Highlight valid move destinations
            self.view.highlight_move_destinations(valid_positions)
            # Add directional pulse for move destinations
            if valid_positions:
                self.view.add_highlight_pulse_animation(valid_positions, 60)
        
        else:
            # Fallback to generic highlighting
            self.view.highlight_valid_moves(valid_positions)
    
    def start_game(self) -> None:
        """Start a new game"""
        self.game.start_game()
        self._reset_interaction_state()
    
    def handle_click(self, position: Position) -> Dict[str, Any]:
        """Handle a board position click"""
        event = GameEvent("click", position=position)
        return self.handle_game_event(event)
    
    def _reset_interaction_state(self) -> None:
        """Reset interaction state to initial values"""
        self.interaction_state = {
            'selected_tile_position': None,
            'move_destination': None,
            'awaiting_confirmation': False,
            'last_action': None,
            'error_message': None,
            'error_timer': 0
        }
        
        self.visual_state = {
            'highlighted_positions': [],
            'preview_tile_position': None,
            'preview_tile_color': None,
            'animation_state': None
        }
    
    def update(self) -> None:
        """Update controller state (called each frame)"""
        # Update error timer
        if self.interaction_state['error_timer'] > 0:
            self.interaction_state['error_timer'] -= 1
            if self.interaction_state['error_timer'] <= 0:
                self._clear_error_message()
        
        # Update visual highlights and check for edge cases
        try:
            current_valid_positions = self.game.get_valid_positions_for_current_phase()
            current_phase = self.game.get_game_state().phase
            
            # Check for edge cases and provide guidance
            self._check_edge_cases(current_valid_positions, current_phase)
            
            # Update highlights
            self.visual_state['highlighted_positions'] = current_valid_positions
            self._apply_phase_specific_highlighting(current_valid_positions)
            
            # Update cursor preview for tile placement
            self._update_cursor_preview(current_phase)
            
        except Exception as e:
            print(f"Error in controller update: {str(e)}")
            # Continue gracefully without crashingelf.game.get_valid_positions_for_current_phase()
        if current_valid_positions != self.visual_state['highlighted_positions']:
            self.visual_state['highlighted_positions'] = current_valid_positions
            
            # Apply phase-specific highlighting
            current_phase = self.game.get_game_state().phase
            if current_phase == GamePhase.TILE_PLACEMENT:
                self.view.highlight_empty_positions(current_valid_positions)
            elif current_phase == GamePhase.FLIP_SELECTION:
                self.view.highlight_flip_candidates(current_valid_positions)
            elif current_phase == GamePhase.MOVE_SELECTION:
                self.view.highlight_move_destinations(current_valid_positions)
            else:
                self.view.highlight_valid_moves(current_valid_positions)
            
            # Provide contextual guidance when highlights change
            self._provide_move_guidance(self.game.get_game_state())
            
            # Check for edge cases
            self._check_edge_cases(current_valid_positions, current_phase)
        
        # Update animation states if needed
        if self.visual_state.get('animation_state'):
            # Process animation frames
            # This would be expanded with actual animation logic
            self.visual_state['animation_state']['frames_remaining'] -= 1
            if self.visual_state['animation_state']['frames_remaining'] <= 0:
                self.visual_state['animation_state'] = None
    
    def get_interaction_state(self) -> Dict[str, Any]:
        """Get current interaction state for debugging/display"""
        return {
            'game_phase': self.game.get_game_state().phase.value,
            'selected_tile': self.interaction_state['selected_tile_position'],
            'move_destination': self.interaction_state['move_destination'],
            'error_message': self.interaction_state['error_message'],
            'error_timer': self.interaction_state['error_timer'],
            'highlighted_count': len(self.visual_state['highlighted_positions']),
            'preview_active': self.visual_state['preview_tile_position'] is not None
        }
    
    def get_context_help(self) -> List[str]:
        """Get context-sensitive help based on current game state"""
        current_phase = self.game.get_game_state().phase
        
        if current_phase == GamePhase.TILE_PLACEMENT:
            if self.game.get_game_state().move_count < 2:
                return [
                    "First moves: Click any empty position to place your tile",
                    "Your tile will be RED by default",
                    "Try to plan for future three-in-a-row opportunities"
                ]
            else:
                return [
                    "Place your new tile on any empty position",
                    "Complete your flip-move-place sequence",
                    "Consider defensive and offensive positioning"
                ]
        
        elif current_phase == GamePhase.FLIP_SELECTION:
            return [
                "Select a tile to flip and move",
                "Only tiles that can move are highlighted",
                "Flipping changes the tile's color (red ↔ green)",
                "Plan your move to disrupt opponent or help yourself"
            ]
        
        elif current_phase == GamePhase.MOVE_SELECTION:
            selected_pos = self.interaction_state['selected_tile_position']
            if selected_pos:
                return [
                    f"Move the selected tile from {selected_pos.row},{selected_pos.col}",
                    "Only orthogonal moves allowed (up/down/left/right)",
                    "Highlighted positions show valid destinations",
                    "Consider how this move affects the board"
                ]
            else:
                return ["Choose where to move the flipped tile"]
        
        elif current_phase == GamePhase.GAME_OVER:
            winner = self.game.get_winner()
            if winner:
                return [
                    f"{winner.name} wins!",
                    "Press R to restart or ESC to quit",
                    "Great game! Try again?"
                ]
            else:
                return [
                    "Game ended in a draw!",
                    "Press R to restart or ESC to quit",
                    "Well played by both sides!"
                ]
        
        else:
            return ["Unknown game state - something went wrong!"]
    
    def get_phase_description(self) -> str:
        """Get human-readable description of current phase"""
        current_phase = self.game.get_game_state().phase
        current_player = self.game.get_current_player().name
        
        descriptions = {
            GamePhase.TILE_PLACEMENT: f"{current_player}: Place a tile",
            GamePhase.FLIP_SELECTION: f"{current_player}: Select tile to flip",
            GamePhase.MOVE_SELECTION: f"{current_player}: Choose move destination",
            GamePhase.GAME_OVER: "Game finished"
        }
        
        return descriptions.get(current_phase, "Unknown phase")
    
    def can_undo(self) -> bool:
        """Check if undo is possible (placeholder for future implementation)"""
        return False  # Not implemented yet
    
    def get_move_preview(self) -> Optional[Dict[str, Any]]:
        """Get preview information for current move in progress"""
        if self.visual_state['preview_tile_position']:
            return {
                'position': self.visual_state['preview_tile_position'],
                'color': self.visual_state['preview_tile_color'],
                'type': 'flip_preview'
            }
        return None