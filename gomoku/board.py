import random
from dataclasses import dataclass
from typing import Optional, Tuple, Iterator, List


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

    def get_candidate_positions(self, radius: int = 2) -> List[Tuple[int, int]]:
        """获取候选位置：只考虑已有子周围的位置"""
        if not self.pieces:
            # 空棋盘时，从中心开始
            center_x, center_y = self.size[0] // 2, self.size[1] // 2
            return [(center_x, center_y)]
        
        candidates = set()
        occupied = {(p.x, p.y) for p in self.pieces}
        
        # 在所有已有子的周围radius格范围内寻找候选位置
        for piece in self.pieces:
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if dx == 0 and dy == 0:
                        continue
                    x, y = piece.x + dx, piece.y + dy
                    if (0 <= x < self.size[0] and 0 <= y < self.size[1] and 
                        (x, y) not in occupied):
                        candidates.add((x, y))
        
        return list(candidates)

    def next_boards(self) -> Iterator['Board']:
        # 使用候选位置过滤来大幅减少搜索空间
        candidate_positions = self.get_candidate_positions()
        random.shuffle(candidate_positions)
        
        for x, y in candidate_positions:
            yield self.add(x, y)
