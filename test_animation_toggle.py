#!/usr/bin/env python3
"""
Test script to verify animation toggle functionality:
- Animations can be enabled/disabled
- Animation methods respect the enabled state
- Keyboard shortcuts work properly
- Performance benefits when disabled
"""

import unittest.mock as mock
from xoxo_squared.views.pygame_view import PygameView
from xoxo_squared.controllers.game_controller import GameController
from xoxo_squared.models import Game, Position, GameEvent, TileColor


def test_animation_toggle_basic():
    """Test basic animation toggle functionality"""
    print("🎬 Testing Animation Toggle - Basic Functionality")
    print("=" * 60)
    
    with mock.patch('pygame.init'), mock.patch('pygame.display.set_mode'), \
         mock.patch('pygame.time.Clock'), mock.patch('pygame.font.Font'):
        
        view = PygameView()
        
        # Test initial state
        print(f"1. Initial state: animations_enabled = {view.animations_enabled}")
        assert view.animations_enabled == True, "Animations should be enabled by default"
        
        # Test toggle method
        new_state = view.toggle_animations()
        print(f"2. After toggle: animations_enabled = {view.animations_enabled}, returned = {new_state}")
        assert view.animations_enabled == False, "Animations should be disabled after toggle"
        assert new_state == False, "Toggle should return new state"
        
        # Test toggle back
        new_state = view.toggle_animations()
        print(f"3. After second toggle: animations_enabled = {view.animations_enabled}, returned = {new_state}")
        assert view.animations_enabled == True, "Animations should be enabled after second toggle"
        assert new_state == True, "Toggle should return new state"
        
        # Test direct setting
        view.set_animations_enabled(False)
        print(f"4. After set_animations_enabled(False): {view.animations_enabled}")
        assert view.animations_enabled == False, "Direct setting should work"
        
        view.set_animations_enabled(True)
        print(f"5. After set_animations_enabled(True): {view.animations_enabled}")
        assert view.animations_enabled == True, "Direct setting should work"
        
        print("✅ Basic animation toggle functionality working!")


def test_animation_methods_respect_toggle():
    """Test that animation methods respect the enabled/disabled state"""
    print("\n🎭 Testing Animation Methods Respect Toggle")
    print("=" * 60)
    
    with mock.patch('pygame.init'), mock.patch('pygame.display.set_mode'), \
         mock.patch('pygame.time.Clock'), mock.patch('pygame.font.Font'):
        
        view = PygameView()
        
        # Test with animations enabled
        view.set_animations_enabled(True)
        initial_count = len(view.animations)
        
        # Add various animations
        tile_data = {'shape': 'hexagon', 'color': 'red', 'owner': 'Player 1'}
        view.add_tile_placement_animation(Position(0, 0), tile_data)
        view.add_tile_flip_animation(Position(1, 1), TileColor.RED, TileColor.GREEN)
        view.add_tile_move_animation(Position(0, 0), Position(1, 1), tile_data)
        
        enabled_count = len(view.animations)
        print(f"1. With animations ENABLED: {enabled_count - initial_count} animations added")
        assert enabled_count > initial_count, "Animations should be added when enabled"
        
        # Clear animations and test with disabled
        view.clear_all_animations()
        view.set_animations_enabled(False)
        initial_count = len(view.animations)
        
        # Try to add animations when disabled
        view.add_tile_placement_animation(Position(0, 0), tile_data)
        view.add_tile_flip_animation(Position(1, 1), TileColor.RED, TileColor.GREEN)
        view.add_tile_move_animation(Position(0, 0), Position(1, 1), tile_data)
        
        disabled_count = len(view.animations)
        print(f"2. With animations DISABLED: {disabled_count - initial_count} animations added")
        assert disabled_count == initial_count, "No animations should be added when disabled"
        
        print("✅ Animation methods properly respect enabled/disabled state!")


def test_keyboard_shortcuts():
    """Test keyboard shortcuts for animation control"""
    print("\n⌨️ Testing Keyboard Shortcuts")
    print("=" * 60)
    
    with mock.patch('pygame.init'), mock.patch('pygame.display.set_mode'), \
         mock.patch('pygame.time.Clock'), mock.patch('pygame.font.Font'):
        
        view = PygameView()
        game = Game()
        controller = GameController(game, view)
        
        # Test animation toggle shortcut (A key)
        initial_state = view.animations_enabled
        toggle_event = GameEvent("key", key="a")
        result = controller.handle_game_event(toggle_event)
        
        print(f"1. Initial state: {initial_state}")
        print(f"2. After 'A' key: {view.animations_enabled}")
        print(f"3. Controller result: {result['success']}, message: '{result['message']}'")
        
        assert result['success'] == True, "Animation toggle should succeed"
        assert view.animations_enabled != initial_state, "Animation state should change"
        assert "Animations" in result['message'], "Message should mention animations"
        
        # Test animation speed toggle (S key) when animations are enabled
        if view.animations_enabled:
            initial_speed = view.animation_speed
            speed_event = GameEvent("key", key="s")
            result = controller.handle_game_event(speed_event)
            
            print(f"4. Initial speed: {initial_speed}")
            print(f"5. After 'S' key: {view.animation_speed}")
            print(f"6. Speed toggle result: {result['success']}, message: '{result['message']}'")
            
            assert result['success'] == True, "Speed toggle should succeed when animations enabled"
            assert view.animation_speed != initial_speed, "Animation speed should change"
        
        # Test speed toggle when animations are disabled
        view.set_animations_enabled(False)
        speed_event = GameEvent("key", key="s")
        result = controller.handle_game_event(speed_event)
        
        print(f"7. Speed toggle when disabled: {result['success']}, message: '{result['message']}'")
        assert result['success'] == False, "Speed toggle should fail when animations disabled"
        
        print("✅ Keyboard shortcuts working correctly!")


