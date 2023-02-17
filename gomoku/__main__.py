from .board import Board
from .tui import TUI


b = Board((15, 15))
ui = TUI()

while True:
    print(ui.render(b))
    x, y = input('Go [x y]:').split()
    b = b.add(int(x), int(y))
