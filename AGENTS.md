# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

## Project Overview

This is a Gomoku (Five-in-a-Row) game implementation in Python with a Tkinter GUI and AI opponent. The project uses minimax search with alpha-beta pruning for the AI strategy.

The project is managed by [uv](https://docs.astral.sh/uv/) and targets **Python 3.13** (pinned in `.python-version`, declared in `pyproject.toml`).

## Running the Application

```bash
uv sync                # create .venv and install project + dev dependencies

uv run gomoku          # run with the default 15x15 board
uv run gomoku 7        # run with a custom board size (e.g. 7x7)
uv run gomoku -p       # enable cProfile output under /tmp/gomoku/

uv run python -m gomoku  # equivalent module entry point
```

## Development Commands

```bash
uv run pytest          # run the test suite
uv run mypy            # strict type checking over gomoku/ and tests/
uv run ruff check .    # lint (E, F, I, UP, B, C4, SIM, RUF)
uv run ruff format .   # formatting (line-length 88)
```

Do not invoke `python`/`pip` directly: everything should go through `uv run` so the pinned interpreter and lockfile are used. After changing dependencies, update the lockfile with `uv lock` (or `uv add`).

## Architecture

The codebase is organized into several modules:

- **`app.py`**: Main application controller that coordinates UI events, game state, and AI computation
- **`board.py`**: Immutable game board representation with pieces and game logic
- **`score.py`**: AI evaluation system including minimax search with alpha-beta pruning
- **`ui.py`**: Tkinter-based GUI with board rendering and event handling
- **`tcl.py`**: Runtime workaround that points `TCL_LIBRARY`/`TK_LIBRARY` at the interpreter's bundled Tcl/Tk
- **`__main__.py`**: Entry point with argument parsing and the `main()` function

### Key Design Patterns

- **Immutable Data Structures**: `Board` and `Piece` are frozen dataclasses, creating new instances for state changes
- **Threaded AI Computation**: AI thinking runs in a single-worker `ThreadPoolExecutor` to keep the UI responsive
- **Event-Driven Architecture**: UI events (`BoardClick`, `Tick`) are handled through a single callback (`App.on_event`)
- **Functional Evaluation**: Board evaluation uses `functools.lru_cache` for line-pattern scoring

### AI Implementation

- **Minimax Search**: Implemented in `MMSearch` class with configurable depth
- **Alpha-Beta Pruning**: Optimized search with early termination
- **Move Ordering**: Candidate moves are split into "critical" threats and the rest, each sorted by evaluation
- **Candidate Pruning**: `Board.next_boards()` only expands positions within radius 2 of an existing stone
- **Threading**: `App.think()` submits the search to the worker thread; the UI polls the returned `Future`

## Development Notes

- The AI uses a heuristic evaluation function that scores piece patterns in all four directions
- Board positions are shuffled during search to add variety to AI play
- Profiling (`--profile`) runs inside the worker thread and dumps to `/tmp/gomoku/profile.<step>.prf`
- The game alternates between black (`'b'`) and white (`'w'`) pieces, with black going first; the app opens with a black stone at the board center, so the human plays white
- Tkinter must not be imported/instantiated at module scope: `configure_tcl_environment()` in `tcl.py` has to run before `tkinter.Tk()` is created

## Code Conventions

- Frozen (`slots=True`) dataclasses for immutable game state
- Type hints everywhere; `mypy --strict` must pass
- `from __future__ import annotations` is used so forward references stay resolvable
- PEP 695 aliases (`type Color = str`) and builtin generics (`list[int]`, `int | None`) instead of `typing.List`/`Optional`
- Chinese full-width punctuation in UI strings and comments is intentional (`allowed-confusables` in `pyproject.toml`)

## Testing Notes

- 这是一个 tkinter 的 UI 程序，不适合直接用 GUI 运行测试；`tests/` 下的测试只覆盖不依赖 Tk 的逻辑（棋盘、评估、搜索、CLI 解析）
- 如需验证 UI/事件循环，请在本地手动运行一段独立脚本（创建 `App`、`root.update()`、最后 `root.destroy()`），并确保结束时不遗留 Tk 主循环
