"""Application controller wiring the UI, game state and AI search together."""

from __future__ import annotations

import contextlib
import cProfile
import datetime
import pathlib
from collections.abc import Iterator
from concurrent import futures
from typing import final

from . import ui
from .board import Board
from .score import MMSearch, winner

PROFILE_DIR = pathlib.Path("/tmp/gomoku")


@final
class App:
    """Coordinates user events, the immutable board state and AI thinking."""

    def __init__(
        self, canvassize: int = 600, boardsize: int = 7, profile: bool = False
    ) -> None:
        self.profile = profile
        self.ui = ui.GUI(canvassize, self.on_event)
        self.thinking: futures.Future[tuple[Board, datetime.timedelta]] | None = None
        self.thinking_executor = futures.ThreadPoolExecutor(max_workers=1)
        self.game_ended = False
        self.init_game(boardsize)

    def run(self) -> None:
        try:
            self.ui.mainloop()
        finally:
            self.thinking_executor.shutdown(wait=False, cancel_futures=True)

    def init_game(self, boardsize: int) -> None:
        """Reset the board, place the opening stone and redraw the UI."""
        self.current = Board(size=(boardsize, boardsize))
        x, y = self.current.size[0] // 2, self.current.size[1] // 2
        self.mmsearch = MMSearch("b", 3)
        self.current = self.current.add(x, y)
        self.game_ended = False
        self.ui.init_board(self.current)
        self.ui.log_message("Init game done.")

    @contextlib.contextmanager
    def maybe_profile(self, step: int) -> Iterator[None]:
        """Profile the enclosed block when ``--profile`` was requested."""
        if not self.profile:
            yield
            return

        path = PROFILE_DIR / f"profile.{step}.prf"
        path.parent.mkdir(parents=True, exist_ok=True)
        profiler = cProfile.Profile()
        profiler.enable()
        try:
            yield
        finally:
            profiler.disable()
            profiler.dump_stats(path)
            print(f"Profile: {path}")

    def check_game_end(self) -> bool:
        """Show the winner dialog if the game has ended."""
        game_winner = winner(self.current)
        if game_winner is None:
            return False
        self.game_ended = True
        self.ui.show_winner_dialog(game_winner)
        return True

    def think(self) -> None:
        assert self.thinking is None
        self.thinking = self.thinking_executor.submit(self.search)
        self.ui.log_message("Thinking...")

    def search(self) -> tuple[Board, datetime.timedelta]:
        """Run the AI search; this executes inside the worker thread."""
        board = self.current
        with self.maybe_profile(board.step):
            return self.mmsearch(board)

    def on_event(self, event: ui.UIEvent) -> None:
        if isinstance(event, ui.BoardClick):
            self._on_board_click(event)
        elif isinstance(event, ui.Tick):
            self._on_tick()

    def _on_board_click(self, event: ui.BoardClick) -> None:
        if self.thinking or self.game_ended:
            return
        try:
            self.current = self.current.add(event.x, event.y)
        except RuntimeError as exc:
            self.ui.log_message(f"Invalid move: {exc}")
            return

        piece = self.current.last_piece
        self.ui.render_piece(piece)
        self.ui.log_message(f"You put on {piece}")

        if not self.check_game_end():
            self.think()

    def _on_tick(self) -> None:
        if self.thinking is None:
            return

        if not self.thinking.done():
            self.ui.log_message(f"Thinking ... {self.mmsearch.iter_times}", amend=True)
            return

        self.current, elapsed = self.thinking.result()
        self.thinking = None
        count = self.mmsearch.iter_times
        self.ui.log_message(
            f"Thinking ... {count} Using {elapsed.total_seconds():.2f}s", amend=True
        )
        piece = self.current.last_piece
        self.ui.render_piece(piece)
        self.ui.log_message(f"AI put on {piece}")
        self.check_game_end()
