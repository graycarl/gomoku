"""Tkinter user interface for the Gomoku board."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox

from .board import Board, Piece
from .tcl import configure_tcl_environment


class UIEvent:
    """Base class for events emitted by the UI."""


class BoardClick(UIEvent):
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class Tick(UIEvent):
    """Periodic timer event used to poll the AI worker."""


class GUI:
    """Wraps a Tk window, board canvas, control panel and log area."""

    def __init__(self, canvassize: int, on_event: Callable[[UIEvent], None]) -> None:
        self.canvassize = canvassize
        self.on_event = on_event
        self.padding = canvassize / 10
        self.interval = 0.0
        self.x_positions: list[tuple[float, int]] = []
        self.y_positions: list[tuple[float, int]] = []

        configure_tcl_environment()
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root, background="gray")
        self.frame.grid(column=0, row=0)
        self.frame.grid_rowconfigure(1, weight=1)
        self.canvas = self.__init_canvas(self.frame, canvassize)
        self.__init_controllers(self.frame)
        self.logarea = self.__init_logarea(self.frame)
        self.__schedule_tick(15)

    def __init_canvas(self, frame: tk.Frame, canvassize: int) -> tk.Canvas:
        canvas = tk.Canvas(
            frame,
            width=canvassize,
            height=canvassize,
            background="#b85",
            highlightbackground="gray",
        )
        canvas.grid(column=0, row=0, rowspan=2)
        canvas.bind("<Button-1>", self.__canvas_click)
        return canvas

    def __canvas_click(self, event: tk.Event) -> None:
        x = self.__nearest(event.x, self.x_positions)
        y = self.__nearest(event.y, self.y_positions)
        if x is not None and y is not None:
            self.on_event(BoardClick(x, y))

    def __nearest(self, value: int, positions: list[tuple[float, int]]) -> int | None:
        for coordinate, index in positions:
            if abs(value - coordinate) < self.interval * 0.4:
                return index
        return None

    def __schedule_tick(self, timeout: int) -> None:
        def tick() -> None:
            self.on_event(Tick())
            self.root.after(timeout, tick)

        self.root.after(timeout, tick)

    def __init_controllers(self, frame: tk.Frame) -> tk.LabelFrame:
        controls = tk.LabelFrame(
            frame, text="Control Panel", width=300, height=200, background="gray"
        )
        controls.grid(column=1, row=0, padx=2, pady=4)
        return controls

    def __init_logarea(self, frame: tk.Frame) -> tk.Text:
        logarea = tk.Text(frame, background="gray", wrap="word", width=40)
        logarea.grid(column=1, row=1, padx=2, pady=4, sticky=(tk.N, tk.S, tk.E, tk.W))
        return logarea

    def init_board(self, board: Board) -> None:
        assert board.size[0] == board.size[1]
        bsize = board.size[0]
        self.interval = (self.canvassize - self.padding * 2) / (bsize - 1)
        self.x_positions, self.y_positions = [], []

        for i in range(board.size[0]):
            x = self.interval * i + self.padding
            self.canvas.create_line(
                x,
                self.padding,
                x,
                self.padding + self.interval * (board.size[1] - 1),
                fill="#222",
                width=2,
            )
            self.x_positions.append((x, i))

        for i in range(board.size[1]):
            y = self.interval * i + self.padding
            self.canvas.create_line(
                self.padding,
                y,
                self.padding + self.interval * (board.size[0] - 1),
                y,
                fill="#222",
                width=2,
            )
            self.y_positions.append((y, i))

        for piece in board.pieces:
            self.render_piece(piece)

    def render_piece(self, piece: Piece) -> None:
        fill = "pink" if piece.color == "w" else "#222"
        size = self.interval * 0.9
        cx = self.padding + self.interval * piece.x
        cy = self.padding + self.interval * piece.y
        half = size * 0.5
        self.canvas.create_oval(
            cx - half,
            cy - half,
            cx + half,
            cy + half,
            outline="gray",
            width=1,
            fill=fill,
        )

    def log_message(self, message: str, *, amend: bool = False) -> None:
        if amend:
            start = self.logarea.index("end-2l linestart")
            self.logarea.delete(start, "end-1c")
        self.logarea.insert("end", message + "\n")
        self.logarea.see("end")

    def show_winner_dialog(self, winner_color: str) -> None:
        winner_name = "黑棋" if winner_color == "b" else "白棋"
        messagebox.showinfo("游戏结束", f"游戏结束！{winner_name}获胜！")

    def mainloop(self) -> None:
        self.root.mainloop()