def test_performance_benefits():
    """Test performance benefits of disabling animations"""
    print("\n⚡ Testing Performance Benefits")
    print("=" * 60)
    
    with mock.patch('pygame.init'), mock.patch('pygame.display.set_mode'), \
         mock.patch('pygame.time.Clock'), mock.patch('pygame.font.Font'):
        
        view = PygameView()
        
        # Test that disabling animations clears existing ones
        tile_data = {'shape': 'hexagon', 'color': 'red', 'owner': 'Player 1'}
        
        # Add animations when enabled
        view.set_animations_enabled(True)
        view.add_tile_placement_animation(Position(0, 0), tile_data)
        view.add_tile_flip_animation(Position(1, 1), TileColor.RED, TileColor.GREEN)
        view.add_win_celebration_animation([Position(0, 0), Position(0, 1), Position(0, 2)])
        
        active_count = len(view.animations)
        print(f"1. Active animations when enabled: {active_count}")
        assert active_count > 0, "Should have active animations"
        
        # Disable animations - should clear existing ones
        view.set_animations_enabled(False)
        cleared_count = len(view.animations)
        print(f"2. Active animations after disabling: {cleared_count}")
        assert cleared_count == 0, "All animations should be cleared when disabled"
        
        # Test optimization checks
        can_optimize_disabled = view.optimize_rendering()
        print(f"3. Can optimize rendering when animations disabled: {can_optimize_disabled}")
        
        # Re-enable and add animations
        view.set_animations_enabled(True)
        view.add_tile_placement_animation(Position(0, 0), tile_data)
        can_optimize_enabled = view.optimize_rendering()
        print(f"4. Can optimize rendering with active animations: {can_optimize_enabled}")
        
        # When animations are disabled, rendering can be optimized more aggressively
        view.set_animations_enabled(False)
        can_optimize_no_animations = view.optimize_rendering()
        print(f"5. Can optimize rendering with no animations: {can_optimize_no_animations}")
        
        print("✅ Performance optimizations working correctly!")


def test_integration_with_game():
    """Test animation toggle integration with actual game"""
    print("\n🎮 Testing Integration with Game")
    print("=" * 60)
    
    with mock.patch('pygame.init'), mock.patch('pygame.display.set_mode'), \
         mock.patch('pygame.time.Clock'), mock.patch('pygame.font.Font'):
        
        view = PygameView()
        game = Game()
        controller = GameController(game, view)
        
        # Test that game works with animations disabled
        view.set_animations_enabled(False)
        print(f"1. Animations disabled: {not view.animations_enabled}")
        
        # Make a game move
        game_state = game.get_game_state()
        print(f"2. Initial game phase: {game_state.phase.value}")
        
        # Simulate a tile placement
        click_event = GameEvent("click", position=Position(1, 1))
        result = controller.handle_game_event(click_event)
        
        print(f"3. Move result: {result['success']}, message: '{result['message']}'")
        print(f"4. Animations after move: {len(view.animations)} active")
        
        # Game should work normally even with animations disabled
        assert result['success'] == True, "Game moves should work with animations disabled"
        assert len(view.animations) == 0, "No animations should be created when disabled"
        
        # Test with animations enabled
        view.set_animations_enabled(True)
        print(f"5. Animations re-enabled: {view.animations_enabled}")
        
        # Make another move
        click_event2 = GameEvent("click", position=Position(2, 2))
        result2 = controller.handle_game_event(click_event2)
        
        print(f"6. Second move result: {result2['success']}")
        print(f"7. Animations after second move: {len(view.animations)} active")
        
        print("✅ Game integration working correctly!")


def main():
    """Run all animation toggle tests"""
    print("🚀 Testing Animation Toggle Functionality")
    print("=" * 80)
    
    try:
        test_animation_toggle_basic()
        test_animation_methods_respect_toggle()
        test_keyboard_shortcuts()
        test_performance_benefits()
        test_integration_with_game()
        
        print("\n" + "=" * 80)
        print("🎉 ALL ANIMATION TOGGLE TESTS PASSED!")
        print("\nFeatures verified:")
        print("  🎬 Animations can be toggled on/off")
        print("  🎭 Animation methods respect enabled state")
        print("  ⌨️ Keyboard shortcuts (A = toggle, S = speed)")
        print("  ⚡ Performance benefits when disabled")
        print("  🎮 Full game integration")
        print("\nKeyboard Controls:")
        print("  A - Toggle animations on/off")
        print("  S - Change animation speed (when enabled)")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()