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

    @property
    def next_color(self) -> str:
        try:
            latest = self.pieces[-1].color
        except IndexError:
            return 'b'
        else:
            return 'w' if latest == 'b' else 'b'

    def add(self, x: int, y: int) -> 'Board':
        pos = (x, y)
        if any(map(lambda p: p.pos == pos, self.pieces)):
            raise RuntimeError(f'Position {pos} already has piece.')
        p = Piece(self.next_color, x, y)
        return Board(self.size, self.pieces + (p,))

    def get(self, x: int, y: int) -> Optional[Piece]:
        for p in self.pieces:
            if p.pos == (x, y):
                return p
        return None

    def iter_position(self) -> Iterator[Tuple[int, int, Optional[Piece]]]:
        lookup = {(p.x, p.y): p for p in self.pieces}
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                if (x, y) in lookup:
                    yield (x, y, lookup[(x, y)])
                else:
                    yield (x, y, None)

    def next_boards(self) -> Iterator['Board']:
        for x, y, p in self.iter_position():
            if not p:
                yield self.add(x, y)
