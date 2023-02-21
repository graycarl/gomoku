import random
from dataclasses import dataclass
from typing import Optional, Tuple, Iterator


@dataclass(frozen=True)
class Piece:
    color: str
    x: int
    y: int

    @property
    def pos(self):
        return (self.x, self.y)


@dataclass(frozen=True)
class Board:
    size: Tuple[int, int]
    pieces: Tuple[Piece, ...] = ()
    step: int = 0

    @property
    def next_color(self) -> str:
        try:
            latest = self.pieces[-1].color
        except IndexError:
            return 'b'
        else:
            return 'w' if latest == 'b' else 'b'

    @property
    def last_piece(self) -> Piece:
        return self.pieces[-1]

    def add(self, x: int, y: int) -> 'Board':
        pos = (x, y)
        if any(map(lambda p: p.pos == pos, self.pieces)):
            raise RuntimeError(f'Position {pos} already has piece.')
        p = Piece(self.next_color, x, y)
        return Board(self.size, self.pieces + (p,), step=self.step + 1)

    def iter_position(self) -> Iterator[Tuple[int, int, Optional[Piece]]]:
        lookup = {(p.x, p.y): p for p in self.pieces}
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                if (x, y) in lookup:
                    yield (x, y, lookup[(x, y)])
                else:
                    yield (x, y, None)

    def next_boards(self) -> Iterator['Board']:
        positions = list(self.iter_position())
        random.shuffle(positions)
        for x, y, p in positions:
            if not p:
                yield self.add(x, y)
