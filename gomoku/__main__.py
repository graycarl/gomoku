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
    profile = ('-p' in sys.argv)
    if sys.argv[1].isnumeric():
        app = gui.App(boardsize=int(sys.argv[1]), profile=profile)
    else:
        app = gui.App(profile=profile)
    app.mainloop()
