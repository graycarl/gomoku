"""Immutable board representation and game rules."""

from __future__ import annotations

import random
from collections.abc import Iterator
from dataclasses import dataclass

type Color = str
type Position = tuple[int, int]

DIRECTIONS: tuple[Position, ...] = ((1, 0), (0, 1), (1, 1), (1, -1))


def other(color: Color) -> Color:
    """Return the opponent color."""
    return "w" if color == "b" else "b"


@dataclass(frozen=True, slots=True)
class Piece:
    color: Color
    x: int
    y: int

    @property
    def pos(self) -> Position:
        return (self.x, self.y)


@dataclass(frozen=True, slots=True)
class Board:
    size: Position
    pieces: tuple[Piece, ...] = ()
    step: int = 0

    @property
    def next_color(self) -> Color:
        if not self.pieces:
            return "b"
        return other(self.pieces[-1].color)

    @property
    def last_piece(self) -> Piece:
        return self.pieces[-1]

    def add(self, x: int, y: int) -> Board:
        pos = (x, y)
        if pos in {p.pos for p in self.pieces}:
            raise RuntimeError(f"Position {pos} already has piece.")
        piece = Piece(self.next_color, x, y)
        return Board(self.size, (*self.pieces, piece), self.step + 1)

    def iter_position(self) -> Iterator[tuple[int, int, Piece | None]]:
        lookup = {p.pos: p for p in self.pieces}
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                yield (x, y, lookup.get((x, y)))

    def get_candidate_positions(self, radius: int = 2) -> list[Position]:
        """Return empty positions within ``radius`` of any existing piece."""
        if not self.pieces:
            return [(self.size[0] // 2, self.size[1] // 2)]

        occupied = {p.pos for p in self.pieces}
        candidates: set[Position] = set()
        for piece in self.pieces:
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    x, y = piece.x + dx, piece.y + dy
                    if (dx or dy) and self.contains(x, y) and (x, y) not in occupied:
                        candidates.add((x, y))
        return list(candidates)

    def contains(self, x: int, y: int) -> bool:
        return 0 <= x < self.size[0] and 0 <= y < self.size[1]

    def next_boards(self) -> Iterator[Board]:
        """Yield boards for every candidate move, in random order."""
        candidates = self.get_candidate_positions()
        random.shuffle(candidates)
        for x, y in candidates:
            yield self.add(x, y)
