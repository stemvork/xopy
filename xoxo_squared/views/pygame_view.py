"""
Pygame-based view for xoxo^2 game
"""

import pygame
import sys
from typing import List, Optional, Tuple
from ..models import GameState, Position, GameEvent, TileColor, TileShape, GamePhase


class PygameView:
    """Pygame-based graphical view for the xoxo^2 game"""
    
    # Color constants
    COLORS = {
        'background': (240, 240, 240),
        'grid_line': (100, 100, 100),
        'board_bg': (255, 255, 255),
        'red': (220, 50, 50),
        'green': (50, 180, 50),
        'highlight': (255, 235, 120),  # Desaturated yellow - more pleasant
        'text': (20, 20, 20),  # Much darker for better readability
        'text_light': (240, 240, 240),  # Light text for dark backgrounds
        'button': (200, 200, 200),
        'button_hover': (180, 180, 180),
        'button_text': (40, 40, 40),  # Dark text for buttons
        'panel_bg': (250, 250, 250),  # Slightly off-white for better contrast
    }
    
    def __init__(self, width: int = 1000, height: int = 1000):  # Increased default height
        """
        Initialize the pygame view
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        self.width = width
        self.height = height
        self.screen = None
        self.clock = None
        self.font = None
        self.title_font = None
        self.running = False
        
        # Responsive layout constants
        # Scale board size based on window size, but keep it reasonable
        max_board_size = min(width - 100, height - 400)  # Leave room for UI
        self.board_size = min(500, max(300, max_board_size))  # Between 300-500px
        self.board_x = (width - self.board_size) // 2
        self.board_y = 50  # Compact space at top for title
        self.cell_size = self.board_size // 4
        
        # UI areas with responsive spacing
        available_ui_height = height - (self.board_y + self.board_size) - 20
        self.info_panel_y = self.board_y + self.board_size + min(30, available_ui_height // 10)
        self.info_panel_height = height - self.info_panel_y - 20
        
        # Event tracking
        self.mouse_pos = (0, 0)
        self.highlighted_positions = []
        self.hovered_position = None
        
        # Click feedback
        self.click_feedback_timer = 0
        self.last_clicked_position = None
        
        # Error message display
        self.error_message = None
        self.error_timer = 0
        self.error_position = None
        self.error_type = "general"
        
        # Warning and info message display
        self.warning_message = None
        self.warning_timer = 0
        self.info_message = None
        self.info_timer = 0
        
        # Help and tooltip system
        self.show_help_overlay = False
        self.tooltip_message = None
        self.tooltip_position = None
        self.tooltip_timer = 0
        
        # Animation system
        self.animations = []
        self.animation_speed = 1.0
        self.animations_enabled = True  # Toggle for enabling/disabling animations
        
        # Load animation preference from simple settings
        self._load_animation_settings()
        
        # Performance optimization
        self.dirty_regions = []
        self.last_render_time = 0
        self.frame_skip_counter = 0
        
        # Restart confirmation
        self.restart_confirmation_timer = 0
        self.restart_confirmation_active = False
        
        # Cursor preview for tile placement
        self.show_cursor_preview = False
        self.cursor_preview_position = None
        self.cursor_preview_tile_data = None
        
        self._initialize_pygame()
    
    def _initialize_pygame(self) -> None:
        """Initialize pygame subsystems"""
        pygame.init()
        
        # Create display
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("xoxo² - Advanced Tic-Tac-Toe")
        
        # Initialize clock for frame rate control
        self.clock = pygame.time.Clock()
        
        # Initialize fonts
        try:
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 36)
        except pygame.error:
            # Fallback to default font
            self.font = pygame.font.SysFont('arial', 24)
            self.title_font = pygame.font.SysFont('arial', 36)
        
        self.running = True
    
    def handle_events(self) -> List[GameEvent]:
        """
        Handle pygame events and return game events
        
        Returns:
            List of GameEvent objects
        """
        events = []
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.append(GameEvent("quit"))
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    click_result = self._handle_mouse_click(event.pos)
                    if click_result:
                        events.append(click_result)
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                self._update_hover_state(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                
                # Handle special key combinations
                mods = pygame.key.get_pressed()
                if mods[pygame.K_LCTRL] or mods[pygame.K_RCTRL]:
                    if event.key == pygame.K_r:
                        key_name = "ctrl+r"
                    elif event.key == pygame.K_q:
                        key_name = "ctrl+q"
                    elif event.key == pygame.K_h:
                        key_name = "ctrl+h"
                elif mods[pygame.K_LSHIFT] or mods[pygame.K_RSHIFT]:
                    if event.key == pygame.K_r:
                        key_name = "shift+r"
                
                events.append(GameEvent("key", key=key_name))
        
        return events
    
    def _handle_mouse_click(self, click_pos: Tuple[int, int]) -> Optional[GameEvent]:
        """
        Handle mouse click and determine what was clicked
        
        Args:
            click_pos: Mouse click position (x, y)
            
        Returns:
            GameEvent if something was clicked, None otherwise
        """
        # Check for button clicks first (UI takes priority)
        button_clicked = self.check_button_clicks(click_pos)
        if button_clicked:
            return GameEvent("button_click", key=button_clicked)
        
        # Check for board position clicks
        board_pos = self._screen_to_board_position(click_pos)
        if board_pos:
            return GameEvent("click", position=board_pos)
        
        # Check for other UI element clicks
        ui_element = self._check_ui_element_click(click_pos)
        if ui_element:
            return GameEvent("ui_click", key=ui_element)
        
        return None
    
    def _update_hover_state(self, mouse_pos: Tuple[int, int]) -> None:
        """
        Update hover state for visual feedback
        
        Args:
            mouse_pos: Current mouse position
        """
        # Update hover state for board positions
        old_hovered = self.hovered_position
        self.hovered_position = self._screen_to_board_position(mouse_pos)
        
        # Add hover animation for new position (only if animations are enabled)
        if self.hovered_position and self.hovered_position != old_hovered and self.animations_enabled:
            self.add_tile_hover_animation(self.hovered_position)
        
        # Update cursor preview position
        self.update_cursor_preview_position(mouse_pos)
        
        # Update hover state for buttons (already handled by mouse_pos update)
        # Additional hover effects could be added here
    
    def _check_ui_element_click(self, click_pos: Tuple[int, int]) -> str:
        """
        Check if a UI element was clicked
        
        Args:
            click_pos: Mouse click position
            
        Returns:
            UI element name that was clicked, or empty string
        """
        # Check for player panel clicks
        if self._is_click_in_player_panel(click_pos, 1):
            return "player1_panel"
        elif self._is_click_in_player_panel(click_pos, 2):
            return "player2_panel"
        
        # Check for instructions panel click
        if self._is_click_in_instructions_panel(click_pos):
            return "instructions_panel"
        
        return ""
    
    def _is_click_in_player_panel(self, click_pos: Tuple[int, int], player_num: int) -> bool:
        """Check if click is in a player panel"""
        panel_width = 180
        panel_height = 100
        panel_y = self.info_panel_y
        
        if player_num == 1:
            panel_x = 400  # Updated to match new position
        else:
            panel_x = 600  # Updated to match new position
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        return panel_rect.collidepoint(click_pos)
    
    def _is_click_in_instructions_panel(self, click_pos: Tuple[int, int]) -> bool:
        """Check if click is in instructions panel"""
        panel_x = 30
        # Use same responsive logic as drawing
        available_space = self.height - self.info_panel_y - 40
        panel_y_offset = min(150, max(120, available_space // 2))
        panel_y = self.info_panel_y + panel_y_offset
        
        panel_width = min(800, self.width - 60)
        max_panel_height = self.height - panel_y - 20
        panel_height = min(160, max(80, max_panel_height))
        
        # Only check if panel is actually drawn
        if panel_height >= 80:
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            return panel_rect.collidepoint(click_pos)
        
        return False
    
    def render_board(self, game_state: GameState, board=None) -> None:
        """
        Render the game board with performance optimizations
        
        Args:
            game_state: Current game state to render
            board: Optional Board object to render tiles from
        """
        # Performance optimization: only clear screen if needed
        if not self.dirty_regions or len(self.animations) > 0:
            self.screen.fill(self.COLORS['background'])
        
        # Draw board background
        board_rect = pygame.Rect(self.board_x, self.board_y, self.board_size, self.board_size)
        pygame.draw.rect(self.screen, self.COLORS['board_bg'], board_rect)
        pygame.draw.rect(self.screen, self.COLORS['grid_line'], board_rect, 2)
        
        # Draw grid lines
        for i in range(1, 4):
            # Vertical lines
            x = self.board_x + i * self.cell_size
            pygame.draw.line(self.screen, self.COLORS['grid_line'], 
                           (x, self.board_y), (x, self.board_y + self.board_size), 1)
            
            # Horizontal lines
            y = self.board_y + i * self.cell_size
            pygame.draw.line(self.screen, self.COLORS['grid_line'], 
                           (self.board_x, y), (self.board_x + self.board_size, y), 1)
        
        # Draw position indicators
        self._draw_position_indicators()
        
        # Highlight valid positions
        self._draw_highlights()
        
        # Draw actual tiles from board
        if board:
            self._draw_board_tiles(board)
        else:
            # Draw placeholder tiles for testing
            self._draw_placeholder_tiles()
        
        # Render animations on top of board
        self._render_animations()
        
        # Render cursor preview on top of everything
        self._render_cursor_preview()
        
        # Clear dirty regions after rendering
        self.dirty_regions.clear()
    
    def render_ui(self, game_state: GameState, player1=None, player2=None) -> None:
        """
        Render the user interface elements
        
        Args:
            game_state: Current game state
            player1: Optional Player 1 object for tile counts
            player2: Optional Player 2 object for tile counts
        """
        # Draw title with enhanced styling
        self._draw_title()
        
        # Draw main game info panel
        self._draw_game_info_panel(game_state, player1, player2)
        
        # Draw player status panels
        self._draw_player_panels(game_state, player1, player2)
        
        # Draw control buttons
        self._draw_control_buttons(game_state)
        
        # Draw instructions panel
        self._draw_instructions_panel(game_state)
        
        # Draw error message if active
        self._draw_error_message()
        
        # Draw warning and info messages
        self._draw_warning_message()
        self._draw_info_message()
        
        # Draw tooltips
        self._draw_tooltip()
        
        # Draw help overlay if active
        if self.show_help_overlay:
            self._draw_help_overlay()
        
        # Draw restart confirmation if active
        if self.restart_confirmation_active:
            self._draw_restart_confirmation()
        
        # Render animations last (on top of everything)
        self._render_animations()
    
    def _draw_title(self) -> None:
        """Draw the game title with enhanced styling"""
        # Main title
        title_text = self.title_font.render("xoxo² - Advanced Tic-Tac-Toe", True, self.COLORS['text'])
        title_rect = title_text.get_rect(centerx=self.width // 2, y=10)
        
        # Add title background with better contrast
        title_bg = pygame.Rect(title_rect.x - 10, title_rect.y - 5, title_rect.width + 20, title_rect.height + 10)
        pygame.draw.rect(self.screen, self.COLORS['panel_bg'], title_bg)
        pygame.draw.rect(self.screen, self.COLORS['grid_line'], title_bg, 2)
        
        self.screen.blit(title_text, title_rect)
    
    def _draw_game_info_panel(self, game_state: GameState, player1=None, player2=None) -> None:
        """Draw the main game information panel"""
        panel_x = 30
        panel_y = self.info_panel_y
        panel_width = 350
        panel_height = 100  # Compact height to prevent overlap
        
        # Draw panel background with better contrast
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, self.COLORS['panel_bg'], panel_rect)
        pygame.draw.rect(self.screen, self.COLORS['grid_line'], panel_rect, 2)
        
        # Panel title
        panel_title = self.font.render("Game Status", True, self.COLORS['text'])
        self.screen.blit(panel_title, (panel_x + 15, panel_y + 15))
        
        info_y = panel_y + 35
        line_height = 20  # Compact line spacing
        
        # Current player with visual indicator
        try:
            player_shape = game_state.current_player.get_shape()
            current_shape = "◆" if player_shape and player_shape.value == "hexagon" else "★"
        except (AttributeError, TypeError):
            current_shape = "?"
        player_text = f"Current: {game_state.current_player.name} {current_shape}"  # Shorter text
        player_color = self.COLORS['red'] if game_state.current_player.name == "Player 1" else self.COLORS['green']
        player_surface = self.font.render(player_text, True, player_color)
        self.screen.blit(player_surface, (panel_x + 15, info_y))
        info_y += line_height
        
        # Game phase with description (compact)
        phase_descriptions = {
            'tile_placement': 'Place tile',
            'flip_selection': 'Select & flip',
            'move_selection': 'Move tile',
            'game_over': 'Game over'
        }
        try:
            phase_value = game_state.phase.value if game_state.phase else "unknown"
            phase_desc = phase_descriptions.get(phase_value, phase_value)
        except (AttributeError, TypeError):
            phase_desc = "unknown"
        phase_text = f"Phase: {phase_desc}"
        phase_surface = self.font.render(phase_text, True, self.COLORS['text'])
        self.screen.blit(phase_surface, (panel_x + 15, info_y))
        info_y += line_height
        
        # Move count
        move_text = f"Move: {game_state.move_count}"
        move_surface = self.font.render(move_text, True, self.COLORS['text'])
        self.screen.blit(move_surface, (panel_x + 15, info_y))
        info_y += line_height
        
        # Animation status indicator
        if not self.animations_enabled:
            anim_text = "Animations: OFF"
            anim_color = (150, 150, 150)  # Gray when disabled
        else:
            speed_text = "Fast" if self.animation_speed > 1.0 else "Normal"
            anim_text = f"Animations: {speed_text}"
            anim_color = self.COLORS['text']
        
        anim_surface = self.font.render(anim_text, True, anim_color)
        self.screen.blit(anim_surface, (panel_x + 15, info_y))
    
    def _draw_player_panels(self, game_state: GameState, player1=None, player2=None) -> None:
        """Draw individual player status panels"""
        panel_width = 180  # Slightly smaller to fit better
        panel_height = 100  # Reduced height
        panel_y = self.info_panel_y
        
        # Player 1 panel
        p1_panel_x = 400  # Moved right to prevent overlap
        p1_rect = pygame.Rect(p1_panel_x, panel_y, panel_width, panel_height)
        # Use lighter background with better contrast
        p1_color = (255, 220, 220) if game_state.current_player.name == "Player 1" else self.COLORS['panel_bg']
        pygame.draw.rect(self.screen, p1_color, p1_rect)
        pygame.draw.rect(self.screen, self.COLORS['red'] if game_state.current_player.name == "Player 1" else self.COLORS['grid_line'], 
                        p1_rect, 3 if game_state.current_player.name == "Player 1" else 1)
        
        # Player 1 info
        p1_title = self.font.render("Player 1 ◆", True, self.COLORS['text'])
        self.screen.blit(p1_title, (p1_panel_x + 10, panel_y + 10))
        
        if player1:
            p1_tiles = f"Tiles: {player1.get_tiles_remaining()}/8"
            p1_tiles_surface = self.font.render(p1_tiles, True, self.COLORS['text'])
            self.screen.blit(p1_tiles_surface, (p1_panel_x + 10, panel_y + 35))
            
            # Draw sample hexagon
            hex_center_x = p1_panel_x + panel_width - 30
            hex_center_y = panel_y + 30
            self._draw_hexagon(hex_center_x, hex_center_y, 15, self.COLORS['red'])
        
        # Player 2 panel
        p2_panel_x = 600  # Adjusted position
        p2_rect = pygame.Rect(p2_panel_x, panel_y, panel_width, panel_height)
        # Use lighter background with better contrast
        p2_color = (220, 255, 220) if game_state.current_player.name == "Player 2" else self.COLORS['panel_bg']
        pygame.draw.rect(self.screen, p2_color, p2_rect)
        pygame.draw.rect(self.screen, self.COLORS['green'] if game_state.current_player.name == "Player 2" else self.COLORS['grid_line'], 
                        p2_rect, 3 if game_state.current_player.name == "Player 2" else 1)
        
        # Player 2 info
        p2_title = self.font.render("Player 2 ★", True, self.COLORS['text'])
        self.screen.blit(p2_title, (p2_panel_x + 10, panel_y + 10))
        
        if player2:
            p2_tiles = f"Tiles: {player2.get_tiles_remaining()}/8"
            p2_tiles_surface = self.font.render(p2_tiles, True, self.COLORS['text'])
            self.screen.blit(p2_tiles_surface, (p2_panel_x + 10, panel_y + 35))
            
            # Draw sample star
            star_center_x = p2_panel_x + panel_width - 30
            star_center_y = panel_y + 30
            self._draw_star(star_center_x, star_center_y, 15, self.COLORS['green'])
    
    def _draw_control_buttons(self, game_state: GameState) -> None:
        """Draw control buttons"""
        # Position buttons below the player panels to avoid overlap
        button_y = self.info_panel_y + 110  # Below player panels (100px height + 10px margin)
        button_width = 80  # Compact size
        button_height = 25  # Slightly smaller height
        button_spacing = 10
        
        # Restart button - align with info panel
        restart_x = 30  # Align with info panel left edge
        restart_rect = pygame.Rect(restart_x, button_y, button_width, button_height)
        restart_color = self.COLORS['button_hover'] if self._is_mouse_over_rect(restart_rect) else self.COLORS['button']
        pygame.draw.rect(self.screen, restart_color, restart_rect)
        pygame.draw.rect(self.screen, self.COLORS['grid_line'], restart_rect, 2)
        
        restart_text = self.font.render("Restart", True, self.COLORS['button_text'])
        restart_text_rect = restart_text.get_rect(center=restart_rect.center)
        self.screen.blit(restart_text, restart_text_rect)
        
        # Store button rect for click detection
        self.restart_button_rect = restart_rect
        
        # Quit button
        quit_x = restart_x + button_width + button_spacing
        quit_rect = pygame.Rect(quit_x, button_y, button_width, button_height)
        quit_color = self.COLORS['button_hover'] if self._is_mouse_over_rect(quit_rect) else self.COLORS['button']
        pygame.draw.rect(self.screen, quit_color, quit_rect)
        pygame.draw.rect(self.screen, self.COLORS['grid_line'], quit_rect, 2)
        
        quit_text = self.font.render("Quit", True, self.COLORS['button_text'])
        quit_text_rect = quit_text.get_rect(center=quit_rect.center)
        self.screen.blit(quit_text, quit_text_rect)
        
        # Store button rect for click detection
        self.quit_button_rect = quit_rect
    
    def _draw_instructions_panel(self, game_state: GameState) -> None:
        """Draw context-sensitive instructions"""
        panel_x = 30
        # More responsive positioning based on available space
        available_space = self.height - self.info_panel_y - 40
        panel_y_offset = min(150, max(120, available_space // 2))
        panel_y = self.info_panel_y + panel_y_offset
        
        panel_width = min(800, self.width - 60)  # Responsive width
        # Ensure panel fits in remaining space
        max_panel_height = self.height - panel_y - 20
        panel_height = min(160, max(80, max_panel_height))  # At least 80px, up to 160px
        
        # Only draw if there's enough space
        if panel_height >= 80:
            # Draw panel background with better contrast
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(self.screen, self.COLORS['panel_bg'], panel_rect)
            pygame.draw.rect(self.screen, self.COLORS['grid_line'], panel_rect, 2)
        
            # Panel title
            instructions_title = self.font.render("Instructions", True, self.COLORS['text'])
            self.screen.blit(instructions_title, (panel_x + 15, panel_y + 15))
            
            # Context-sensitive instructions based on game phase
            instructions = self._get_phase_instructions(game_state)
            
            instruction_y = panel_y + 40
            line_height = 20  # Compact line height for smaller spaces
            max_lines = (panel_height - 50) // line_height  # How many lines fit
            
            for i, instruction in enumerate(instructions[:max_lines]):  # Limit to available space
                inst_surface = self.font.render(instruction, True, self.COLORS['text'])
                self.screen.blit(inst_surface, (panel_x + 15, instruction_y))
                instruction_y += line_height
    
    def _get_phase_instructions(self, game_state: GameState) -> list[str]:
        """Get context-sensitive instructions based on current game phase"""
        if game_state.phase == GamePhase.GAME_OVER:
            if game_state.winner:
                return [
                    f"🎉 {game_state.winner.name} wins!",
                    "• Press R to restart the game",
                    "• Press ESC to quit",
                    "• Press H for help and rules",
                    "• Great game! The winner achieved an unbreakable 3-in-a-row"
                ]
            else:
                return [
                    "🤝 Game ended in a draw!",
                    "• Board is full with no winner", 
                    "• Neither player could create an unbreakable 3-in-a-row",
                    "• Press R to restart the game", 
                    "• Press ESC to quit"
                ]
        
        elif game_state.phase == GamePhase.TILE_PLACEMENT:
            if game_state.move_count < 1:
                # First move only - just Player 1's first placement
                current_tiles = game_state.current_player.get_tiles_remaining() if hasattr(game_state.current_player, 'get_tiles_remaining') else 8
                return [
                    "🎯 First move: Place your tile strategically",
                    "• Click on any empty position to place a tile",
                    "• Your tile will be RED by default",
                    f"• {game_state.current_player.name} turn ({current_tiles} tiles remaining)",
                    "• Tip: Consider center positions for better control",
                    "• Next: All other turns will be flip-move-place!"
                ]
            else:
                # Regular placement after flip-move with resource awareness
                current_tiles = game_state.current_player.get_tiles_remaining() if hasattr(game_state.current_player, 'get_tiles_remaining') else "?"
                if current_tiles == 0:
                    return [
                        "🎯 No tiles to place - turn will end",
                        "• You're out of tiles to place",
                        "• Future turns: flip and move only",
                        "• Focus on disrupting opponent's plans",
                        "• Look for defensive opportunities"
                    ]
                else:
                    return [
                        "🎯 Place your new tile strategically",
                        "• Click on any empty position",
                        "• Complete your flip-move-place sequence",
                        f"• {current_tiles} tiles remaining",
                        "• Press 'C' to change tile color (red/green)",
                        "• Try to form 3 in a row of the same color",
                        "• Consider both offensive and defensive positioning"
                    ]
        
        elif game_state.phase == GamePhase.FLIP_SELECTION:
            # Enhanced flip selection guidance
            return [
                "🔄 Select a tile to flip and move",
                "• Click on any highlighted tile (yellow border)",
                "• Only tiles that can move are highlighted",
                "• Flipping changes the tile's color (red ↔ green)",
                "• Tiles need adjacent empty spaces to be movable",
                "• Strategy: Disrupt opponent or create opportunities",
                "• Remember: You'll move it next, then place a new tile"
            ]
        
        elif game_state.phase == GamePhase.MOVE_SELECTION:
            # Enhanced move selection guidance
            return [
                "➡️ Choose where to move the flipped tile",
                "• Click on a highlighted adjacent position",
                "• Only orthogonal moves allowed (up/down/left/right)",
                "• No diagonal moves permitted",
                "• Destination must be empty",
                "• Consider the impact on board control",
                "• Next: Place your new tile (if you have tiles remaining)"
            ]
        
        else:
            return [
                "🎮 xoxo² - Advanced Tic-Tac-Toe",
                "• Goal: Get 3 tiles of the same COLOR in a row",
                "• Challenge: Opponent can break it by flipping tiles!",
                "• Victory: Win only if opponent can't break your 3-in-a-row",
                "• Each player has 8 tiles and unique shapes",
                "• Press H for detailed rules and strategy tips"
            ]
    
    def _is_mouse_over_rect(self, rect: pygame.Rect) -> bool:
        """Check if mouse is over a rectangle"""
        return rect.collidepoint(self.mouse_pos)
    
    def check_button_clicks(self, click_pos: tuple[int, int]) -> str:
        """
        Check if a button was clicked
        
        Args:
            click_pos: Mouse click position
            
        Returns:
            Button name that was clicked, or empty string
        """
        if hasattr(self, 'restart_button_rect') and self.restart_button_rect.collidepoint(click_pos):
            return "restart"
        elif hasattr(self, 'quit_button_rect') and self.quit_button_rect.collidepoint(click_pos):
            return "quit"
        return ""
    
    def add_click_feedback(self, position: Position) -> None:
        """
        Add visual feedback for a clicked position
        
        Args:
            position: Board position that was clicked
        """
        self.last_clicked_position = position
        self.click_feedback_timer = 30  # 30 frames of feedback
        
    def show_invalid_move_feedback(self, position: Position) -> None:
        """
        Show visual feedback for an invalid move
        
        Args:
            position: Board position where invalid move was attempted
        """
        self.last_clicked_position = position
        self.click_feedback_timer = 15  # 15 frames of error feedback
        
    def show_error_message(self, message: str, position: Optional[Position] = None, error_type: str = "general") -> None:
        """
        Show error message on screen with enhanced feedback
        
        Args:
            message: Error message to display
            position: Optional position to highlight as error source
            error_type: Type of error for different visual styling
        """
        # Store error message for rendering
        self.error_message = message
        self.error_timer = 240  # 4 seconds at 60 FPS for better readability
        self.error_type = error_type
        
        # Highlight position if provided
        if position:
            self.error_position = position
            
        # Add sound feedback if available (placeholder for future enhancement)
        # self._play_error_sound()
    
    def show_warning_message(self, message: str, duration: int = 120) -> None:
        """
        Show warning message (less severe than error)
        
        Args:
            message: Warning message to display
            duration: Duration in frames (default 2 seconds)
        """
        self.warning_message = message
        self.warning_timer = duration
    
    def show_info_message(self, message: str, duration: int = 180) -> None:
        """
        Show informational message
        
        Args:
            message: Info message to display
            duration: Duration in frames (default 3 seconds)
        """
        self.info_message = message
        self.info_timer = duration
    
    def show_constraint_violation(self, constraint: str, position: Optional[Position] = None) -> None:
        """
        Show specific constraint violation message with enhanced feedback
        
        Args:
            constraint: Type of constraint violated
            position: Position where violation occurred
        """
        constraint_messages = {
            'occupied_position': '❌ Position is already occupied by another tile',
            'no_valid_moves': '🚫 Selected tile cannot be moved (no adjacent empty spaces)',
            'invalid_move_direction': '↔️ Only orthogonal moves allowed (up/down/left/right)',
            'out_of_tiles': '📦 No tiles remaining - you can only flip and move existing tiles',
            'empty_position_flip': '🔄 Cannot flip an empty position - select a tile',
            'game_over': '🏁 Game is over - press R to restart',
            'invalid_phase': '⚠️ Action not allowed in current game phase',
            'board_full': '🔲 Board is full - no more tiles can be placed',
            'no_tiles_to_flip': '🚫 No tiles available to flip and move',
            'invalid_sequence': '🔄 Must complete flip-move-place sequence in order'
        }
        
        message = constraint_messages.get(constraint, f'❓ Constraint violation: {constraint}')
        
        # Add helpful guidance based on constraint type
        guidance = self._get_constraint_guidance(constraint)
        if guidance:
            message += f"\n💡 {guidance}"
        
        self.show_error_message(message, position, "constraint")
        
        # Add position-specific visual feedback
        if position:
            self._add_constraint_visual_feedback(constraint, position)
    
    def _get_constraint_guidance(self, constraint: str) -> str:
        """Get helpful guidance for specific constraint violations"""
        guidance_map = {
            'occupied_position': 'Try clicking on an empty (highlighted) position',
            'no_valid_moves': 'Look for tiles with yellow highlights - they can be moved',
            'invalid_move_direction': 'Only up, down, left, right moves allowed - no diagonal',
            'out_of_tiles': 'Focus on strategic flipping to disrupt opponent plans',
            'empty_position_flip': 'Click on a tile (not empty space) to flip it',
            'game_over': 'Start a new game to continue playing',
            'invalid_phase': 'Follow the highlighted positions for valid moves',
            'board_full': 'Game will end soon - focus on winning moves',
            'no_tiles_to_flip': 'This may indicate a draw condition',
            'invalid_sequence': 'Complete current phase before proceeding'
        }
        return guidance_map.get(constraint, '')
    
    def _add_constraint_visual_feedback(self, constraint: str, position: Position) -> None:
        """Add visual feedback specific to constraint type"""
        if constraint == 'occupied_position':
            # Show occupied position with different styling
            self.error_position = position
        elif constraint == 'no_valid_moves':
            # Could highlight the tile that can't be moved
            self.error_position = position
        elif constraint == 'invalid_move_direction':
            # Could show valid directions from the position
            self.error_position = position
    
    def get_detailed_click_info(self, click_pos: tuple[int, int]) -> dict:
        """
        Get detailed information about what was clicked
        
        Args:
            click_pos: Mouse click position
            
        Returns:
            Dictionary with click information
        """
        info = {
            'type': 'none',
            'position': None,
            'button': None,
            'ui_element': None,
            'coordinates': click_pos
        }
        
        # Check buttons
        button = self.check_button_clicks(click_pos)
        if button:
            info['type'] = 'button'
            info['button'] = button
            return info
        
        # Check board position
        board_pos = self._screen_to_board_position(click_pos)
        if board_pos:
            info['type'] = 'board'
            info['position'] = board_pos
            return info
        
        # Check UI elements
        ui_element = self._check_ui_element_click(click_pos)
        if ui_element:
            info['type'] = 'ui'
            info['ui_element'] = ui_element
            return info
        
        return info
    
    def is_position_clickable(self, position: Position, valid_positions: List[Position]) -> bool:
        """
        Check if a board position is clickable given the current valid positions
        
        Args:
            position: Position to check
            valid_positions: List of currently valid positions
            
        Returns:
            True if position is clickable
        """
        return position in valid_positions
    
    def get_click_precision_info(self, click_pos: tuple[int, int]) -> dict:
        """
        Get precision information about a click for debugging/analytics
        
        Args:
            click_pos: Mouse click position
            
        Returns:
            Dictionary with precision information
        """
        board_pos = self._screen_to_board_position(click_pos)
        
        info = {
            'screen_pos': click_pos,
            'board_pos': board_pos,
            'precision': 'outside_board'
        }
        
        if board_pos:
            # Calculate how close to center of cell the click was
            center_x, center_y = self._board_position_to_screen(board_pos)
            distance_from_center = ((click_pos[0] - center_x) ** 2 + (click_pos[1] - center_y) ** 2) ** 0.5
            
            # Categorize precision
            if distance_from_center < self.cell_size * 0.2:
                info['precision'] = 'center'
            elif distance_from_center < self.cell_size * 0.4:
                info['precision'] = 'good'
            else:
                info['precision'] = 'edge'
            
            info['distance_from_center'] = distance_from_center
            info['cell_center'] = (center_x, center_y)
        
        return info
    
    def highlight_valid_moves(self, positions: List[Position]) -> None:
        """
        Set positions to highlight on the board
        
        Args:
            positions: List of positions to highlight
        """
        self.highlighted_positions = positions.copy()
        
    def highlight_flip_candidates(self, positions: List[Position]) -> None:
        """
        Highlight tiles that can be flipped during flip selection phase
        
        Args:
            positions: List of positions with tiles that can be flipped
        """
        self.highlighted_positions = positions.copy()
        
    def highlight_move_destinations(self, positions: List[Position]) -> None:
        """
        Highlight valid move destinations during move selection phase
        
        Args:
            positions: List of valid destination positions
        """
        self.highlighted_positions = positions.copy()
        
    def highlight_empty_positions(self, positions: List[Position]) -> None:
        """
        Highlight empty positions for tile placement
        
        Args:
            positions: List of empty positions
        """
        self.highlighted_positions = positions.copy()
    
    def show_game_over(self, winner: Optional[str]) -> None:
        """
        Show game over screen
        
        Args:
            winner: Name of winner, or None for draw
        """
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over message
        if winner:
            message = f"{winner} Wins!"
            color = self.COLORS['red']
        else:
            message = "Draw!"
            color = self.COLORS['text']
        
        # Render message
        message_surface = self.title_font.render(message, True, color)
        message_rect = message_surface.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(message_surface, message_rect)
        
        # Instructions
        restart_text = "Press R to restart or ESC to quit"
        restart_surface = self.font.render(restart_text, True, self.COLORS['text'])
        restart_rect = restart_surface.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(restart_surface, restart_rect)
    
    def _draw_error_message(self) -> None:
        """Draw error message if active with enhanced styling"""
        if self.error_message and self.error_timer > 0:
            # Determine colors based on error type
            if self.error_type == "constraint":
                bg_color = (255, 120, 120)  # Light red for constraints
                border_color = (200, 50, 50)
                icon = "⚠️"
            elif self.error_type == "resource":
                bg_color = (255, 180, 100)  # Orange for resource issues
                border_color = (200, 120, 50)
                icon = "📦"
            else:
                bg_color = (255, 100, 100)  # Default red
                border_color = (200, 50, 50)
                icon = "❌"
            
            # Create error message background with dynamic sizing
            lines = self._wrap_text(self.error_message, 50)  # Wrap long messages
            line_height = 25
            error_bg_width = min(500, max(300, len(max(lines, key=len)) * 8 + 60))
            error_bg_height = max(60, len(lines) * line_height + 20)
            error_bg_x = (self.width - error_bg_width) // 2
            error_bg_y = self.board_y + self.board_size + 10
            
            # Draw semi-transparent background with fade effect
            alpha = min(255, self.error_timer * 2)  # Fade in effect
            error_bg = pygame.Surface((error_bg_width, error_bg_height))
            error_bg.set_alpha(alpha)
            error_bg.fill(bg_color)
            self.screen.blit(error_bg, (error_bg_x, error_bg_y))
            
            # Draw border with pulsing effect
            border_width = 2 + int(abs(pygame.time.get_ticks() / 200) % 2)
            error_rect = pygame.Rect(error_bg_x, error_bg_y, error_bg_width, error_bg_height)
            pygame.draw.rect(self.screen, border_color, error_rect, border_width)
            
            # Draw icon and error text
            icon_surface = self.font.render(icon, True, self.COLORS['text_light'])
            self.screen.blit(icon_surface, (error_bg_x + 10, error_bg_y + 10))
            
            # Draw wrapped text lines
            text_x = error_bg_x + 40
            text_y = error_bg_y + 10
            for line in lines:
                error_surface = self.font.render(line, True, self.COLORS['text_light'])
                self.screen.blit(error_surface, (text_x, text_y))
                text_y += line_height
            
            # Highlight error position on board if provided
            if self.error_position:
                self._highlight_error_position(self.error_position)
    
    def _draw_warning_message(self) -> None:
        """Draw warning message if active"""
        if self.warning_message and self.warning_timer > 0:
            # Position warning below error message
            warning_bg_width = 350
            warning_bg_height = 40
            warning_bg_x = (self.width - warning_bg_width) // 2
            warning_bg_y = self.board_y + self.board_size + 80
            
            # Draw semi-transparent background
            warning_bg = pygame.Surface((warning_bg_width, warning_bg_height))
            warning_bg.set_alpha(180)
            warning_bg.fill((255, 200, 100))  # Orange background
            self.screen.blit(warning_bg, (warning_bg_x, warning_bg_y))
            
            # Draw border
            warning_rect = pygame.Rect(warning_bg_x, warning_bg_y, warning_bg_width, warning_bg_height)
            pygame.draw.rect(self.screen, (200, 150, 50), warning_rect, 2)
            
            # Draw warning text with icon
            warning_text = f"⚠️ {self.warning_message}"
            warning_surface = self.font.render(warning_text, True, (100, 50, 0))
            warning_text_rect = warning_surface.get_rect(center=(warning_bg_x + warning_bg_width // 2, warning_bg_y + warning_bg_height // 2))
            self.screen.blit(warning_surface, warning_text_rect)
    
    def _draw_info_message(self) -> None:
        """Draw info message if active"""
        if self.info_message and self.info_timer > 0:
            # Position info message at top of screen
            info_bg_width = 400
            info_bg_height = 35
            info_bg_x = (self.width - info_bg_width) // 2
            info_bg_y = 5
            
            # Draw semi-transparent background
            info_bg = pygame.Surface((info_bg_width, info_bg_height))
            info_bg.set_alpha(160)
            info_bg.fill((100, 150, 255))  # Blue background
            self.screen.blit(info_bg, (info_bg_x, info_bg_y))
            
            # Draw border
            info_rect = pygame.Rect(info_bg_x, info_bg_y, info_bg_width, info_bg_height)
            pygame.draw.rect(self.screen, (50, 100, 200), info_rect, 1)
            
            # Draw info text with icon
            info_text = f"ℹ️ {self.info_message}"
            info_surface = self.font.render(info_text, True, self.COLORS['text_light'])
            info_text_rect = info_surface.get_rect(center=(info_bg_x + info_bg_width // 2, info_bg_y + info_bg_height // 2))
            self.screen.blit(info_surface, info_text_rect)
    
    def _draw_tooltip(self) -> None:
        """Draw tooltip if active"""
        if self.tooltip_message and self.tooltip_timer > 0 and self.tooltip_position:
            # Calculate tooltip position near mouse
            tooltip_width = len(self.tooltip_message) * 8 + 20
            tooltip_height = 30
            tooltip_x = min(self.tooltip_position[0] + 10, self.width - tooltip_width - 10)
            tooltip_y = max(10, self.tooltip_position[1] - tooltip_height - 10)
            
            # Draw semi-transparent background
            tooltip_bg = pygame.Surface((tooltip_width, tooltip_height))
            tooltip_bg.set_alpha(200)
            tooltip_bg.fill((50, 50, 50))  # Dark background
            self.screen.blit(tooltip_bg, (tooltip_x, tooltip_y))
            
            # Draw border
            tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
            pygame.draw.rect(self.screen, (150, 150, 150), tooltip_rect, 1)
            
            # Draw tooltip text
            tooltip_surface = self.font.render(self.tooltip_message, True, self.COLORS['text_light'])
            tooltip_text_rect = tooltip_surface.get_rect(center=(tooltip_x + tooltip_width // 2, tooltip_y + tooltip_height // 2))
            self.screen.blit(tooltip_surface, tooltip_text_rect)
    
    def _highlight_error_position(self, position: Position) -> None:
        """Highlight a position with error styling"""
        center_x, center_y = self._board_position_to_screen(position)
        
        # Draw pulsing red circle around the error position
        pulse_radius = 30 + int(5 * abs(pygame.time.get_ticks() / 100) % 2)
        pygame.draw.circle(self.screen, (255, 50, 50), (center_x, center_y), pulse_radius, 3)
        
        # Draw X mark over the position
        x_size = 20
        pygame.draw.line(self.screen, (255, 0, 0), 
                        (center_x - x_size, center_y - x_size), 
                        (center_x + x_size, center_y + x_size), 4)
        pygame.draw.line(self.screen, (255, 0, 0), 
                        (center_x + x_size, center_y - x_size), 
                        (center_x - x_size, center_y + x_size), 4)
    
    def _wrap_text(self, text: str, max_chars: int) -> List[str]:
        """Wrap text to multiple lines"""
        if len(text) <= max_chars:
            return [text]
        
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_chars:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _draw_help_overlay(self) -> None:
        """Draw comprehensive help overlay"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Help panel dimensions
        panel_width = 600
        panel_height = 500
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        
        # Draw help panel background
        help_bg = pygame.Surface((panel_width, panel_height))
        help_bg.fill((240, 240, 240))
        self.screen.blit(help_bg, (panel_x, panel_y))
        
        # Draw border
        help_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (100, 100, 100), help_rect, 3)
        
        # Title
        title_text = self.title_font.render("xoxo² Game Rules & Controls", True, (50, 50, 50))
        title_rect = title_text.get_rect(centerx=panel_x + panel_width // 2, y=panel_y + 20)
        self.screen.blit(title_text, title_rect)
        
        # Help content with enhanced information
        help_content = [
            "",
            "🎯 OBJECTIVE:",
            "Get 3 tiles of the same COLOR in a row (horizontal, vertical, or diagonal)",
            "But your opponent can break it by flipping tiles on their turn!",
            "You win only if opponent can't break your 3-in-a-row on their next turn.",
            "",
            "🎮 HOW TO PLAY:",
            "• First moves: Just place your tiles anywhere (they start RED)",
            "• Regular turns follow: Flip → Move → Place sequence",
            "  1. Select a tile to flip (changes color: red ↔ green)",
            "  2. Move it orthogonally (up/down/left/right only - no diagonal)",
            "  3. Place your new tile on any empty space",
            "",
            "📦 RESOURCES & CONSTRAINTS:",
            "• Each player starts with 8 tiles total",
            "• Player 1 uses hexagons ◆, Player 2 uses stars ★",
            "• When out of tiles, you can only flip and move existing ones",
            "• Only tiles with adjacent empty spaces can be flipped",
            "• Movement is restricted to orthogonal directions only",
            "",
            "🧠 STRATEGY TIPS:",
            "• Focus on COLOR matching, not player shapes for winning",
            "• Plan defensive moves to prevent opponent victories",
            "• Control the center for better positioning options",
            "• Save tiles for critical late-game situations",
            "",
            "⌨️ CONTROLS:",
            "• Click board positions to make moves",
            "• R = Restart (with confirmation)  • Shift+R = Force restart",
            "• Ctrl+R = Quick restart  • Ctrl+Q = Quick quit",
            "• ESC = Cancel/Quit  • H/F1 = Toggle help  • Space = Context help",
            "• Tab = Game statistics  • A = Toggle animations  • S = Animation speed",
            "• Hover over positions for context-sensitive tooltips",
            "",
            "❗ COMMON MISTAKES:",
            "• Trying to move diagonally (not allowed)",
            "• Forgetting that winning is based on COLOR, not shape",
            "• Not considering opponent's ability to break 3-in-a-row",
            "",
            "Press H or ESC to close this help"
        ]
        
        # Draw help content
        content_y = panel_y + 60
        line_height = 20
        
        for line in help_content:
            if line.startswith("🎯") or line.startswith("🎮") or line.startswith("📦") or line.startswith("⌨️"):
                # Section headers
                text_surface = self.font.render(line, True, (100, 50, 150))
            elif line.startswith("•"):
                # Bullet points
                text_surface = self.font.render(line, True, (50, 50, 50))
            elif line.startswith("  "):
                # Sub-points
                text_surface = self.font.render(line, True, (80, 80, 80))
            else:
                # Regular text
                text_surface = self.font.render(line, True, (50, 50, 50))
            
            self.screen.blit(text_surface, (panel_x + 20, content_y))
            content_y += line_height
    
    def toggle_help_overlay(self) -> None:
        """Toggle the help overlay on/off"""
        self.show_help_overlay = not self.show_help_overlay
        
        # Show info message about help toggle
        if self.show_help_overlay:
            self.show_info_message("Help overlay shown - Press H or ESC to close", 120)
        else:
            self.show_info_message("Help overlay hidden", 60)
    
    def show_tooltip(self, message: str, position: tuple[int, int], duration: int = 120) -> None:
        """
        Show tooltip at specific position
        
        Args:
            message: Tooltip message
            position: Screen position (x, y)
            duration: Duration in frames
        """
        self.tooltip_message = message
        self.tooltip_position = position
        self.tooltip_timer = duration
    
    def get_position_tooltip(self, position: Position, game_state, board=None) -> str:
        """
        Get context-sensitive tooltip for a board position
        
        Args:
            position: Board position
            game_state: Current game state
            board: Optional board to check tile information
            
        Returns:
            Tooltip message for the position
        """
        # Get basic position info
        pos_text = f"Position ({position.row},{position.col})"
        
        # Add phase-specific information
        try:
            phase_value = game_state.phase.value if game_state.phase else "unknown"
        except (AttributeError, TypeError):
            phase_value = "unknown"
        
        if phase_value == "tile_placement":
            if board and board.is_position_empty(position):
                return f"{pos_text}: Click to place your tile here"
            else:
                return f"{pos_text}: Occupied - cannot place tile"
        
        elif phase_value == "flip_selection":
            if board and not board.is_position_empty(position):
                tile = board.get_tile(position)
                if tile:
                    try:
                        current_color = tile.get_current_color().value if tile.get_current_color() else "unknown"
                        shape = tile.get_shape().value if tile.get_shape() else "unknown"
                        owner = tile.get_owner().name if tile.get_owner() else "unknown"
                        return f"{pos_text}: {owner}'s {current_color} {shape} - click to flip and move"
                    except (AttributeError, TypeError):
                        return f"{pos_text}: Click to flip this tile"
                else:
                    return f"{pos_text}: Click to flip this tile"
            else:
                return f"{pos_text}: Empty - select a tile to flip"
        
        elif phase_value == "move_selection":
            if board and board.is_position_empty(position):
                return f"{pos_text}: Click to move selected tile here"
            else:
                return f"{pos_text}: Occupied - cannot move tile here"
        
        elif game_state.phase.value == "game_over":
            return f"{pos_text}: Game over - press R to restart"
        
        else:
            return pos_text
    
    def show_edge_case_guidance(self, case_type: str, additional_info: dict = None) -> None:
        """
        Show guidance for specific edge cases
        
        Args:
            case_type: Type of edge case
            additional_info: Additional information about the edge case
        """
        edge_case_messages = {
            'no_valid_moves': {
                'message': 'No valid moves available!',
                'guidance': 'This may indicate a stalemate condition. Game may end in draw.',
                'type': 'warning'
            },
            'low_tiles': {
                'message': 'Running low on tiles!',
                'guidance': 'Plan carefully - you\'ll only be able to flip and move soon.',
                'type': 'warning'
            },
            'board_nearly_full': {
                'message': 'Board is nearly full!',
                'guidance': 'Game will end soon. Focus on winning moves or blocking opponent.',
                'type': 'info'
            },
            'forced_move': {
                'message': 'Only one move possible!',
                'guidance': 'The highlighted position is your only option.',
                'type': 'info'
            },
            'potential_win': {
                'message': 'Potential winning opportunity!',
                'guidance': 'Look for ways to create unbreakable three-in-a-row.',
                'type': 'info'
            },
            'opponent_threat': {
                'message': 'Opponent has a threat!',
                'guidance': 'Consider defensive moves to prevent opponent victory.',
                'type': 'warning'
            }
        }
        
        case_info = edge_case_messages.get(case_type, {
            'message': f'Edge case: {case_type}',
            'guidance': 'Unusual game state detected.',
            'type': 'info'
        })
        
        # Add additional info if provided
        if additional_info:
            if 'tiles_remaining' in additional_info:
                case_info['message'] += f" ({additional_info['tiles_remaining']} tiles left)"
            if 'positions_available' in additional_info:
                case_info['message'] += f" ({additional_info['positions_available']} positions available)"
        
        # Show appropriate message type
        full_message = f"{case_info['message']}\n💡 {case_info['guidance']}"
        
        if case_info['type'] == 'warning':
            self.show_warning_message(full_message, 180)  # 3 seconds
        else:
            self.show_info_message(full_message, 150)  # 2.5 seconds
    
    def show_move_constraints(self, constraints: List[str], position: Optional[Position] = None) -> None:
        """
        Show information about current move constraints
        
        Args:
            constraints: List of constraint descriptions
            position: Optional position related to constraints
        """
        if not constraints:
            return
        
        constraint_text = "Move constraints:\n" + "\n".join(f"• {c}" for c in constraints)
        self.show_info_message(constraint_text, 200)  # 3.3 seconds
        
        if position:
            # Show tooltip at position
            self.show_tooltip("Constraints apply here", self._board_position_to_screen(position), 120)
    
    def show_rule_explanation(self, rule_type: str) -> None:
        """
        Show explanation of specific game rules
        
        Args:
            rule_type: Type of rule to explain
        """
        rule_explanations = {
            'three_in_row': 'Win by getting 3 tiles of the same COLOR in a row, but only if opponent can\'t break it!',
            'flip_move_place': 'Regular turns: 1) Flip a tile (changes color), 2) Move it orthogonally, 3) Place new tile',
            'orthogonal_only': 'Tiles can only move up, down, left, or right - no diagonal moves allowed',
            'color_matching': 'Win condition is based on COLOR (red/green), not player shapes',
            'survivability': 'You only win if opponent cannot break your three-in-a-row on their next turn',
            'resource_management': 'Each player has 8 tiles. When out, you can only flip and move existing tiles',
            'first_moves': 'First two moves are placement only - no flipping or moving yet'
        }
        
        explanation = rule_explanations.get(rule_type, f'Rule explanation for {rule_type} not available')
        self.show_info_message(f"📖 Rule: {explanation}", 240)  # 4 seconds
    
    def show_strategic_tip(self, tip_type: str, context: dict = None) -> None:
        """
        Show strategic tips based on game state
        
        Args:
            tip_type: Type of strategic tip
            context: Additional context information
        """
        tips = {
            'opening_strategy': '🎯 Tip: Control the center positions early for better board control',
            'defensive_play': '🛡️ Tip: Watch for opponent\'s potential three-in-a-row formations',
            'resource_conservation': '💰 Tip: Save tiles for critical moments - you only have 8!',
            'color_awareness': '🎨 Tip: Remember, wins are based on COLOR, not player shapes',
            'movement_planning': '🗺️ Tip: Plan your flip-move sequence to create opportunities',
            'endgame_tactics': '⚡ Tip: Focus on creating unbreakable three-in-a-row formations'
        }
        
        tip = tips.get(tip_type, f'Strategic tip for {tip_type} not available')
        
        # Add context-specific information
        if context:
            if tip_type == 'resource_conservation' and 'tiles_remaining' in context:
                tip += f" (You have {context['tiles_remaining']} tiles left)"
            elif tip_type == 'defensive_play' and 'threat_positions' in context:
                tip += f" (Watch positions: {context['threat_positions']})"
        
        self.show_info_message(tip, 200)  # 3.3 seconds
    
    def show_restart_confirmation(self) -> None:
        """Show restart confirmation dialog"""
        self.restart_confirmation_active = True
        self.restart_confirmation_timer = 300  # 5 seconds
    
    def hide_restart_confirmation(self) -> None:
        """Hide restart confirmation dialog"""
        self.restart_confirmation_active = False
        self.restart_confirmation_timer = 0
    
    def _draw_restart_confirmation(self) -> None:
        """Draw restart confirmation dialog"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Confirmation dialog dimensions
        dialog_width = 400
        dialog_height = 200
        dialog_x = (self.width - dialog_width) // 2
        dialog_y = (self.height - dialog_height) // 2
        
        # Draw dialog background with pulsing effect
        pulse_alpha = int(240 + 15 * abs(pygame.time.get_ticks() / 300) % 2)
        dialog_bg = pygame.Surface((dialog_width, dialog_height))
        dialog_bg.set_alpha(pulse_alpha)
        dialog_bg.fill((240, 240, 240))
        self.screen.blit(dialog_bg, (dialog_x, dialog_y))
        
        # Draw border with warning color
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, (200, 50, 50), dialog_rect, 3)
        
        # Title with warning icon
        title_text = self.title_font.render("⚠️ Restart Game?", True, (200, 50, 50))
        title_rect = title_text.get_rect(centerx=dialog_x + dialog_width // 2, y=dialog_y + 30)
        self.screen.blit(title_text, title_rect)
        
        # Message lines
        message_lines = [
            "Are you sure you want to restart?",
            "This will reset the current game.",
            "",
            "🔄 Press R again to confirm",
            "❌ Press ESC to cancel"
        ]
        
        message_y = dialog_y + 80
        for line in message_lines:
            if line:
                color = (200, 50, 50) if line.startswith("🔄") else (50, 50, 50)
                message_surface = self.font.render(line, True, color)
                message_rect = message_surface.get_rect(centerx=dialog_x + dialog_width // 2, y=message_y)
                self.screen.blit(message_surface, message_rect)
            message_y += 25
        
        # Show timeout countdown
        timeout_seconds = max(0, self.restart_confirmation_timer // 60)
        if timeout_seconds > 0:
            timeout_text = f"Auto-cancel in {timeout_seconds}s"
            timeout_surface = self.font.render(timeout_text, True, (100, 100, 100))
            timeout_rect = timeout_surface.get_rect(centerx=dialog_x + dialog_width // 2, y=dialog_y + dialog_height - 25)
            self.screen.blit(timeout_surface, timeout_rect)
    
    def show_contextual_help(self, game_state, board) -> None:
        """Show contextual help based on current game state"""
        phase = game_state.phase
        current_player = game_state.current_player
        
        if phase.value == 'flip_selection':
            help_text = f"🔄 {current_player.name}'s turn: Select a tile to flip and move"
        elif phase.value == 'move_selection':
            help_text = f"➡️ {current_player.name}: Choose where to move the flipped tile"
        elif phase.value == 'tile_placement':
            tiles_left = current_player.get_tiles_remaining() if hasattr(current_player, 'get_tiles_remaining') else "?"
            help_text = f"🎯 {current_player.name}: Place your tile ({tiles_left} remaining)"
        elif phase.value == 'game_over':
            winner = game_state.winner
            if winner:
                help_text = f"🎉 {winner.name} wins! Press R to restart"
            else:
                help_text = "🤝 Draw! Press R to restart"
        else:
            help_text = "🎮 xoxo² - Advanced Tic-Tac-Toe"
        
        self.show_info_message(help_text, 180)
    
    def show_rule_explanation(self, rule_type: str) -> None:
        """Show explanation for specific game rules"""
        explanations = {
            'flip_move_place': "Each turn: 1) Flip a tile, 2) Move it orthogonally, 3) Place new tile",
            'orthogonal_only': "Movement is restricted to up/down/left/right only - no diagonal moves",
            'resource_management': "Each player has 8 tiles total - plan your placements carefully",
            'first_moves': "Early game: Focus on controlling center positions for better mobility",
            'three_in_row': "Win by getting 3 tiles of same COLOR in a row that opponent can't break"
        }
        
        message = explanations.get(rule_type, f"Rule explanation for {rule_type}")
        self.show_info_message(f"💡 {message}", 240)
    
    def show_move_constraints(self, constraints: list, position=None) -> None:
        """Show current move constraints to help player understand valid moves"""
        if not constraints:
            return
        
        constraint_text = "⚠️ Move constraints: " + " • ".join(constraints)
        self.show_warning_message(constraint_text, 180)
    
    def get_position_tooltip(self, position: Position, game_state, board=None) -> str:
        """
        Get tooltip text for a specific board position
        
        Args:
            position: Board position
            game_state: Current game state
            board: Optional board object
            
        Returns:
            Tooltip text for the position
        """
        pos_text = f"Position ({position.row},{position.col})"
        
        if board and not board.is_position_empty(position):
            tile = board.get_tile(position)
            if tile:
                shape = tile.get_shape().value
                color = tile.get_current_color().value
                owner = tile.get_owner().name
                return f"{pos_text}: {owner}'s {color} {shape}"
        
        if game_state.phase.value == "tile_placement":
            return f"{pos_text}: Click to place tile"
        elif game_state.phase.value == "flip_selection":
            return f"{pos_text}: Click to flip and move tile"
        elif game_state.phase.value == "move_selection":
            return f"{pos_text}: Click to move flipped tile here"
        elif game_state.phase.value == "game_over":
            return f"{pos_text}: Game over - press R to restart"
        else:
            return pos_text
    
    def _draw_restart_confirmation(self) -> None:
        """Draw restart confirmation dialog"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Dialog dimensions
        dialog_width = 400
        dialog_height = 200
        dialog_x = (self.width - dialog_width) // 2
        dialog_y = (self.height - dialog_height) // 2
        
        # Draw dialog background
        dialog_bg = pygame.Surface((dialog_width, dialog_height))
        dialog_bg.fill((240, 240, 240))
        self.screen.blit(dialog_bg, (dialog_x, dialog_y))
        
        # Draw border
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, (100, 100, 100), dialog_rect, 3)
        
        # Title
        title_text = self.title_font.render("Restart Game?", True, (50, 50, 50))
        title_rect = title_text.get_rect(centerx=dialog_x + dialog_width // 2, y=dialog_y + 30)
        self.screen.blit(title_text, title_rect)
        
        # Message
        message_lines = [
            "Are you sure you want to restart?",
            "Current game progress will be lost.",
            "",
            "Press R again to confirm",
            "Press ESC to cancel",
            f"Auto-cancel in {self.restart_confirmation_timer // 60 + 1} seconds"
        ]
        
        message_y = dialog_y + 80
        for line in message_lines:
            if line.startswith("Press"):
                color = (100, 50, 150)  # Purple for instructions
            elif line.startswith("Auto-cancel"):
                color = (150, 100, 50)  # Orange for timer
            else:
                color = (50, 50, 50)  # Default
            
            message_surface = self.font.render(line, True, color)
            message_rect = message_surface.get_rect(centerx=dialog_x + dialog_width // 2, y=message_y)
            self.screen.blit(message_surface, message_rect)
            message_y += 25
    
    def show_contextual_help(self, game_state, board=None) -> None:
        """
        Show contextual help based on current game state
        
        Args:
            game_state: Current game state
            board: Optional board for additional context
        """
        try:
            phase_value = game_state.phase.value if game_state.phase else "unknown"
        except (AttributeError, TypeError):
            phase_value = "unknown"
        
        help_messages = {
            'tile_placement': [
                "🎯 Click on any empty position to place your tile",
                "💡 Consider strategic positioning for future moves",
                "🎨 Your tile will be placed with the RED side up"
            ],
            'flip_selection': [
                "🔄 Click on a highlighted tile to flip it",
                "⚡ Flipping changes the tile's color (red ↔ green)",
                "🚫 Only tiles that can move are highlighted"
            ],
            'move_selection': [
                "➡️ Click on a highlighted position to move the flipped tile",
                "↔️ Only orthogonal moves allowed (up/down/left/right)",
                "🎯 Choose your destination carefully"
            ],
            'game_over': [
                "🏁 Game has ended!",
                "🔄 Press R to restart or ESC to quit",
                "📖 Press H for detailed rules and strategy tips"
            ]
        }
        
        messages = help_messages.get(phase_value, ["❓ Unknown game phase"])
        
        # Show the help messages
        for i, message in enumerate(messages):
            # Stagger the messages slightly
            duration = 180 + (i * 30)  # 3+ seconds, staggered
            if i == 0:
                self.show_info_message(message, duration)
            else:
                # For subsequent messages, we'd need a queue system
                # For now, just show the first message
                pass
    
    def update_display(self) -> None:
        """Update the display and maintain frame rate"""
        # Update timers
        if self.click_feedback_timer > 0:
            self.click_feedback_timer -= 1
        
        if self.error_timer > 0:
            self.error_timer -= 1
            if self.error_timer <= 0:
                self.error_message = None
                self.error_position = None
                self.error_type = "general"
        
        if self.warning_timer > 0:
            self.warning_timer -= 1
            if self.warning_timer <= 0:
                self.warning_message = None
        
        if self.info_timer > 0:
            self.info_timer -= 1
            if self.info_timer <= 0:
                self.info_message = None
        
        if self.tooltip_timer > 0:
            self.tooltip_timer -= 1
            if self.tooltip_timer <= 0:
                self.tooltip_message = None
                self.tooltip_position = None
        
        # Update restart confirmation timer
        if self.restart_confirmation_timer > 0:
            self.restart_confirmation_timer -= 1
            if self.restart_confirmation_timer <= 0:
                self.restart_confirmation_active = False
        
        # Update animations
        self._update_animations()
        
        # Performance optimization - only update if needed
        current_time = pygame.time.get_ticks()
        if current_time - self.last_render_time > 16:  # ~60 FPS
            pygame.display.flip()
            self.last_render_time = current_time
        else:
            self.frame_skip_counter += 1
        
        self.clock.tick(60)  # 60 FPS
    
    def is_running(self) -> bool:
        """Check if the window should continue running"""
        return self.running
    
    def quit(self) -> None:
        """Clean up and quit pygame"""
        self.running = False
        pygame.quit()
    
    # Animation System
    def add_tile_move_animation(self, from_pos: Position, to_pos: Position, tile_data: dict, duration: int = 20) -> None:
        """
        Add smooth tile movement animation
        
        Args:
            from_pos: Starting position
            to_pos: Ending position
            tile_data: Dictionary with tile information (shape, color, owner)
            duration: Animation duration in frames
        """
        if not self.animations_enabled:
            return  # Skip animation if disabled
            
        from_screen = self._board_position_to_screen(from_pos)
        to_screen = self._board_position_to_screen(to_pos)
        
        animation = {
            'type': 'tile_move',
            'from_pos': from_screen,
            'to_pos': to_screen,
            'current_pos': from_screen,
            'tile_data': tile_data,
            'duration': duration,
            'elapsed': 0,
            'easing': 'ease_out'
        }
        
        self.animations.append(animation)
    
    def add_tile_flip_animation(self, position: Position, old_color: TileColor, new_color: TileColor, duration: int = 15) -> None:
        """
        Add smooth tile flipping animation
        
        Args:
            position: Position of tile to flip
            old_color: Original color
            new_color: New color after flip
            duration: Animation duration in frames
        """
        if not self.animations_enabled:
            return  # Skip animation if disabled
            
        animation = {
            'type': 'tile_flip',
            'position': position,
            'old_color': old_color,
            'new_color': new_color,
            'duration': duration,
            'elapsed': 0,
            'flip_progress': 0.0,
            'easing': 'ease_in_out'
        }
        
        self.animations.append(animation)
    
    def add_tile_placement_animation(self, position: Position, tile_data: dict, duration: int = 12) -> None:
        """
        Add smooth tile placement animation with scale effect
        
        Args:
            position: Position where tile is placed
            tile_data: Dictionary with tile information
            duration: Animation duration in frames
        """
        if not self.animations_enabled:
            return  # Skip animation if disabled
            
        animation = {
            'type': 'tile_placement',
            'position': position,
            'tile_data': tile_data,
            'duration': duration,
            'elapsed': 0,
            'scale': 0.0,
            'easing': 'bounce'
        }
        
        self.animations.append(animation)
    
    def add_highlight_pulse_animation(self, positions: List[Position], duration: int = 60) -> None:
        """
        Add pulsing highlight animation for valid moves
        
        Args:
            positions: List of positions to highlight
            duration: Animation duration in frames
        """
        if not self.animations_enabled:
            return  # Skip animation if disabled
            
        animation = {
            'type': 'highlight_pulse',
            'positions': positions.copy(),
            'duration': duration,
            'elapsed': 0,
            'pulse_intensity': 0.0,
            'easing': 'sine_wave'
        }
        
        self.animations.append(animation)
    
    def add_win_celebration_animation(self, winning_positions: List[Position], duration: int = 120) -> None:
        """
        Add celebration animation for winning three-in-a-row
        
        Args:
            winning_positions: Positions that form the winning line
            duration: Animation duration in frames
        """
        if not self.animations_enabled:
            return  # Skip animation if disabled
            
        animation = {
            'type': 'win_celebration',
            'positions': winning_positions.copy(),
            'duration': duration,
            'elapsed': 0,
            'glow_intensity': 0.0,
            'particle_effects': [],
            'easing': 'ease_out'
        }
        
        # Add particle effects for each winning position
        for pos in winning_positions:
            screen_pos = self._board_position_to_screen(pos)
            for i in range(8):  # 8 particles per position
                import random
                import math
                angle = (i / 8) * 2 * math.pi
                speed = random.uniform(2, 5)
                animation['particle_effects'].append({
                    'x': screen_pos[0],
                    'y': screen_pos[1],
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'life': duration,
                    'color': (255, 215, 0)  # Gold color
                })
        
        self.animations.append(animation)
    
    def add_tile_hover_animation(self, position: Position, duration: int = 30) -> None:
        """
        Add subtle hover animation for tiles
        
        Args:
            position: Position of tile to animate
            duration: Animation duration in frames
        """
        # Only add hover animation if animations are enabled
        if not self.animations_enabled:
            return
            
        animation = {
            'type': 'tile_hover',
            'position': position,
            'duration': duration,
            'elapsed': 0,
            'scale_factor': 1.0,
            'easing': 'smooth_step'
        }
        
        self.animations.append(animation)
    
    def add_error_shake_animation(self, position: Position, duration: int = 20) -> None:
        """
        Add shake animation for error feedback
        
        Args:
            position: Position to shake
            duration: Animation duration in frames
        """
        animation = {
            'type': 'error_shake',
            'position': position,
            'duration': duration,
            'elapsed': 0,
            'shake_offset': (0, 0),
            'easing': 'elastic'
        }
        
        self.animations.append(animation)
    
    def _update_animations(self) -> None:
        """Update all active animations with variable speed control"""
        active_animations = []
        
        for animation in self.animations:
            # Apply animation speed multiplier
            animation['elapsed'] += self.animation_speed
            progress = min(1.0, animation['elapsed'] / animation['duration'])
            
            # Apply easing function
            eased_progress = self._apply_easing(progress, animation.get('easing', 'linear'))
            
            if animation['type'] == 'tile_move':
                self._update_tile_move_animation(animation, eased_progress)
            elif animation['type'] == 'tile_flip':
                self._update_tile_flip_animation(animation, eased_progress)
            elif animation['type'] == 'tile_placement':
                self._update_tile_placement_animation(animation, eased_progress)
            elif animation['type'] == 'highlight_pulse':
                self._update_highlight_pulse_animation(animation, eased_progress)
            elif animation['type'] == 'win_celebration':
                self._update_win_celebration_animation(animation, eased_progress)
            elif animation['type'] == 'tile_hover':
                self._update_tile_hover_animation(animation, eased_progress)
            elif animation['type'] == 'error_shake':
                self._update_error_shake_animation(animation, eased_progress)
            
            # Keep animation if not finished
            if animation['elapsed'] < animation['duration']:
                active_animations.append(animation)
        
        self.animations = active_animations
    
    def _apply_easing(self, progress: float, easing_type: str) -> float:
        """Apply easing function to animation progress with enhanced curves"""
        import math
        
        if easing_type == 'ease_out':
            return 1 - (1 - progress) ** 3
        elif easing_type == 'ease_in':
            return progress ** 3
        elif easing_type == 'ease_in_out':
            if progress < 0.5:
                return 2 * progress ** 2
            else:
                return 1 - 2 * (1 - progress) ** 2
        elif easing_type == 'bounce':
            # Enhanced bounce with multiple bounces
            if progress < 0.36363636:
                return 7.5625 * progress * progress
            elif progress < 0.72727273:
                progress -= 0.54545455
                return 7.5625 * progress * progress + 0.75
            elif progress < 0.90909091:
                progress -= 0.81818182
                return 7.5625 * progress * progress + 0.9375
            else:
                progress -= 0.95454545
                return 7.5625 * progress * progress + 0.984375
        elif easing_type == 'elastic':
            # Elastic easing for dramatic effect
            if progress == 0 or progress == 1:
                return progress
            result = -(2 ** (10 * (progress - 1))) * math.sin((progress - 1.1) * 5 * math.pi)
            # Clamp to reasonable bounds to avoid floating point precision issues
            return max(0.0, min(2.0, result))
        elif easing_type == 'sine_wave':
            return (math.sin(progress * math.pi * 4) + 1) / 2
        elif easing_type == 'smooth_step':
            # Smooth step function for natural motion
            return progress * progress * (3 - 2 * progress)
        elif easing_type == 'smoother_step':
            # Even smoother step function
            return progress * progress * progress * (progress * (progress * 6 - 15) + 10)
        else:  # linear
            return progress
    
    def _update_tile_move_animation(self, animation: dict, progress: float) -> None:
        """Update tile movement animation"""
        from_x, from_y = animation['from_pos']
        to_x, to_y = animation['to_pos']
        
        # Interpolate position
        current_x = from_x + (to_x - from_x) * progress
        current_y = from_y + (to_y - from_y) * progress
        
        animation['current_pos'] = (current_x, current_y)
    
    def _update_tile_flip_animation(self, animation: dict, progress: float) -> None:
        """Update tile flipping animation"""
        # Flip progress affects the visual scaling/rotation
        if progress < 0.5:
            # First half: scale down
            animation['flip_progress'] = progress * 2
        else:
            # Second half: scale up with new color
            animation['flip_progress'] = (1 - progress) * 2
    
    def _update_tile_placement_animation(self, animation: dict, progress: float) -> None:
        """Update tile placement animation"""
        animation['scale'] = progress
    
    def _update_highlight_pulse_animation(self, animation: dict, progress: float) -> None:
        """Update highlight pulsing animation"""
        import math
        animation['pulse_intensity'] = (math.sin(progress * math.pi * 6) + 1) / 2
    
    def _update_win_celebration_animation(self, animation: dict, progress: float) -> None:
        """Update win celebration animation"""
        import math
        animation['glow_intensity'] = math.sin(progress * math.pi * 3) * 0.5 + 0.5
        
        # Update particle effects
        for particle in animation['particle_effects']:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # Gravity
            particle['life'] -= 1
    
    def _update_tile_hover_animation(self, animation: dict, progress: float) -> None:
        """Update tile hover animation"""
        import math
        # Subtle scale pulsing
        animation['scale_factor'] = 1.0 + 0.1 * math.sin(progress * math.pi * 2)
    
    def _update_error_shake_animation(self, animation: dict, progress: float) -> None:
        """Update error shake animation"""
        import math
        import random
        
        # Decreasing shake intensity
        intensity = (1.0 - progress) * 5
        shake_x = random.uniform(-intensity, intensity)
        shake_y = random.uniform(-intensity, intensity)
        animation['shake_offset'] = (shake_x, shake_y)
    
    def _render_animations(self) -> None:
        """Render all active animations"""
        for animation in self.animations:
            if animation['type'] == 'tile_move':
                self._render_tile_move_animation(animation)
            elif animation['type'] == 'tile_flip':
                self._render_tile_flip_animation(animation)
            elif animation['type'] == 'tile_placement':
                self._render_tile_placement_animation(animation)
            elif animation['type'] == 'highlight_pulse':
                self._render_highlight_pulse_animation(animation)
            elif animation['type'] == 'win_celebration':
                self._render_win_celebration_animation(animation)
            elif animation['type'] == 'tile_hover':
                self._render_tile_hover_animation(animation)
            elif animation['type'] == 'error_shake':
                self._render_error_shake_animation(animation)
    
    def _render_tile_move_animation(self, animation: dict) -> None:
        """Render moving tile animation"""
        x, y = animation['current_pos']
        tile_data = animation['tile_data']
        
        # Draw tile at current animated position
        if tile_data['shape'] == 'hexagon':
            self._draw_hexagon(x, y, 25, self.COLORS[tile_data['color']])
        else:  # star
            self._draw_star(x, y, 25, self.COLORS[tile_data['color']])
    
    def _render_tile_flip_animation(self, animation: dict) -> None:
        """Render tile flipping animation"""
        position = animation['position']
        screen_x, screen_y = self._board_position_to_screen(position)
        
        # Scale effect during flip
        scale = 1.0 - abs(animation['flip_progress'] - 0.5) * 0.5
        radius = int(25 * scale)
        
        # Choose color based on flip progress
        if animation['flip_progress'] > 0.5:
            color = self.COLORS[animation['new_color'].value]
        else:
            color = self.COLORS[animation['old_color'].value]
        
        # Draw scaled tile
        self._draw_hexagon(screen_x, screen_y, radius, color)
    
    def _render_tile_placement_animation(self, animation: dict) -> None:
        """Render tile placement animation"""
        position = animation['position']
        screen_x, screen_y = self._board_position_to_screen(position)
        tile_data = animation['tile_data']
        
        # Scale effect
        radius = int(25 * animation['scale'])
        
        if radius > 0:
            if tile_data['shape'] == 'hexagon':
                self._draw_hexagon(screen_x, screen_y, radius, self.COLORS[tile_data['color']])
            else:  # star
                self._draw_star(screen_x, screen_y, radius, self.COLORS[tile_data['color']])
    
    def _render_highlight_pulse_animation(self, animation: dict) -> None:
        """Render pulsing highlight animation"""
        intensity = animation['pulse_intensity']
        alpha = int(100 + 155 * intensity)
        
        for position in animation['positions']:
            x = self.board_x + position.col * self.cell_size
            y = self.board_y + position.row * self.cell_size
            
            # Create pulsing highlight surface
            highlight_surface = pygame.Surface((self.cell_size - 4, self.cell_size - 4))
            highlight_surface.set_alpha(alpha)
            highlight_surface.fill(self.COLORS['highlight'])
            
            self.screen.blit(highlight_surface, (x + 2, y + 2))
    
    def _render_win_celebration_animation(self, animation: dict) -> None:
        """Render win celebration animation"""
        # Render glowing effect on winning positions
        glow_intensity = animation['glow_intensity']
        
        for position in animation['positions']:
            screen_x, screen_y = self._board_position_to_screen(position)
            
            # Draw glowing circle
            glow_radius = int(40 + 20 * glow_intensity)
            glow_color = (255, 215, 0, int(100 * glow_intensity))  # Gold with alpha
            
            # Create glow surface
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2))
            glow_surface.set_alpha(int(100 * glow_intensity))
            pygame.draw.circle(glow_surface, (255, 215, 0), (glow_radius, glow_radius), glow_radius)
            
            self.screen.blit(glow_surface, (screen_x - glow_radius, screen_y - glow_radius))
        
        # Render particle effects
        for particle in animation['particle_effects']:
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / animation['duration']))
                particle_surface = pygame.Surface((4, 4))
                particle_surface.set_alpha(alpha)
                particle_surface.fill(particle['color'])
                self.screen.blit(particle_surface, (int(particle['x']), int(particle['y'])))
    
    def _render_tile_hover_animation(self, animation: dict) -> None:
        """Render tile hover animation"""
        position = animation['position']
        screen_x, screen_y = self._board_position_to_screen(position)
        scale_factor = animation['scale_factor']
        
        # Draw subtle glow effect
        glow_radius = int(30 * scale_factor)
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2))
        glow_surface.set_alpha(50)
        pygame.draw.circle(glow_surface, (255, 255, 255), (glow_radius, glow_radius), glow_radius)
        self.screen.blit(glow_surface, (screen_x - glow_radius, screen_y - glow_radius))
    
    def _render_error_shake_animation(self, animation: dict) -> None:
        """Render error shake animation"""
        position = animation['position']
        screen_x, screen_y = self._board_position_to_screen(position)
        shake_x, shake_y = animation['shake_offset']
        
        # Draw error indicator with shake offset
        error_x = int(screen_x + shake_x)
        error_y = int(screen_y + shake_y)
        
        # Draw pulsing red circle
        pygame.draw.circle(self.screen, (255, 50, 50), (error_x, error_y), 25, 3)
        
        # Draw X mark
        x_size = 15
        pygame.draw.line(self.screen, (255, 0, 0), 
                        (error_x - x_size, error_y - x_size), 
                        (error_x + x_size, error_y + x_size), 3)
        pygame.draw.line(self.screen, (255, 0, 0), 
                        (error_x + x_size, error_y - x_size), 
                        (error_x - x_size, error_y + x_size), 3)
    
    def _render_cursor_preview(self) -> None:
        """Render cursor preview for tile placement"""
        if (self.show_cursor_preview and 
            self.cursor_preview_position and 
            self.cursor_preview_tile_data):
            
            screen_x, screen_y = self._board_position_to_screen(self.cursor_preview_position)
            tile_data = self.cursor_preview_tile_data
            
            # Draw semi-transparent preview tile
            preview_alpha = 150  # Semi-transparent
            
            # Create a surface for the preview tile
            preview_surface = pygame.Surface((60, 60))
            preview_surface.set_alpha(preview_alpha)
            preview_surface.fill(self.COLORS['background'])  # Transparent background
            
            # Draw the tile shape on the preview surface
            center_x, center_y = 30, 30  # Center of preview surface
            
            # Default to red if color is None or not in COLORS
            color_key = tile_data.get('color', 'red')
            if color_key not in self.COLORS:
                color_key = 'red'
            tile_color = self.COLORS[color_key]
            
            if tile_data.get('shape') == 'hexagon':
                self._draw_hexagon_on_surface(preview_surface, center_x, center_y, 25, tile_color)
            else:  # star
                self._draw_star_on_surface(preview_surface, center_x, center_y, 25, tile_color)
            
            # Blit the preview surface to the screen
            self.screen.blit(preview_surface, (screen_x - 30, screen_y - 30))
    
    def _draw_hexagon_on_surface(self, surface: pygame.Surface, x: int, y: int, radius: int, color: Tuple[int, int, int]) -> None:
        """Draw a hexagon on a specific surface"""
        import math
        points = []
        for i in range(6):
            angle = i * math.pi / 3 - math.pi / 2  # Start from top
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))
        
        # Draw filled hexagon
        pygame.draw.polygon(surface, color, points)
        
        # Draw border
        pygame.draw.polygon(surface, self.COLORS['grid_line'], points, 2)
    
    def _draw_star_on_surface(self, surface: pygame.Surface, x: int, y: int, radius: int, color: Tuple[int, int, int]) -> None:
        """Draw a star on a specific surface"""
        import math
        points = []
        for i in range(10):
            angle = i * math.pi / 5 - math.pi / 2  # Start from top
            if i % 2 == 0:
                # Outer points
                px = x + radius * math.cos(angle)
                py = y + radius * math.sin(angle)
            else:
                # Inner points
                px = x + (radius * 0.4) * math.cos(angle)
                py = y + (radius * 0.4) * math.sin(angle)
            points.append((px, py))
        
        # Draw filled star
        pygame.draw.polygon(surface, color, points)
        
        # Draw border
        pygame.draw.polygon(surface, self.COLORS['grid_line'], points, 2)
    
    def _screen_to_board_position(self, screen_pos: Tuple[int, int]) -> Optional[Position]:
        """
        Convert screen coordinates to board position
        
        Args:
            screen_pos: (x, y) screen coordinates
            
        Returns:
            Position object or None if outside board
        """
        x, y = screen_pos
        
        # Check if click is within board bounds
        if (self.board_x <= x <= self.board_x + self.board_size and
            self.board_y <= y <= self.board_y + self.board_size):
            
            # Calculate board position
            col = (x - self.board_x) // self.cell_size
            row = (y - self.board_y) // self.cell_size
            
            # Ensure within valid range
            if 0 <= row < 4 and 0 <= col < 4:
                return Position(row, col)
        
        return None
    
    def _board_position_to_screen(self, position: Position) -> Tuple[int, int]:
        """
        Convert board position to screen coordinates (center of cell)
        
        Args:
            position: Board position
            
        Returns:
            (x, y) screen coordinates of cell center
        """
        x = self.board_x + position.col * self.cell_size + self.cell_size // 2
        y = self.board_y + position.row * self.cell_size + self.cell_size // 2
        return (x, y)
    
    def _draw_highlights(self) -> None:
        """Draw highlights for valid move positions and hover effects"""
        # Draw valid move highlights
        for position in self.highlighted_positions:
            x = self.board_x + position.col * self.cell_size
            y = self.board_y + position.row * self.cell_size
            
            # Draw highlight rectangle
            highlight_rect = pygame.Rect(x + 2, y + 2, self.cell_size - 4, self.cell_size - 4)
            pygame.draw.rect(self.screen, self.COLORS['highlight'], highlight_rect, 3)
        
        # Draw hover effect
        if self.hovered_position and self.hovered_position not in self.highlighted_positions:
            x = self.board_x + self.hovered_position.col * self.cell_size
            y = self.board_y + self.hovered_position.row * self.cell_size
            
            # Draw subtle hover rectangle
            hover_rect = pygame.Rect(x + 4, y + 4, self.cell_size - 8, self.cell_size - 8)
            hover_color = (200, 200, 200)  # Light gray
            pygame.draw.rect(self.screen, hover_color, hover_rect, 2)
        
        # Draw click feedback
        if self.click_feedback_timer > 0 and self.last_clicked_position:
            x = self.board_x + self.last_clicked_position.col * self.cell_size
            y = self.board_y + self.last_clicked_position.row * self.cell_size
            
            # Draw pulsing click feedback
            alpha = int(255 * (self.click_feedback_timer / 30))  # Fade over 30 frames
            click_rect = pygame.Rect(x + 1, y + 1, self.cell_size - 2, self.cell_size - 2)
            
            # Create surface with alpha for fade effect
            feedback_surface = pygame.Surface((self.cell_size - 2, self.cell_size - 2))
            feedback_surface.set_alpha(alpha)
            feedback_surface.fill((255, 255, 255))
            self.screen.blit(feedback_surface, (x + 1, y + 1))
    
    def mark_dirty_region(self, rect: pygame.Rect) -> None:
        """Mark a region as dirty for optimized rendering"""
        self.dirty_regions.append(rect)
    
    def mark_position_dirty(self, position: Position) -> None:
        """Mark a board position as dirty"""
        x = self.board_x + position.col * self.cell_size
        y = self.board_y + position.row * self.cell_size
        dirty_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
        self.mark_dirty_region(dirty_rect)
    
    def optimize_rendering(self) -> bool:
        """
        Check if rendering optimizations should be applied
        
        Returns:
            True if optimizations should be used
        """
        # Skip optimizations if animations are active
        if self.animations:
            return False
        
        # Skip optimizations if frame rate is low
        if self.frame_skip_counter > 5:
            self.frame_skip_counter = 0
            return False
        
        return True
    
    def set_animation_speed(self, speed: float) -> None:
        """
        Set animation speed multiplier
        
        Args:
            speed: Speed multiplier (1.0 = normal, 2.0 = double speed, 0.5 = half speed)
        """
        self.animation_speed = max(0.1, min(5.0, speed))  # Clamp between 0.1x and 5.0x
        
        # Save the preference
        self._save_animation_settings()
    
    def set_animations_enabled(self, enabled: bool) -> None:
        """
        Enable or disable animations
        
        Args:
            enabled: True to enable animations, False to disable
        """
        self.animations_enabled = enabled
        if not enabled:
            # Clear all active animations when disabling
            self.clear_all_animations()
    
    def toggle_animations(self) -> bool:
        """
        Toggle animations on/off
        
        Returns:
            New animation state (True if enabled, False if disabled)
        """
        self.set_animations_enabled(not self.animations_enabled)
        return self.animations_enabled
    
    def clear_all_animations(self) -> None:
        """Clear all active animations"""
        self.animations.clear()
    
    def get_animation_count(self) -> int:
        """Get the number of active animations"""
        return len(self.animations)
    
    def is_animating(self) -> bool:
        """Check if any animations are currently active"""
        return len(self.animations) > 0
    
    def are_animations_enabled(self) -> bool:
        """Check if animations are enabled"""
        return self.animations_enabled
    
    def set_animations_enabled(self, enabled: bool) -> None:
        """
        Enable or disable animations
        
        Args:
            enabled: Whether to enable animations
        """
        self.animations_enabled = enabled
        if not enabled:
            # Clear all active animations when disabling
            self.clear_all_animations()
        
        # Save the preference
        self._save_animation_settings()
    
    def toggle_animations(self) -> bool:
        """
        Toggle animations on/off
        
        Returns:
            New animation state (True if enabled, False if disabled)
        """
        self.set_animations_enabled(not self.animations_enabled)
        return self.animations_enabled
    
    def are_animations_enabled(self) -> bool:
        """Check if animations are currently enabled"""
        return self.animations_enabled
    
    def _load_animation_settings(self) -> None:
        """Load animation settings from a simple config file"""
        try:
            import os
            config_path = os.path.expanduser("~/.xoxo_squared_settings")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('animations_enabled='):
                            value = line.split('=')[1].lower()
                            self.animations_enabled = value in ('true', '1', 'yes', 'on')
                        elif line.startswith('animation_speed='):
                            try:
                                self.animation_speed = float(line.split('=')[1])
                            except ValueError:
                                pass  # Keep default if invalid
        except Exception:
            # If any error occurs, just use defaults
            pass
    
    def _save_animation_settings(self) -> None:
        """Save animation settings to a simple config file"""
        try:
            import os
            config_path = os.path.expanduser("~/.xoxo_squared_settings")
            with open(config_path, 'w') as f:
                f.write(f"animations_enabled={self.animations_enabled}\n")
                f.write(f"animation_speed={self.animation_speed}\n")
        except Exception:
            # If saving fails, just continue silently
            pass
    
    def set_cursor_preview(self, tile_data: dict, enabled: bool = True) -> None:
        """
        Enable/disable cursor preview for tile placement
        
        Args:
            tile_data: Dictionary with tile information (shape, color, owner)
            enabled: Whether to show cursor preview
        """
        self.show_cursor_preview = enabled
        
        # Ensure tile_data has required fields if enabled
        if enabled and tile_data:
            # Validate and set defaults for required fields
            validated_data = {
                'shape': tile_data.get('shape', 'hexagon'),
                'color': tile_data.get('color', 'red'),
                'owner': tile_data.get('owner', 'Player 1')
            }
            
            # Ensure color is valid
            if validated_data['color'] not in ['red', 'green']:
                validated_data['color'] = 'red'
                
            # Ensure shape is valid
            if validated_data['shape'] not in ['hexagon', 'star']:
                validated_data['shape'] = 'hexagon'
                
            self.cursor_preview_tile_data = validated_data
        else:
            self.cursor_preview_tile_data = None
    
    def update_cursor_preview_position(self, mouse_pos: Tuple[int, int]) -> None:
        """
        Update cursor preview position based on mouse position
        
        Args:
            mouse_pos: Current mouse position
        """
        if self.show_cursor_preview:
            board_pos = self._screen_to_board_position(mouse_pos)
            self.cursor_preview_position = board_pos
    
    def _draw_board_tiles(self, board) -> None:
        """
        Draw all tiles from the board
        
        Args:
            board: Board object containing tiles to render
        """
        all_tiles = board.get_all_tiles()
        for position, tile in all_tiles:
            self._draw_tile(position, tile.get_current_color(), tile.get_shape())
    
    def _draw_placeholder_tiles(self) -> None:
        """Draw placeholder tiles for testing (will be replaced with actual tile rendering)"""
        # Draw some example tiles for visual testing
        test_positions = [
            (Position(0, 0), TileColor.RED, TileShape.HEXAGON),
            (Position(1, 1), TileColor.GREEN, TileShape.STAR),
            (Position(2, 2), TileColor.RED, TileShape.STAR),
        ]
        
        for position, color, shape in test_positions:
            self._draw_tile(position, color, shape)
    
    def _draw_tile(self, position: Position, color: TileColor, shape: TileShape) -> None:
        """
        Draw a tile at the specified position
        
        Args:
            position: Board position
            color: Tile color
            shape: Tile shape
        """
        center_x, center_y = self._board_position_to_screen(position)
        tile_color = self.COLORS['red'] if color == TileColor.RED else self.COLORS['green']
        
        # Calculate tile size based on cell size
        tile_radius = min(self.cell_size // 3, 40)
        
        if shape == TileShape.HEXAGON:
            self._draw_hexagon(center_x, center_y, tile_radius, tile_color)
        else:  # STAR
            self._draw_star(center_x, center_y, tile_radius, tile_color)
    
    def _draw_position_indicators(self) -> None:
        """Draw position indicators (row/col numbers) around the board"""
        # Draw row numbers on the left
        for row in range(4):
            y = self.board_y + row * self.cell_size + self.cell_size // 2
            text = self.font.render(str(row), True, self.COLORS['text'])
            text_rect = text.get_rect(center=(self.board_x - 20, y))
            self.screen.blit(text, text_rect)
        
        # Draw column numbers on the top
        for col in range(4):
            x = self.board_x + col * self.cell_size + self.cell_size // 2
            text = self.font.render(str(col), True, self.COLORS['text'])
            text_rect = text.get_rect(center=(x, self.board_y - 20))
            self.screen.blit(text, text_rect)
    
    def _draw_hexagon(self, x: int, y: int, radius: int, color: Tuple[int, int, int]) -> None:
        """Draw a hexagon shape with enhanced graphics"""
        import math
        points = []
        for i in range(6):
            angle = i * math.pi / 3 - math.pi / 2  # Start from top
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))
        
        # Draw filled hexagon
        pygame.draw.polygon(self.screen, color, points)
        
        # Draw border
        pygame.draw.polygon(self.screen, self.COLORS['grid_line'], points, 3)
        
        # Add inner highlight for 3D effect
        inner_points = []
        for i in range(6):
            angle = i * math.pi / 3 - math.pi / 2
            px = x + (radius * 0.7) * math.cos(angle)
            py = y + (radius * 0.7) * math.sin(angle)
            inner_points.append((px, py))
        
        # Lighter color for highlight
        highlight_color = tuple(min(255, c + 30) for c in color)
        pygame.draw.polygon(self.screen, highlight_color, inner_points, 1)
    
    def _draw_star(self, x: int, y: int, radius: int, color: Tuple[int, int, int]) -> None:
        """Draw a star shape with enhanced graphics"""
        import math
        points = []
        for i in range(10):
            angle = i * math.pi / 5 - math.pi / 2  # Start from top
            if i % 2 == 0:
                # Outer points
                px = x + radius * math.cos(angle)
                py = y + radius * math.sin(angle)
            else:
                # Inner points
                px = x + (radius * 0.4) * math.cos(angle)
                py = y + (radius * 0.4) * math.sin(angle)
            points.append((px, py))
        
        # Draw filled star
        pygame.draw.polygon(self.screen, color, points)
        
        # Draw border
        pygame.draw.polygon(self.screen, self.COLORS['grid_line'], points, 3)
        
        # Add center circle for better visual
        center_radius = radius // 4
        center_color = tuple(min(255, c + 40) for c in color)
        pygame.draw.circle(self.screen, center_color, (int(x), int(y)), center_radius)
        pygame.draw.circle(self.screen, self.COLORS['grid_line'], (int(x), int(y)), center_radius, 2)
    
    def _set_click_feedback(self, position: Position) -> None:
        """
        Set click feedback for visual indication
        
        Args:
            position: Position that was clicked
        """
        self.last_clicked_position = position
        self.click_feedback_timer = 30  # 30 frames of feedback
    
    def show_error_message(self, message: str, position: Optional[Position] = None, error_type: str = "general") -> None:
        """
        Show an error message
        
        Args:
            message: Error message to display
            position: Optional position where error occurred
            error_type: Type of error for styling
        """
        self.error_message = message
        self.error_position = position
        self.error_type = error_type
        self.error_timer = 180  # Show for 3 seconds at 60 FPS
    
    def show_warning_message(self, message: str, duration: int = 120) -> None:
        """
        Show a warning message
        
        Args:
            message: Warning message to display
            duration: Duration in frames (default 2 seconds at 60 FPS)
        """
        self.warning_message = message
        self.warning_timer = duration
    
    def show_info_message(self, message: str, duration: int = 90) -> None:
        """
        Show an info message
        
        Args:
            message: Info message to display
            duration: Duration in frames (default 1.5 seconds at 60 FPS)
        """
        self.info_message = message
        self.info_timer = duration
    
    def check_button_clicks(self, click_pos: Tuple[int, int]) -> Optional[str]:
        """
        Check if any buttons were clicked
        
        Args:
            click_pos: Mouse click position
            
        Returns:
            Button name that was clicked, or None
        """
        if hasattr(self, 'restart_button_rect') and self.restart_button_rect.collidepoint(click_pos):
            return "restart"
        elif hasattr(self, 'quit_button_rect') and self.quit_button_rect.collidepoint(click_pos):
            return "quit"
        return None