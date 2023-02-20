import tkinter as tk
from .board import Board, Piece
from .score import MMSearch


class App(tk.Frame):

    def __init__(self, canvassize=600, boardsize=7):
        super(App, self).__init__()
        self.canvassize = canvassize
        self.grid()
        self.init_canvas()
        self.current = Board(size=(boardsize, boardsize))
        self.padding = canvassize / 10
        self.interval = (canvassize - self.padding * 2) / (boardsize - 1)
        self.render_board(self.current)
        self.init_game()

    def init_game(self):
        x = self.current.size[0] // 2
        y = self.current.size[1] // 2
        self.current = self.current.add(x, y)
        self.render_peice(self.current.last_piece)

    def init_canvas(self):
        self.canvas = tk.Canvas(
            self, width=self.canvassize, height=self.canvassize,
            background='#b85')
        self.canvas.grid()
        self.canvas.bind('<Button-1>', self._on_click)

    def _on_click(self, event):
        print(f'Click at: {event.x} {event.y}')
        try:
            x = next(filter(
                lambda x: abs(event.x - x[0]) < self.interval * 0.4,
                self.x_positions
            ))
            y = next(filter(
                lambda y: abs(event.y - y[0]) < self.interval * 0.4,
                self.y_positions
            ))
        except StopIteration:
            pass
        else:
            print(f'Nearest: {x} {y}')
            self.current = self.current.add(x[1], y[1])
            self.render_peice(self.current.last_piece)
            mm = MMSearch(self.current.next_color, 4)
            self.current = mm(self.current)
            self.render_peice(self.current.last_piece)

    def render_board(self, board: Board):
        self.x_positions, self.y_positions = [], []
        for i in range(board.size[0]):
            start_x = end_x = self.interval * i + self.padding
            start_y = self.padding
            end_y = start_y + (self.interval * (board.size[1] - 1))
            self.canvas.create_line(start_x, start_y, end_x, end_y,
                                    fill='#222', width=2)
            self.x_positions.append((start_x, i))

        for i in range(board.size[1]):
            start_y = end_y = self.interval * i + self.padding
            start_x = self.padding
            end_x = start_x + (self.interval * (board.size[0] - 1))
            self.canvas.create_line(start_x, start_y, end_x, end_y,
                                    fill='#222', width=2)
            self.y_positions.append((start_y, i))

    def render_peice(self, piece: Piece):
        print(f'Render {piece}')
        fill = 'pink' if piece.color == 'w' else '#222'
        size = self.interval * 0.9
        x0 = self.padding + self.interval * piece.x
        y0 = self.padding + self.interval * piece.y
        x1 = x0 - size * 0.5
        x2 = x0 + size * 0.5
        y1 = y0 - size * 0.5
        y2 = y0 + size * 0.5
        self.canvas.create_oval(x1, y1, x2, y2,
                                outline='gray', width=1, fill=fill)
