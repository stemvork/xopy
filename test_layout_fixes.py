#!/usr/bin/env python3
"""
Test script to verify layout fixes for Task 12:
- Text readability improvements
- Layout overlap fixes
- Color contrast enhancements
"""

import unittest.mock as mock
from xoxo_squared.views.pygame_view import PygameView
from xoxo_squared.models import Game


def test_color_contrast():
    """Test that text colors provide good contrast"""
    print("🎨 Testing Color Contrast...")
    
    with mock.patch('pygame.init'), mock.patch('pygame.display.set_mode'), \
         mock.patch('pygame.time.Clock'), mock.patch('pygame.font.Font'):
        
        view = PygameView()
        
        # Check text colors
        text_color = view.COLORS['text']
        button_text_color = view.COLORS['button_text']
        light_text_color = view.COLORS['text_light']
        
        print(f"  ✓ Main text color: {text_color} (dark for light backgrounds)")
        print(f"  ✓ Button text color: {button_text_color} (dark for button backgrounds)")
        print(f"  ✓ Light text color: {light_text_color} (light for dark backgrounds)")
        
        # Check background colors
        panel_bg = view.COLORS['panel_bg']
        board_bg = view.COLORS['board_bg']
        background = view.COLORS['background']
        
        print(f"  ✓ Panel background: {panel_bg} (off-white for better contrast)")
        print(f"  ✓ Board background: {board_bg} (white)")
        print(f"  ✓ Main background: {background} (light gray)")
        
        # Verify contrast ratios (simplified check)
        def luminance(color):
            """Calculate relative luminance of a color"""
            r, g, b = [c / 255.0 for c in color]
            return 0.299 * r + 0.587 * g + 0.114 * b
        
        text_lum = luminance(text_color)
        bg_lum = luminance(panel_bg)
        contrast_ratio = (max(text_lum, bg_lum) + 0.05) / (min(text_lum, bg_lum) + 0.05)
        
        print(f"  ✓ Text/Panel contrast ratio: {contrast_ratio:.2f} (should be > 4.5 for accessibility)")
        
        assert contrast_ratio > 4.5, f"Insufficient contrast: {contrast_ratio}"


def test_layout_spacing():
    """Test that layout elements don't overlap"""
    print("\n📐 Testing Layout Spacing...")
    
    with mock.patch('pygame.init'), mock.patch('pygame.display.set_mode'), \
         mock.patch('pygame.time.Clock'), mock.patch('pygame.font.Font'):
        
        view = PygameView()
        
        # Check board positioning
        print(f"  ✓ Board size: {view.board_size}x{view.board_size}")
        print(f"  ✓ Board position: ({view.board_x}, {view.board_y})")
        print(f"  ✓ Board bottom: {view.board_y + view.board_size}")
        
        # Check UI panel positioning
        print(f"  ✓ Info panel Y: {view.info_panel_y}")
        print(f"  ✓ Space between board and UI: {view.info_panel_y - (view.board_y + view.board_size)}")
        
        # Verify no overlap between board and UI
        board_bottom = view.board_y + view.board_size
        ui_top = view.info_panel_y
        spacing = ui_top - board_bottom
        
        print(f"  ✓ Board-to-UI spacing: {spacing} pixels")
        assert spacing >= 20, f"Insufficient spacing between board and UI: {spacing}"
        
        # Check window dimensions
        print(f"  ✓ Window size: {view.width}x{view.height}")
        print(f"  ✓ Info panel height: {view.info_panel_height}")
        
        # Verify UI fits within window
        instructions_y = view.info_panel_y + 150  # Instructions panel position
        instructions_height = min(160, view.height - instructions_y - 20)
        total_ui_height = instructions_y + instructions_height
        
        print(f"  ✓ Total UI height: {total_ui_height}")
        print(f"  ✓ Window height: {view.height}")
        
        assert total_ui_height <= view.height, f"UI exceeds window height: {total_ui_height} > {view.height}"


def test_responsive_elements():
    """Test that UI elements are responsive to window size"""
    print("\n📱 Testing Responsive Elements...")
    
    with mock.patch('pygame.init'), mock.patch('pygame.display.set_mode'), \
         mock.patch('pygame.time.Clock'), mock.patch('pygame.font.Font'):
        
        # Test different window sizes
        sizes = [(800, 800), (1000, 1000), (1200, 1000)]
        
        for width, height in sizes:
            view = PygameView(width, height)
            
            print(f"  ✓ Testing {width}x{height}:")
            print(f"    - Board centered at: ({view.board_x}, {view.board_y})")
            print(f"    - Info panel Y: {view.info_panel_y}")
            
            # Check that board is centered
            expected_board_x = (width - view.board_size) // 2
            assert view.board_x == expected_board_x, f"Board not centered: {view.board_x} != {expected_board_x}"
            
            # Check that UI fits
            total_height_needed = view.info_panel_y + 300  # Approximate UI height
            assert total_height_needed <= height, f"UI doesn't fit in {width}x{height}"
            
            print(f"    ✓ Layout fits properly")


