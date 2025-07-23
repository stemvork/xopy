# Implementation Plan

- [x] 1. Set up project structure and core data models
  - Create directory structure for models, views, and controllers
  - Implement enumerations for TileShape, TileColor, and GamePhase
  - Create Position and Move dataclasses with validation
  - _Requirements: 1.1, 1.3_

- [x] 2. Implement core Tile class with state management
  - Create Tile class with shape, color, and owner properties
  - Implement color flipping functionality between red and green
  - Add methods for getting current state and owner information
  - Write unit tests for tile state management and flipping
  - _Requirements: 1.3, 2.2_

- [x] 3. Implement Player class with tile resource management
  - Create Player class with name, shape, and tile count tracking
  - Implement tile usage and availability checking methods
  - Add validation for tile placement capability
  - Write unit tests for player resource management
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 4. Create Board class with grid management
- [x] 4.1 Implement basic board operations
  - Create 4x4 grid structure with position validation
  - Implement tile placement and removal methods
  - Add position bounds checking and empty space validation
  - Write unit tests for basic board operations
  - _Requirements: 1.1, 1.4_

- [x] 4.2 Implement movement validation and calculation
  - Add orthogonal movement validation (up, down, left, right only)
  - Implement get_valid_moves method for tile movement options
  - Ensure movement destination must be empty
  - Write unit tests for movement validation
  - _Requirements: 2.3, 2.4_

- [x] 4.3 Implement three-in-a-row detection
  - Create method to detect horizontal, vertical, and diagonal three-in-a-row
  - Implement color-based matching (not player-based)
  - Return ThreeInRowResult with positions and direction
  - Write unit tests for all winning scenarios
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 4.4 Implement complex win condition logic
  - Add method to simulate opponent's ability to break three-in-a-row
  - Check if opponent can flip and move tiles to disrupt winning formation
  - Implement survivability check for three-in-a-row formations
  - Write unit tests for complex win scenarios
  - _Requirements: 3.4, 3.5_

- [x] 5. Implement Game class with turn management
- [x] 5.1 Create basic game flow coordination
  - Initialize game with two players and empty board
  - Implement turn switching and current player tracking
  - Add game phase management (flip, move, place)
  - Write unit tests for basic game flow
  - _Requirements: 1.4, 2.6_

- [x] 5.2 Implement move validation and execution
  - Create move validation for flip-move-place sequence
  - Handle first move exception (placement only)
  - Ensure tiles can only be flipped if they have valid moves
  - Write unit tests for move sequence validation
  - _Requirements: 2.1, 2.4, 2.5_

- [x] 5.3 Implement win condition checking
  - Add post-move win condition evaluation
  - Integrate complex survivability logic from Board class
  - Handle forced wins when opponent creates three-in-a-row
  - Write unit tests for win detection scenarios
  - _Requirements: 3.4, 3.5_

- [x] 6. Set up pygame foundation and window management
  - Install pygame dependency and create main game window
  - Set up basic game loop with event handling
  - Create window with appropriate size (800x700 for board + UI)
  - Implement clean shutdown and window close handling
  - _Requirements: 4.1, 4.5_

- [x] 7. Implement basic graphics rendering
- [x] 7.1 Create tile graphics and board rendering
  - Design and implement hexagon and star tile graphics
  - Create red and green color variants for each shape
  - Implement 4x4 grid rendering with proper spacing
  - Add grid lines and position indicators
  - _Requirements: 4.1, 6.3_

- [x] 7.2 Implement UI components and game state display
  - Create player information panel showing remaining tiles
  - Add current turn indicator and game phase display
  - Implement game over screen with winner/draw results
  - Add visual styling and consistent color scheme
  - _Requirements: 4.2, 4.5, 5.4, 5.5_

- [x] 8. Implement mouse interaction and event handling
- [x] 8.1 Create click detection and position mapping
  - Map mouse clicks to board positions
  - Implement hover effects for tiles and empty spaces
  - Add click feedback and visual confirmation
  - Handle edge cases for clicks outside valid areas
  - _Requirements: 4.3, 4.4_

- [x] 8.2 Implement game phase interaction logic
  - Handle flip selection phase with valid tile highlighting
  - Implement move selection with destination highlighting
  - Add tile placement interaction for empty positions
  - Provide visual feedback for invalid moves
  - _Requirements: 2.1, 4.3, 4.4, 6.2_

- [x] 9. Integrate model and view with complete game loop
  - Connect pygame view with game model through controller
  - Implement complete flip-move-place interaction sequence
  - Add real-time game state updates and visual feedback
  - Handle game over conditions and restart functionality
  - _Requirements: 2.6, 3.4, 4.5_

- [x] 10. Add error handling and user guidance
  - Implement clear error messages for invalid moves
  - Add visual indicators for move constraints and limitations
  - Handle edge cases like no tiles remaining or no valid moves
  - Provide helpful tooltips and game rule explanations
  - _Requirements: 5.5, 6.1, 6.2_

- [-] 11. Create comprehensive test suite
- [x] 11.1 Write integration tests for complete game scenarios
  - Test full game from start to finish with various outcomes
  - Verify complex win conditions with opponent disruption scenarios
  - Test edge cases like board full conditions and resource depletion
  - _Requirements: 3.5, 5.3_

- [x] 11.2 Write pygame interaction tests
  - Test mouse click handling and position mapping
  - Verify visual feedback and highlighting systems
  - Test game state synchronization between model and view
  - _Requirements: 4.3, 4.4_

- [x] 12. Polish and final integration
  - Add smooth animations for tile movement and flipping
  - Implement game restart functionality
  - Add keyboard shortcuts and accessibility features
  - Optimize rendering performance and add final visual polish
  - _Requirements: 4.1, 6.4_