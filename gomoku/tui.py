from .board import Board


class TUI:
    js = ' | '

    def render(self, board: Board) -> str:
        lines = []
        for y in range(board.size[1]):
            line = []
            for x in range(board.size[0]):
                p = board.get(x, y)
                if not p:
                    line.append(' ')
                else:
                    line.append('X' if p.color == 'b' else 'O')
            lines.append(self.js.join(line))
        return '\n'.join(lines)
