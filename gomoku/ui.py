import tkinter as tk
from tkinter import messagebox
from .board import Board, Piece


class UIEvent:
    pass


class BoardClick(UIEvent):

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Tick(UIEvent):
    pass


class GUI:

    def __init__(self, canvassize, on_event):
        self.canvassize = canvassize
        self.on_event = on_event
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root, background='gray')
        self.frame.grid(column=0, row=0)
        self.frame.grid_rowconfigure(1, weight=1)
        self.padding = canvassize / 10
        self.canvas = self.__init_canvas(self.frame, canvassize)
        self.__init_controllers(self.frame)
        self.logarea = self.__init_logarea(self.frame)
        self.__init_tick(15)

    def __init_canvas(self, frame, canvassize):
        canvas = tk.Canvas(
            self.frame, width=canvassize, height=canvassize,
            background='#b85', highlightbackground='gray')
        canvas.grid(column=0, row=0, rowspan=2)
        canvas.bind('<Button-1>', self.__canvas_click)
        return canvas

    def __canvas_click(self, event):
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
            self.on_event(BoardClick(x[1], y[1]))

    def __init_tick(self, timeout):
        def tick():
            self.on_event(Tick())
            self.root.after(timeout, tick)
        self.root.after(timeout, tick)

    def __init_controllers(self, frame):
        cs = tk.LabelFrame(
            frame, text='Control Panel',
            width=300, height=200, background='gray')
        cs.grid(column=1, row=0, padx=2, pady=4)
        return cs

    def __init_logarea(self, frame):
        logarea = tk.Text(frame, background='gray', wrap='word', width=40)
        logarea.grid(column=1, row=1, padx=2, pady=4,
                     sticky=(tk.N, tk.S, tk.E, tk.W))
        return logarea

    def init_board(self, board: Board):
        self.x_positions, self.y_positions = [], []
        assert board.size[0] == board.size[1]
        bsize = board.size[0]
        self.interval = (self.canvassize - self.padding * 2) / (bsize - 1)
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

        for p in board.pieces:
            self.render_piece(p)

    def render_piece(self, piece: Piece):
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

    def log_message(self, message, amend=False):
        if amend:
            s = self.logarea.index('end-2l linestart')
            self.logarea.delete(s, 'end-1c')
        self.logarea.insert('end', message + '\n')
        self.logarea.see('end')


    def show_winner_dialog(self, winner_color):
        """显示获胜者弹窗"""
        winner_name = "黑棋" if winner_color == 'b' else "白棋"
        message = f"游戏结束！{winner_name}获胜！"
        messagebox.showinfo("游戏结束", message)

    def mainloop(self):
        self.root.mainloop()
