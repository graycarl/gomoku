# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Gomoku (Five-in-a-Row) game implementation in Python with a Tkinter GUI and AI opponent. The project uses minimax search with alpha-beta pruning for the AI strategy.

## Running the Application

```bash
# Run with default 15x15 board
python -m gomoku

# Run with custom board size (e.g., 7x7)
python -m gomoku 7

# Run with profiling enabled
python -m gomoku -p
```

## Architecture

The codebase is organized into several modules:

- **`app.py`**: Main application controller that coordinates UI events, game state, and AI computation
- **`board.py`**: Immutable game board representation with pieces and game logic
- **`score.py`**: AI evaluation system including minimax search with alpha-beta pruning
- **`ui.py`**: Tkinter-based GUI with board rendering and event handling
- **`__main__.py`**: Entry point with argument parsing

### Key Design Patterns

- **Immutable Data Structures**: `Board` and `Piece` are immutable dataclasses, creating new instances for state changes
- **Threaded AI Computation**: AI thinking runs in a separate thread to keep UI responsive
- **Event-Driven Architecture**: UI events (`BoardClick`, `Tick`) are handled through callbacks
- **Functional Evaluation**: Board evaluation uses cached scoring functions for performance

### AI Implementation

- **Minimax Search**: Implemented in `MMSearch` class with configurable depth
- **Alpha-Beta Pruning**: Optimized search with early termination
- **Position Evaluation**: Heuristic scoring based on piece patterns and continuity
- **Threading**: AI computation runs asynchronously to maintain UI responsiveness

## Development Notes

- The AI uses a simple evaluation function that scores based on piece continuity in all directions (horizontal, vertical, diagonal)
- Board positions are randomized during search to add variety to AI play
- Profiling can be enabled to analyze AI performance (outputs to `/tmp/gomoku/`)
- The game alternates between black ('b') and white ('w') pieces, with black going first

## Code Conventions

- Uses dataclasses with frozen=True for immutable game state
- Type hints are used throughout for better code clarity
- Lambda functions and functional programming patterns are common
- Print statements are used for debugging (consider removing in production)

## Testing Notes

- 这是一个 tkinter 的 UI 程序，不适合直接用来运行测试，如需测试，应该编写独立的测试脚本