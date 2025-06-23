import functools
import datetime
from typing import Tuple, List, Optional, Dict
from .board import Board, Piece


class Evaluator:
    DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]
    
    PATTERN_SCORES = {
        (1, 1, 1, 1, 1): 100000,  # 连五
        (0, 1, 1, 1, 1, 0): 10000,  # 活四
        (1, 1, 1, 1, 0): 1000,   # 冲四
        (0, 1, 1, 1, 1): 1000,   # 冲四
        (1, 0, 1, 1, 1): 1000,   # 跳冲四
        (1, 1, 0, 1, 1): 1000,   # 跳冲四
        (1, 1, 1, 0, 1): 1000,   # 跳冲四
        (0, 1, 1, 1, 0): 800,    # 活三
        (0, 0, 1, 1, 1, 0, 0): 800,  # 活三
        (1, 1, 1, 0, 0): 200,    # 眠三
        (0, 0, 1, 1, 1): 200,    # 眠三
        (1, 0, 1, 1, 0): 200,    # 跳眠三
        (0, 1, 1, 0, 1): 200,    # 跳眠三
        (0, 1, 1, 0, 0): 50,     # 活二
        (0, 0, 1, 1, 0): 50,     # 活二
        (1, 1, 0, 0, 0): 10,     # 眠二
        (0, 0, 0, 1, 1): 10,     # 眠二
        (1, 0, 1, 0, 0): 10,     # 跳眠二
        (0, 0, 1, 0, 1): 10,     # 跳眠二
    }

    def __init__(self, color):
        self.color = color
        self.count = 0
        self._cache = {}

    def __call__(self, board: Board) -> int:
        board_hash = hash(tuple(sorted((x, y, p.color if p else None) for x, y, p in board.iter_position())))
        if board_hash in self._cache:
            return self._cache[board_hash]
        
        mine_score = self._evaluate_color(board, self.color)
        peer_color = 'b' if self.color == 'w' else 'w'
        peer_score = self._evaluate_color(board, peer_color)
        
        result = mine_score - int(peer_score * 1.2)
        self._cache[board_hash] = result
        self.count += 1
        return result

    def _evaluate_color(self, board: Board, color: str) -> int:
        total_score = 0
        board_dict = {(x, y): p for x, y, p in board.iter_position()}
        
        for x, y, piece in board.iter_position():
            if piece and piece.color == color:
                for dx, dy in self.DIRECTIONS:
                    line_score = self._evaluate_line_from_position(board_dict, x, y, dx, dy, color)
                    total_score += line_score
        
        return total_score

    def _evaluate_line_from_position(self, board_dict: Dict, x: int, y: int, dx: int, dy: int, color: str) -> int:
        line = []
        
        for i in range(-4, 5):
            nx, ny = x + i * dx, y + i * dy
            piece = board_dict.get((nx, ny))
            if piece and piece.color == color:
                line.append(1)
            elif piece and piece.color != color:
                line.append(-1)
            else:
                line.append(0)
        
        return self._pattern_match_score(tuple(line))

    @functools.lru_cache(maxsize=10000)
    def _pattern_match_score(self, line: Tuple[int, ...]) -> int:
        if len(line) < 5:
            return 0
        
        score = 0
        
        for pattern, pattern_score in self.PATTERN_SCORES.items():
            score += self._count_pattern_matches(line, pattern) * pattern_score
        
        consecutive_count = self._max_consecutive(line)
        if consecutive_count >= 2:
            score += consecutive_count ** 3
        
        return score

    def _count_pattern_matches(self, line: Tuple[int, ...], pattern: Tuple[int, ...]) -> int:
        count = 0
        for i in range(len(line) - len(pattern) + 1):
            if line[i:i+len(pattern)] == pattern:
                count += 1
        return count

    def _max_consecutive(self, line: Tuple[int, ...]) -> int:
        max_count = 0
        current_count = 0
        
        for val in line:
            if val == 1:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
        
        return max_count


class MMSearch:
    color: str
    max_depth: int
    evaluate: Evaluator

    def __init__(self, color: str, max_depth: int):
        self.color = color
        self.max_depth = max_depth
        self.evaluate = Evaluator(color)

    def __call__(self, board: Board) -> Tuple[Board, datetime.timedelta]:
        startat = datetime.datetime.now()
        self.evaluate.count = 0
        s, b = self.best_next(board, depth=1)
        endat = datetime.datetime.now()
        print(f'Evaluate {self.evaluate.count} times, using {endat - startat}')
        return b, endat - startat

    @property
    def iter_times(self):
        return self.evaluate.count

    def best_next(self, board: Board, depth: int,
                  parent_alpha: Optional[int] = None,
                  parent_beta: Optional[int] = None):
        # print(f'>>> {depth} {parent_alpha} {parent_beta}')
        subs = []
        select = max if depth % 2 == 1 else min
        alpha, beta = None, None
        sub_boards = board.next_boards()
        if depth != self.max_depth:
            # 这里的排序是为了 alpha-beta 剪枝更有效
            sub_boards = sorted(sub_boards,
                                key=self.evaluate,
                                reverse=(select is max))
        for b in sub_boards:
            if depth == self.max_depth:
                s = self.evaluate(b)
            else:
                s, _ = self.best_next(b, depth+1, alpha, beta)
            subs.append((s, b))
            if select is max:
                if alpha is None or s > alpha:
                    alpha = s
                if parent_beta is not None and alpha >= parent_beta:
                    # print(f">>> Break on {alpha} >= {parent_beta}")
                    break
            else:
                if beta is None or s < beta:
                    beta = s
                if parent_alpha is not None and beta <= parent_alpha:
                    # print(f">>> Break on {beta} <= {parent_alpha}")
                    break
        return select(subs, key=lambda sb: sb[0])


def winner(board: Board) -> str:
    pass
