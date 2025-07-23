"""
Game class for xoxo^2 game coordination
"""

from typing import Optional, List
from .board import Board
from .player import Player
from .data_classes import GameState, Move, Position, ThreeInRowResult
from .enums import TileShape, GamePhase, TileColor


class MoveResult:
    """Result of attempting to make a move"""
    def __init__(self, success: bool, message: str = "", winner: Optional[Player] = None):
        self.success = success
        self.message = message
        self.winner = winner


class Game:
    """Main game coordinator for xoxo^2"""
    
    def __init__(self):
        """Initialize a new game"""
        self._board = Board()
        self._player1 = Player("Player 1", TileShape.HEXAGON)
        self._player2 = Player("Player 2", TileShape.STAR)
        self._current_player = self._player1
        self._phase = GamePhase.TILE_PLACEMENT  # First move is placement only
        self._move_count = 0
        self._winner = None
        self._game_over = False
        
        # Track partial move state for multi-phase moves
        self._partial_move = {
            'flip_position': None,
            'move_to_position': None,
            'selected_color': None
        }
    
    def start_game(self) -> None:
        """Start a new game"""
        self._board = Board()
        self._player1 = Player("Player 1", TileShape.HEXAGON)
        self._player2 = Player("Player 2", TileShape.STAR)
        self._current_player = self._player1
        self._phase = GamePhase.TILE_PLACEMENT
        self._move_count = 0
        self._winner = None
        self._game_over = False
        self._partial_move = {'flip_position': None, 'move_to_position': None, 'selected_color': None}
    
    def get_current_player(self) -> Player:
        """Get the current player"""
        return self._current_player
    
    def get_other_player(self) -> Player:
        """Get the other player (not current)"""
        return self._player2 if self._current_player == self._player1 else self._player1
    
    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self._game_over
    
    def get_winner(self) -> Optional[Player]:
        """Get the winner if game is over"""
        return self._winner
    
    def get_game_state(self) -> GameState:
        """Get the current game state"""
        return GameState(
            current_player=self._current_player,
            phase=self._phase,
            move_count=self._move_count,
            winner=self._winner
        )
    
    def get_board(self) -> Board:
        """Get the game board"""
        return self._board
    
    def get_valid_positions_for_current_phase(self) -> List[Position]:
        """Get valid positions for the current game phase"""
        if self._game_over:
            return []
        
        if self._phase == GamePhase.TILE_PLACEMENT:
            # Return empty positions where tiles can be placed
            return [Position(row, col) for row in range(4) for col in range(4) 
                   if self._board.is_position_empty(Position(row, col))]
        
        elif self._phase == GamePhase.FLIP_SELECTION:
            # Return positions with tiles that can be flipped and moved
            valid_positions = []
            for row in range(4):
                for col in range(4):
                    pos = Position(row, col)
                    if not self._board.is_position_empty(pos):
                        # Check if this tile can be moved
                        valid_moves = self._board.get_valid_moves(pos)
                        if len(valid_moves) > 0:
                            valid_positions.append(pos)
            
            # Handle edge case: no tiles can be moved
            if not valid_positions:
                # This is a critical game state - should trigger draw or special handling
                self._handle_no_valid_moves()
            
            return valid_positions
        
        elif self._phase == GamePhase.MOVE_SELECTION:
            # Return valid move destinations for the selected tile
            if self._partial_move['flip_position']:
                valid_moves = self._board.get_valid_moves(self._partial_move['flip_position'])
                
                # Handle edge case: selected tile suddenly has no valid moves
                if not valid_moves:
                    # Reset to flip selection phase
                    self._phase = GamePhase.FLIP_SELECTION
                    self._partial_move['flip_position'] = None
                    return self.get_valid_positions_for_current_phase()
                
                return valid_moves
            return []
        
        elif self._phase == GamePhase.COLOR_SELECTION:
            # Return special positions for color selection (we'll use positions to represent colors)
            return [Position(0, 0), Position(0, 1)]  # Red and Green color choices
        
        return []
    
    def _handle_no_valid_moves(self) -> None:
        """Handle the edge case where no valid moves are available"""
        # Check if board is full
        if self._board.is_full():
            # Board is full, declare draw
            self._game_over = True
            self._phase = GamePhase.GAME_OVER
            return
        
        # Check if any tiles can be moved at all
        can_move_any = False
        for row in range(4):
            for col in range(4):
                pos = Position(row, col)
                if not self._board.is_position_empty(pos):
                    if len(self._board.get_valid_moves(pos)) > 0:
                        can_move_any = True
                        break
            if can_move_any:
                break
        
        if not can_move_any:
            # No tiles can be moved - this is a stalemate
            self._game_over = True
            self._phase = GamePhase.GAME_OVER
            # Winner is None (draw)
    
    def make_move(self, move: Move) -> MoveResult:
        """
        Make a complete move
        
        Args:
            move: The move to make
            
        Returns:
            MoveResult indicating success/failure and any winner
        """
        if self._game_over:
            return MoveResult(False, "Game is already over")
        
        # Validate move based on current game state
        validation_result = self._validate_move(move)
        if not validation_result.success:
            return validation_result
        
        # Execute the move
        try:
            self._execute_move(move)
            
            # Check for win condition after move
            winner = self.check_win_after_move()
            if winner:
                self._winner = winner
                self._game_over = True
                self._phase = GamePhase.GAME_OVER
                return MoveResult(True, f"{winner.name} wins!", winner)
            
            # Check for draw condition
            if self._is_draw():
                self._game_over = True
                self._phase = GamePhase.GAME_OVER
                return MoveResult(True, "Game is a draw!")
            
            # Switch turns
            self._switch_turn()
            
            return MoveResult(True, "Move completed successfully")
            
        except Exception as e:
            return MoveResult(False, f"Error executing move: {str(e)}")
    
    def make_phase_move(self, position: Position) -> MoveResult:
        """
        Make a move for the current phase (used for interactive gameplay)
        
        Args:
            position: Position for the current phase action
            
        Returns:
            MoveResult indicating success and next phase
        """
        if self._game_over:
            return MoveResult(False, "Game is already over")
        
        try:
            if self._phase == GamePhase.TILE_PLACEMENT:
                # First move or placement phase
                if self._move_count < 1:
                    # Only the very first move - just place tile
                    return self._handle_first_move(position)
                else:
                    # Regular placement after flip and move
                    return self._handle_tile_placement(position)
            
            elif self._phase == GamePhase.FLIP_SELECTION:
                return self._handle_flip_selection(position)
            
            elif self._phase == GamePhase.MOVE_SELECTION:
                return self._handle_move_selection(position)
            
            elif self._phase == GamePhase.COLOR_SELECTION:
                return self._handle_color_selection(position)
            
            else:
                return MoveResult(False, f"Invalid phase: {self._phase}")
                
        except Exception as e:
            return MoveResult(False, f"Error in phase move: {str(e)}")
    
    def check_win_after_move(self) -> Optional[Player]:
        """
        Check for win condition after a move using complex xoxo^2 rules
        
        Returns:
            Winning player if there's a winner, None otherwise
        """
        # Get all three-in-a-row formations
        three_in_rows = self._board.check_three_in_row()
        
        if not three_in_rows:
            return None
        
        # Check each three-in-a-row to see if it's survivable
        for three_in_row in three_in_rows:
            opponent = self.get_other_player()
            
            # Check if opponent can break this three-in-a-row on their next turn
            can_break = self._board.can_opponent_break_three_in_row(three_in_row, opponent)
            
            if not can_break:
                # This three-in-a-row cannot be broken - we have a winner
                # Determine which player wins based on the color
                return self._current_player  # Current player just made the winning move
        
        return None
    
    def simulate_opponent_responses(self, three_in_row: ThreeInRowResult) -> bool:
        """
        Simulate if opponent can break a three-in-a-row formation
        
        Args:
            three_in_row: The formation to check
            
        Returns:
            True if opponent can break it, False otherwise
        """
        opponent = self.get_other_player()
        return self._board.can_opponent_break_three_in_row(three_in_row, opponent)
    
    def _validate_move(self, move: Move) -> MoveResult:
        """Validate a complete move"""
        # First move validation
        if self._move_count == 0:
            if move.flip_position is not None or move.move_to_position is not None:
                return MoveResult(False, "First move must be placement only")
            if not self._board.is_position_empty(move.place_position):
                return MoveResult(False, "Cannot place tile on occupied position")
            return MoveResult(True)
        
        # Regular move validation
        if move.flip_position is None:
            return MoveResult(False, "Must flip a tile (except for first move)")
        
        # Check if flip position has a tile
        if self._board.is_position_empty(move.flip_position):
            return MoveResult(False, "Cannot flip empty position")
        
        # Check if tile can be moved
        valid_moves = self._board.get_valid_moves(move.flip_position)
        if not valid_moves:
            return MoveResult(False, "Selected tile cannot be moved")
        
        if move.move_to_position not in valid_moves:
            return MoveResult(False, "Invalid move destination")
        
        # Check if placement position is valid
        if not self._board.is_position_empty(move.place_position):
            # Special case: if moving to the place position, that's ok
            if move.move_to_position != move.place_position:
                return MoveResult(False, "Cannot place tile on occupied position")
        
        # Check if player has tiles remaining
        if not self._current_player.can_place_tile():
            # Player can still flip and move, but cannot place new tiles
            # This is allowed in the game rules
            pass
        
        return MoveResult(True)
    
    def _execute_move(self, move: Move) -> None:
        """Execute a validated move"""
        if self._move_count == 0:
            # First move - just place tile
            if self._current_player.can_place_tile():
                tile = self._current_player.use_tile(TileColor.RED)  # Default to RED
                self._board.place_tile(move.place_position, tile)
        else:
            # Regular move - flip, move, then place
            # 1. Flip the tile
            tile_to_flip = self._board.get_tile(move.flip_position)
            tile_to_flip.flip()
            
            # 2. Move the tile
            self._board.remove_tile(move.flip_position)
            self._board.place_tile(move.move_to_position, tile_to_flip)
            
            # 3. Place new tile (if player has tiles remaining)
            if self._current_player.can_place_tile():
                new_tile = self._current_player.use_tile(TileColor.RED)  # Default to RED
                self._board.place_tile(move.place_position, new_tile)
        
        self._move_count += 1
    
    def _handle_first_move(self, position: Position) -> MoveResult:
        """Handle the very first move of the game"""
        if not self._board.is_position_empty(position):
            return MoveResult(False, "Cannot place tile on occupied position")
        
        if not self._current_player.can_place_tile():
            return MoveResult(False, "Player has no tiles remaining")
        
        # Place the tile with selected color or default to RED for first move
        selected_color = self._partial_move.get('selected_color') or TileColor.RED
        tile = self._current_player.use_tile(selected_color)
        self._board.place_tile(position, tile)
        self._move_count += 1
        
        # Check for immediate win (unlikely on first move, but possible in theory)
        winner = self.check_win_after_move()
        if winner:
            self._winner = winner
            self._game_over = True
            self._phase = GamePhase.GAME_OVER
            return MoveResult(True, f"{winner.name} wins!", winner)
        
        # Switch to next player
        self._switch_turn()
        
        return MoveResult(True, "First move completed")
    
    def _handle_flip_selection(self, position: Position) -> MoveResult:
        """Handle flip selection phase"""
        if self._board.is_position_empty(position):
            return MoveResult(False, "Cannot flip empty position")
        
        # Check if tile can be moved
        valid_moves = self._board.get_valid_moves(position)
        if not valid_moves:
            return MoveResult(False, "Selected tile cannot be moved")
        
        # Flip the tile immediately
        tile = self._board.get_tile(position)
        if tile:
            tile.flip()
        
        # Store the flip position and move to next phase
        self._partial_move['flip_position'] = position
        self._phase = GamePhase.MOVE_SELECTION
        
        return MoveResult(True, "Tile selected and flipped")
    
    def _handle_move_selection(self, position: Position) -> MoveResult:
        """Handle move selection phase"""
        flip_pos = self._partial_move['flip_position']
        if not flip_pos:
            return MoveResult(False, "No tile selected for flipping")
        
        valid_moves = self._board.get_valid_moves(flip_pos)
        if position not in valid_moves:
            return MoveResult(False, "Invalid move destination")
        
        # Actually move the tile now (not later)
        tile_to_move = self._board.get_tile(flip_pos)
        if tile_to_move is None:
            return MoveResult(False, f"No tile found at position ({flip_pos.row},{flip_pos.col}) to move")
        
        # Move the tile immediately
        self._board.remove_tile(flip_pos)
        self._board.place_tile(position, tile_to_move)
        
        # Store move position and proceed to placement
        self._partial_move['move_to_position'] = position
        self._phase = GamePhase.TILE_PLACEMENT
        
        return MoveResult(True, f"Tile moved to ({position.row},{position.col}). Now place your new tile.")
    
    def _handle_tile_placement(self, position: Position) -> MoveResult:
        """Handle tile placement phase"""
        if not self._board.is_position_empty(position):
            return MoveResult(False, "Cannot place tile on occupied position")
        
        # The tile has already been moved in the move selection phase
        # Now we just need to place the new tile
        
        try:
            # Place new tile (if player has tiles remaining)
            if self._current_player.can_place_tile():
                selected_color = self._partial_move.get('selected_color') or TileColor.RED
                new_tile = self._current_player.use_tile(selected_color)
                self._board.place_tile(position, new_tile)
                
                self._move_count += 1
                
                # Check for win condition after move
                winner = self.check_win_after_move()
                if winner:
                    self._winner = winner
                    self._game_over = True
                    self._phase = GamePhase.GAME_OVER
                    return MoveResult(True, f"{winner.name} wins!", winner)
                
                # Check for draw condition
                if self._is_draw():
                    self._game_over = True
                    self._phase = GamePhase.GAME_OVER
                    return MoveResult(True, "Game is a draw!")
                
                # Switch turns
                self._switch_turn()
                
                return MoveResult(True, "Move completed successfully")
                
        except Exception as e:
            return MoveResult(False, f"Error executing move: {str(e)}")
    
    def _handle_color_selection(self, position: Position) -> MoveResult:
        """Handle color selection phase"""
        # Use position to represent color choice: (0,0) = RED, (0,1) = GREEN
        if position.row == 0 and position.col == 0:
            selected_color = TileColor.RED
        elif position.row == 0 and position.col == 1:
            selected_color = TileColor.GREEN
        else:
            return MoveResult(False, "Invalid color selection")
        
        # Store selected color and move to tile placement
        self._partial_move['selected_color'] = selected_color
        self._phase = GamePhase.TILE_PLACEMENT
        
        return MoveResult(True, f"Color {selected_color.value} selected")
    
    def _switch_turn(self) -> None:
        """Switch to the other player"""
        self._current_player = self.get_other_player()
        
        # Reset phase for next turn based on corrected game flow
        if self._move_count < 1:  # Only the very first move is placement only
            self._phase = GamePhase.TILE_PLACEMENT
        else:  # After the first move, all subsequent moves are flip-move-place
            self._phase = GamePhase.FLIP_SELECTION  # Regular flip-move-place sequence
        
        # Reset partial move state
        self._partial_move = {'flip_position': None, 'move_to_position': None, 'selected_color': None}
    
    def _is_draw(self) -> bool:
        """Check if the game is a draw"""
        # Game is a draw if board is full and no winner
        if not self._board.is_full():
            return False
        
        # Additional check: if no player can make any moves
        # (This is a more complex condition that might be implemented later)
        return True