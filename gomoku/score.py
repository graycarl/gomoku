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

    def _is_critical_position(self, board: Board, test_board: Board) -> bool:
        """检测是否为关键位置（能形成重大威胁或防守关键威胁）"""
        score = self.evaluate(test_board)
        
        # 检查是否能形成连五（绝对获胜）
        if abs(score) > 80000:
            return True
            
        # 检查是否能形成活四（强威胁）
        if abs(score) > 8000:
            return True
        
        # 检查是否能阻止对手的威胁
        # 通过比较当前局面和下子后的局面来判断
        current_score = self.evaluate(board)
        score_diff = abs(score - current_score)
        
        # 如果分数变化很大，说明这是关键位置
        if score_diff > 5000:
            return True
            
        return False

    def _sort_boards_by_priority(self, boards: List[Board], base_board: Board, is_maximizing: bool) -> List[Board]:
        """根据优先级对棋盘进行排序"""
        if len(boards) <= 1:
            return boards
        
        critical_boards = []
        normal_boards = []
        
        # 分离关键和普通位置
        for board in boards:
            if self._is_critical_position(base_board, board):
                critical_boards.append(board)
            else:
                normal_boards.append(board)
        
        # 对关键位置进行评估排序
        if critical_boards:
            critical_boards = sorted(critical_boards, 
                                   key=self.evaluate, 
                                   reverse=is_maximizing)
        
        # 对普通位置进行简单排序（较少评估）
        if normal_boards:
            normal_boards = sorted(normal_boards, 
                                 key=self.evaluate, 
                                 reverse=is_maximizing)
        
        # 关键位置优先
        return critical_boards + normal_boards

    def best_next(self, board: Board, depth: int,
                  parent_alpha: Optional[int] = None,
                  parent_beta: Optional[int] = None):
        subs = []
        select = max if depth % 2 == 1 else min
        is_maximizing = (select is max)
        alpha, beta = None, None
        
        # 获取候选棋盘（现在已经通过board.next_boards()进行了空间缩减）
        sub_boards = list(board.next_boards())
        
        # 智能排序：关键位置优先，然后按评估值排序
        if depth != self.max_depth and len(sub_boards) > 1:
            sub_boards = self._sort_boards_by_priority(sub_boards, board, is_maximizing)
        
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
                    break
            else:
                if beta is None or s < beta:
                    beta = s
                if parent_alpha is not None and beta <= parent_alpha:
                    break
        
        return select(subs, key=lambda sb: sb[0]) if subs else (0, board)


def winner(board: Board) -> Optional[str]:
    """检查是否有获胜者，返回获胜者颜色或None"""
    if not board.pieces:
        return None
    
    board_dict = {(x, y): p for x, y, p in board.iter_position()}
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    
    for x, y, piece in board.iter_position():
        if piece:
            for dx, dy in directions:
                count = 1
                # 向正方向检查
                for i in range(1, 5):
                    nx, ny = x + i * dx, y + i * dy
                    next_piece = board_dict.get((nx, ny))
                    if next_piece and next_piece.color == piece.color:
                        count += 1
                    else:
                        break
                
                # 向负方向检查
                for i in range(1, 5):
                    nx, ny = x - i * dx, y - i * dy
                    prev_piece = board_dict.get((nx, ny))
                    if prev_piece and prev_piece.color == piece.color:
                        count += 1
                    else:
                        break
                
                if count >= 5:
                    return piece.color
    
    return None
