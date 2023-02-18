import sys
from .board import Board
from . import tui, gui


b = Board((15, 15))

if len(sys.argv) == 2 and sys.argv[1] == 'tui':
    ui = tui.TUI()
    while True:
        print(ui.render(b))
        x, y = input('Go [x y]:').split()
        b = b.add(int(x), int(y))
else:
    app = gui.App()
    app.mainloop()