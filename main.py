"""
Main entry point for xoxo^2 game
"""

import sys
import pygame
from xoxo_squared.models import Game, GamePhase, Position
from xoxo_squared.views import PygameView
from xoxo_squared.controllers import GameController


def main():
    """Main game loop"""
    # Initialize game, view, and controller
    game = Game()
    view = PygameView()
    controller = GameController(game, view)
    
    print("Starting xoxo^2 game...")
    print("Enhanced controls:")
    print("- Click on board positions to make moves")
    print("- Press ESC to quit, R to restart, H for help")
    print("- First move is placement only")
    print("- All other moves: flip → move → place")
    print("- Context-sensitive instructions provided")
    
    # Initialize game state
    game.start_game()
    
    # Set initial highlights
    valid_positions = game.get_valid_positions_for_current_phase()
    view.highlight_valid_moves(valid_positions)
    
    print(f"Game initialized. Valid positions: {len(valid_positions)}")
    print(f"Current player: {game.get_current_player().name}")
    print(f"Current phase: {game.get_game_state().phase}")
    print("Window should be visible now...")
    
    try:
        print("Entering main game loop...")
        frame_count = 0
        
        # Main game loop
        while view.is_running():
            # Update controller state
            controller.update()
            
            # Handle events
            events = view.handle_events()
            
            for event in events:
                if event.event_type == "quit":
                    print("Quitting game...")
                    break
                else:
                    # Let controller handle all other events
                    result = controller.handle_game_event(event)
                    
                    if result['success']:
                        print(f"Action successful: {result['message']}")
                        
                        # Handle game over state
                        if result.get('game_over', False):
                            winner = result.get('winner')
                            if winner:
                                print(f"🎉 Game over! Winner: {winner.name}")
                            else:
                                print("🤝 Game ended in a draw!")
                    else:
                        if result['message']:
                            print(f"Action failed: {result['message']}")
                    
                    # Handle quit request from controller
                    if 'quit_game' in result.get('visual_updates', []):
                        break
            
            # Only render if still running
            if not view.is_running():
                break
            
            # Get current game state
            game_state = game.get_game_state()
            
            # Render everything
            board = game.get_board()
            view.render_board(game_state, board)
            view.render_ui(game_state, game._player1, game._player2)
            
            # Show game over screen if needed
            if game.is_game_over():
                winner_name = game_state.winner.name if game_state.winner else None
                view.show_game_over(winner_name)
            
            # Update display
            view.update_display()
            
            frame_count += 1
            if frame_count % 60 == 0:  # Print every second
                print(f"Frame {frame_count}, Game running: {view.is_running()}")
            
            # Small delay to prevent excessive CPU usage
            import time
            time.sleep(0.016)  # ~60 FPS
    
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        view.quit()
        print("Game ended.")


if __name__ == "__main__":
    main()