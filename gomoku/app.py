import cProfile
import contextlib
import pathlib
from concurrent import futures
from .board import Board
from .score import MMSearch
from . import ui


class App:

    def __init__(self, canvassize=600, boardsize=7, profile=False):
        self.profile = profile
        self.ui = ui.GUI(canvassize, self.on_event)
        self.thinking = None
        self.thinking_executor = futures.ThreadPoolExecutor(max_workers=1)
        self.init_game(boardsize)

    def run(self):
        self.ui.mainloop()

    def init_game(self, boardsize):
        self.current = Board(size=(boardsize, boardsize))
        x = self.current.size[0] // 2
        y = self.current.size[1] // 2
        self.current = self.current.add(x, y)
        self.ui.init_board(self.current)

    @contextlib.contextmanager
    def maybe_profile(self):
        path = pathlib.Path(f'/tmp/gomoku/profile.{self.current.step}.prf')
        path.parent.mkdir(exist_ok=True)
        if self.profile:
            pf = cProfile.Profile()
            pf.enable()
            yield
            pf.disable()
            pf.dump_stats(path)
            print(f'Profile: {path}')
        else:
            yield

    def think(self):
        assert self.thinking is None
        mm = MMSearch(self.current.next_color, 3)
        self.thinking = self.thinking_executor.submit(lambda: mm(self.current))

    def on_event(self, event: ui.UIEvent):
        if isinstance(event, ui.BoardClick):
            if self.thinking:
                return
            self.current = self.current.add(event.x, event.y)
            self.ui.render_piece(self.current.last_piece)
            self.think()
        elif isinstance(event, ui.Tick):
            if self.thinking:
                if not self.thinking.done():
                    print('Still thinking ...')
                else:
                    print('Think done')
                    self.current = self.thinking.result()
                    self.thinking = None
                    self.ui.render_piece(self.current.last_piece)
