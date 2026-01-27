import contextlib
import cProfile
import pathlib
from concurrent import futures

from . import ui
from .board import Board
from .score import MMSearch, winner


class App:
    """
    App 类是一个五子棋游戏的主程序，负责管理游戏的逻辑、用户界面和 AI 思考。

    属性:
        profile (bool): 是否启用性能分析。
        ui (ui.GUI): 用户界面对象，用于渲染棋盘和处理用户交互。
        thinking (concurrent.futures.Future): 当前 AI 思考的异步任务。
        thinking_executor (concurrent.futures.ThreadPoolExecutor): 用于执行 AI 思考的线程池。
        game_ended (bool): 游戏是否已经结束。
        current (Board): 当前的棋盘状态。
        mmsearch (MMSearch): AI 的搜索算法实例。

    方法:
        __init__: 初始化 App 类的实例。
        run: 启动用户界面主循环。
        init_game: 初始化游戏状态，包括棋盘和 AI。
        maybe_profile: 上下文管理器，用于在启用性能分析时记录性能数据。
        check_game_end: 检查游戏是否结束，并在结束时显示获胜者弹窗。
        think: 触发 AI 的思考过程。
        on_event: 处理用户界面事件，例如棋盘点击和定时器事件。
    """

    def __init__(self, canvassize=600, boardsize=7, profile=False):
        self.profile = profile
        self.ui = ui.GUI(canvassize, self.on_event)
        self.thinking = None
        self.thinking_executor = futures.ThreadPoolExecutor(max_workers=1)
        self.game_ended = False
        self.init_game(boardsize)

    def run(self):
        self.ui.mainloop()

    def init_game(self, boardsize):
        self.current = Board(size=(boardsize, boardsize))
        x = self.current.size[0] // 2
        y = self.current.size[1] // 2
        self.mmsearch = MMSearch("b", 3)
        self.current = self.current.add(x, y)
        self.game_ended = False
        self.ui.init_board(self.current)
        self.ui.log_message("Init game done.")

    @contextlib.contextmanager
    def maybe_profile(self):
        path = pathlib.Path(f"/tmp/gomoku/profile.{self.current.step}.prf")
        path.parent.mkdir(exist_ok=True)
        if self.profile:
            pf = cProfile.Profile()
            pf.enable()
            yield
            pf.disable()
            pf.dump_stats(path)
            print(f"Profile: {path}")
        else:
            yield

    def check_game_end(self):
        """检查游戏是否结束并显示弹窗"""
        game_winner = winner(self.current)
        if game_winner:
            self.game_ended = True
            self.ui.show_winner_dialog(game_winner)
            return True
        return False

    def think(self):
        assert self.thinking is None
        self.thinking = self.thinking_executor.submit(
            lambda: self.mmsearch(self.current)
        )
        self.ui.log_message("Thinking...")

    def on_event(self, event: ui.UIEvent):
        if isinstance(event, ui.BoardClick):
            if self.thinking or self.game_ended:
                return
            try:
                self.current = self.current.add(event.x, event.y)
                p = self.current.last_piece
                self.ui.render_piece(p)
                self.ui.log_message(f"You put on {p}")

                # 检查玩家是否获胜
                if self.check_game_end():
                    return

                self.think()
            except RuntimeError as e:
                self.ui.log_message(f"Invalid move: {e}")
        elif isinstance(event, ui.Tick):
            if self.thinking:
                if not self.thinking.done():
                    self.ui.log_message(
                        f"Thinking ... {self.mmsearch.iter_times}", amend=True
                    )
                else:
                    self.current, time = self.thinking.result()
                    self.ui.log_message(
                        f"Thinking ... {self.mmsearch.iter_times} "
                        f"Using {time.total_seconds():.2f}s",
                        amend=True,
                    )
                    p = self.current.last_piece
                    self.thinking = None
                    self.ui.render_piece(p)
                    self.ui.log_message(f"AI put on {p}")

                    # 检查AI是否获胜
                    self.check_game_end()