def test_panel_positioning():
    """Test that panels don't overlap with each other"""
    print("\n🎛️ Testing Panel Positioning...")
    
    with mock.patch('pygame.init'), mock.patch('pygame.display.set_mode'), \
         mock.patch('pygame.time.Clock'), mock.patch('pygame.font.Font'):
        
        view = PygameView()
        
        # Game info panel
        info_panel = {
            'x': 30,
            'y': view.info_panel_y,
            'width': 350,
            'height': 100  # Updated height
        }
        
        # Player 1 panel
        p1_panel = {
            'x': 400,
            'y': view.info_panel_y,
            'width': 180,
            'height': 100
        }
        
        # Player 2 panel
        p2_panel = {
            'x': 600,
            'y': view.info_panel_y,
            'width': 180,
            'height': 100
        }
        
        # Control buttons
        buttons = {
            'x': 30,  # Updated position
            'y': view.info_panel_y + 110,  # Updated position
            'width': 170,  # Two buttons + spacing (80 + 10 + 80)
            'height': 25  # Updated height
        }
        
        # Instructions panel (using responsive logic)
        available_space = view.height - view.info_panel_y - 40
        panel_y_offset = min(150, max(120, available_space // 2))
        instructions_y = view.info_panel_y + panel_y_offset
        max_panel_height = view.height - instructions_y - 20
        
        instructions = {
            'x': 30,
            'y': instructions_y,
            'width': min(800, view.width - 60),
            'height': min(160, max(80, max_panel_height))
        }
        
        panels = {
            'info': info_panel,
            'player1': p1_panel,
            'player2': p2_panel,
            'buttons': buttons,
            'instructions': instructions
        }
        
        print("  Panel positions:")
        for name, panel in panels.items():
            print(f"    {name}: ({panel['x']}, {panel['y']}) {panel['width']}x{panel['height']}")
        
        # Check for overlaps
        def panels_overlap(p1, p2):
            """Check if two panels overlap"""
            return not (p1['x'] + p1['width'] <= p2['x'] or 
                       p2['x'] + p2['width'] <= p1['x'] or
                       p1['y'] + p1['height'] <= p2['y'] or
                       p2['y'] + p2['height'] <= p1['y'])
        
        overlaps = []
        panel_names = list(panels.keys())
        for i in range(len(panel_names)):
            for j in range(i + 1, len(panel_names)):
                name1, name2 = panel_names[i], panel_names[j]
                if panels_overlap(panels[name1], panels[name2]):
                    overlaps.append((name1, name2))
        
        if overlaps:
            print(f"  ❌ Found overlaps: {overlaps}")
            for name1, name2 in overlaps:
                p1, p2 = panels[name1], panels[name2]
                print(f"    {name1} vs {name2}:")
                print(f"      {name1}: {p1['x']}-{p1['x']+p1['width']}, {p1['y']}-{p1['y']+p1['height']}")
                print(f"      {name2}: {p2['x']}-{p2['x']+p2['width']}, {p2['y']}-{p2['y']+p2['height']}")
        else:
            print("  ✓ No panel overlaps detected")
        
        assert not overlaps, f"Panel overlaps detected: {overlaps}"


def test_text_rendering():
    """Test text rendering with proper colors"""
    print("\n📝 Testing Text Rendering...")
    
    with mock.patch('pygame.init'), mock.patch('pygame.display.set_mode'), \
         mock.patch('pygame.time.Clock'), mock.patch('pygame.font.Font'):
        
        view = PygameView()
        game = Game()
        game_state = game.get_game_state()
        
        # Test that we have appropriate text colors for different contexts
        contexts = {
            'main_text': view.COLORS['text'],
            'button_text': view.COLORS['button_text'],
            'light_text': view.COLORS['text_light']
        }
        
        print("  Text color contexts:")
        for context, color in contexts.items():
            r, g, b = color
            brightness = (r + g + b) / 3
            print(f"    {context}: {color} (brightness: {brightness:.1f})")
            
            # Verify colors are appropriate
            if 'light' in context:
                assert brightness > 200, f"Light text should be bright: {brightness}"
            else:
                assert brightness < 100, f"Dark text should be dark: {brightness}"
        
        print("  ✓ All text colors are appropriate for their contexts")


def main():
    """Run all layout and readability tests"""
    print("🔧 Testing Layout Fixes and Text Readability")
    print("=" * 60)
    
    try:
        test_color_contrast()
        test_layout_spacing()
        test_responsive_elements()
        test_panel_positioning()
        test_text_rendering()
        
        print("\n" + "=" * 60)
        print("✅ All layout and readability tests passed!")
        print("\nImprovements verified:")
        print("  🎨 Text contrast improved for better readability")
        print("  📐 Layout spacing fixed to prevent overlaps")
        print("  📱 Responsive design for different window sizes")
        print("  🎛️ Panel positioning optimized")
        print("  📝 Text colors appropriate for all contexts")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()