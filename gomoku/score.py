"""Board evaluation and minimax search with alpha-beta pruning."""

from __future__ import annotations

import datetime
import functools
import time
from typing import final

from .board import DIRECTIONS, Board, Color, Piece, Position, other

# Patterns are read along a line window centered on a stone of the evaluated
# color: 1 = our stone, 0 = empty, -1 = opponent stone.
PATTERN_SCORES: dict[tuple[int, ...], int] = {
    (1, 1, 1, 1, 1): 100_000,  # 连五
    (0, 1, 1, 1, 1, 0): 10_000,  # 活四
    (1, 1, 1, 1, 0): 1_000,  # 冲四
    (0, 1, 1, 1, 1): 1_000,  # 冲四
    (1, 0, 1, 1, 1): 1_000,  # 跳冲四
    (1, 1, 0, 1, 1): 1_000,  # 跳冲四
    (1, 1, 1, 0, 1): 1_000,  # 跳冲四
    (0, 1, 1, 1, 0): 800,  # 活三
    (0, 0, 1, 1, 1, 0, 0): 800,  # 活三
    (1, 1, 1, 0, 0): 200,  # 眠三
    (0, 0, 1, 1, 1): 200,  # 眠三
    (1, 0, 1, 1, 0): 200,  # 跳眠三
    (0, 1, 1, 0, 1): 200,  # 跳眠三
    (0, 1, 1, 0, 0): 50,  # 活二
    (0, 0, 1, 1, 0): 50,  # 活二
    (1, 1, 0, 0, 0): 10,  # 眠二
    (0, 0, 0, 1, 1): 10,  # 眠二
    (1, 0, 1, 0, 0): 10,  # 跳眠二
    (0, 0, 1, 0, 1): 10,  # 跳眠二
}

WIN_SCORE = 100_000


def _count_pattern_matches(line: tuple[int, ...], pattern: tuple[int, ...]) -> int:
    return sum(
        line[i : i + len(pattern)] == pattern
        for i in range(len(line) - len(pattern) + 1)
    )


def _max_consecutive(line: tuple[int, ...]) -> int:
    longest = current = 0
    for value in line:
        current = current + 1 if value == 1 else 0
        longest = max(longest, current)
    return longest


@functools.lru_cache(maxsize=10_000)
def pattern_match_score(line: tuple[int, ...]) -> int:
    """Score a single nine-position line window."""
    if len(line) < 5:
        return 0

    score = sum(
        _count_pattern_matches(line, pattern) * value
        for pattern, value in PATTERN_SCORES.items()
    )
    consecutive = _max_consecutive(line)
    if consecutive >= 2:
        score += consecutive**3
    return score


def _line_window(
    stones: dict[Position, Piece],
    x: int,
    y: int,
    dx: int,
    dy: int,
    color: Color,
) -> tuple[int, ...]:
    line: list[int] = []
    for i in range(-4, 5):
        piece = stones.get((x + i * dx, y + i * dy))
        if piece is None:
            line.append(0)
        else:
            line.append(1 if piece.color == color else -1)
    return tuple(line)


@final
class Evaluator:
    """Heuristic board evaluator; higher scores favor ``color``."""

    def __init__(self, color: Color) -> None:
        self.color = color
        self.count = 0
        self._cache: dict[int, int] = {}

    def __call__(self, board: Board) -> int:
        key = hash((board.size, board.pieces))
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        mine = self._evaluate_color(board, self.color)
        peer = self._evaluate_color(board, other(self.color))
        result = mine - int(peer * 1.2)

        self._cache[key] = result
        self.count += 1
        return result

    def _evaluate_color(self, board: Board, color: Color) -> int:
        stones = {p.pos: p for p in board.pieces}
        total = 0
        for (x, y), piece in stones.items():
            if piece.color != color:
                continue
            for dx, dy in DIRECTIONS:
                total += pattern_match_score(_line_window(stones, x, y, dx, dy, color))
        return total


@final
class MMSearch:
    """Minimax search with alpha-beta pruning and move ordering."""

    def __init__(self, color: Color, max_depth: int) -> None:
        self.color = color
        self.max_depth = max_depth
        self.evaluate = Evaluator(color)

    @property
    def iter_times(self) -> int:
        """Number of positions evaluated by the most recent search."""
        return self.evaluate.count

    def __call__(self, board: Board) -> tuple[Board, datetime.timedelta]:
        start = time.perf_counter()
        self.evaluate.count = 0
        _, best = self.best_next(board, depth=1)
        elapsed = datetime.timedelta(seconds=time.perf_counter() - start)
        print(f"Evaluate {self.evaluate.count} times, using {elapsed}")
        return best, elapsed

    def _is_critical_position(self, board: Board, test_board: Board) -> bool:
        """Whether a move creates or blocks a major threat."""
        score = self.evaluate(test_board)
        if abs(score) > 8_000:
            return True
        return abs(score - self.evaluate(board)) > 5_000

    def _sort_boards_by_priority(
        self, boards: list[Board], base_board: Board, *, is_maximizing: bool
    ) -> list[Board]:
        critical: list[Board] = []
        normal: list[Board] = []
        for candidate in boards:
            target = (
                critical
                if self._is_critical_position(base_board, candidate)
                else normal
            )
            target.append(candidate)

        # Critical moves are searched first; the rest are ordered by raw score.
        critical.sort(key=self.evaluate, reverse=is_maximizing)
        normal.sort(key=self.evaluate, reverse=is_maximizing)
        return critical + normal

    def best_next(
        self,
        board: Board,
        depth: int,
        parent_alpha: int | None = None,
        parent_beta: int | None = None,
    ) -> tuple[int, Board]:
        subs: list[tuple[int, Board]] = []
        is_maximizing = depth % 2 == 1
        alpha: int | None = None
        beta: int | None = None

        sub_boards = list(board.next_boards())
        if depth != self.max_depth and len(sub_boards) > 1:
            sub_boards = self._sort_boards_by_priority(
                sub_boards, board, is_maximizing=is_maximizing
            )

        for candidate in sub_boards:
            if depth == self.max_depth:
                score = self.evaluate(candidate)
            else:
                score, _ = self.best_next(candidate, depth + 1, alpha, beta)
            subs.append((score, candidate))

            if is_maximizing:
                alpha = score if alpha is None else max(alpha, score)
                if parent_beta is not None and alpha >= parent_beta:
                    break
            else:
                beta = score if beta is None else min(beta, score)
                if parent_alpha is not None and beta <= parent_alpha:
                    break

        if not subs:
            return 0, board
        select = max if is_maximizing else min
        return select(subs, key=lambda sb: sb[0])


def winner(board: Board) -> Color | None:
    """Return the color of the winner, or ``None`` if the game is ongoing."""
    stones = {p.pos: p for p in board.pieces}
    for (x, y), piece in stones.items():
        for dx, dy in DIRECTIONS:
            count = 1
            count += _count_direction(stones, x, y, dx, dy, piece.color)
            count += _count_direction(stones, x, y, -dx, -dy, piece.color)
            if count >= 5:
                return piece.color
    return None


def _count_direction(
    stones: dict[Position, Piece],
    x: int,
    y: int,
    dx: int,
    dy: int,
    color: Color,
) -> int:
    count = 0
    for i in range(1, 5):
        piece = stones.get((x + i * dx, y + i * dy))
        if piece is None or piece.color != color:
            break
        count += 1
    return count
