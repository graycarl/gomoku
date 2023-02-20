from .board import Board, Piece
from typing import Tuple, List, Optional, Dict


class Evaluator:
    offsets = {
        'heng': lambda p, o: (p.x + o, p.y),
        'shu': lambda p, o: (p.x, p.y + o),
        'pie': lambda p, o: (p.x - o, p.y + o),
        'na': lambda p, o: (p.x + o, p.y + o),
    }

    def __init__(self, color):
        self.color = color

    def __call__(self, board: Board) -> int:
        matrix = {(x, y): p for x, y, p in board.iter_position()}
        mine_score = self._color_score(matrix, self.color)
        peer_color = 'b' if self.color == 'w' else 'w'
        peer_score = self._color_score(matrix, peer_color)
        return mine_score - peer_score

    def _color_score(self,
                     matrix: Dict[Tuple[int, int], Optional[Piece]],
                     color: str) -> int:
        pieces = filter(lambda p: p and p.color == color, matrix.values())
        print(f'>> _color_score: {color}')
        scores = {}
        for p in pieces:
            p_score = 0
            for name, func in self.offsets.items():
                line: List[Optional[Piece]] = []
                for o in (-1, -2, -3, -4):
                    try:
                        op = matrix[func(p, o)]
                    except KeyError:
                        break
                    else:
                        if op and op.color != color:
                            break
                    line.insert(0, op)
                line.append(p)
                for o in (1, 2, 3, 4):
                    try:
                        op = matrix[func(p, o)]
                    except KeyError:
                        break
                    else:
                        if op and op.color != color:
                            break
                    line.append(op)
                if len(line) < 5:
                    continue
                p_score += self._eval_line(line)
        scores[p] = p_score
        return sum(scores.values())

    def _eval_line(self, line: List[Optional[Piece]]):
        if len(line) < 5:
            return 0
        score = 0
        for shift in range(len(line) - 5 + 1):
            pieces = line[shift:shift+5]
            score += self._eval_five(pieces)
        # print(f'eval_line: {score} -- {line}')
        return score

    def _eval_five(self, pieces: List[Optional[Piece]]):
        count = 0
        continus, max_countinus = 0, 0
        for p in pieces:
            if p:
                continus += 1
                count += 1
            else:
                continus = 0
            max_countinus = max(continus, max_countinus)
        if max_countinus == 5:
            return 9999
        return count + (max_countinus * max_countinus * max_countinus)


class MMSearch:
    color: str
    max_depth: int
    evaluate: Evaluator

    def __init__(self, color: str, max_depth: int):
        self.color = color
        self.max_depth = max_depth
        self.evaluate = Evaluator(color)

    def __call__(self, board: Board) -> Board:
        self.eval_count = 0
        s, b = self.best_next(board, depth=1)
        print(f'Evaluate {self.eval_count} times')
        return b

    def best_next(self, board: Board, depth: int,
                  parent_alpha: Optional[int] = None,
                  parent_beta: Optional[int] = None):
        print(f'>>> {depth} {parent_alpha} {parent_beta}')
        subs = []
        select = max if depth % 2 == 1 else min
        alpha, beta = None, None
        for b in board.next_boards():
            if depth == self.max_depth:
                self.eval_count += 1
                s = self.evaluate(b)
            else:
                s, _ = self.best_next(b, depth+1, alpha, beta)
            subs.append((s, b))
            if select is max:
                if alpha is None or s > alpha:
                    alpha = s
                if parent_beta is not None and alpha >= parent_beta:
                    print(f">>> Break on {alpha} >= {parent_beta}")
                    break
            else:
                if beta is None or s < beta:
                    beta = s
                if parent_alpha is not None and beta <= parent_alpha:
                    print(f">>> Break on {beta} <= {parent_alpha}")
                    break
        return select(subs, key=lambda sb: sb[0])


def winner(board: Board) -> str:
    pass
