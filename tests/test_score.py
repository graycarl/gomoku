from gomoku.board import Board
from gomoku.score import Evaluator, pattern_match_score, winner

BLACK_WIN = [
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
    (2, 0),
    (2, 1),
    (3, 0),
    (3, 1),
    (4, 0),
]


def build_board(moves: list[tuple[int, int]], size: tuple[int, int] = (9, 9)) -> Board:
    board = Board(size=size)
    for x, y in moves:
        board = board.add(x, y)
    return board


def test_winner_detects_horizontal_five() -> None:
    assert winner(build_board(BLACK_WIN)) == "b"


def test_winner_detects_vertical_five() -> None:
    moves = [
        (0, 0),
        (5, 5),
        (0, 1),
        (5, 6),
        (0, 2),
        (5, 7),
        (0, 3),
        (5, 8),
        (0, 4),
    ]
    assert winner(build_board(moves)) == "b"


def test_winner_detects_diagonal_five() -> None:
    moves = [
        (0, 0),
        (8, 0),
        (1, 1),
        (8, 1),
        (2, 2),
        (8, 2),
        (3, 3),
        (8, 3),
        (4, 4),
    ]
    assert winner(build_board(moves)) == "b"


def test_no_winner_for_short_run() -> None:
    assert winner(build_board([(0, 0), (0, 1), (1, 0), (1, 1)])) is None


def test_no_winner_on_empty_board() -> None:
    assert winner(Board(size=(5, 5))) is None


def test_pattern_match_scores_five_in_a_row_highest() -> None:
    five = pattern_match_score((1, 1, 1, 1, 1))
    open_four = pattern_match_score((0, 1, 1, 1, 1, 0))
    empty = pattern_match_score((0, 0, 0, 0, 0))
    assert five > open_four > empty == 0


def test_evaluator_is_zero_for_empty_board() -> None:
    assert Evaluator("b")(Board(size=(7, 7))) == 0


def test_evaluator_is_zero_for_a_single_stone() -> None:
    # A lone stone matches no pattern on its own.
    assert Evaluator("b")(Board(size=(9, 9)).add(4, 4)) == 0


def test_evaluator_favors_the_color_with_the_better_position() -> None:
    board = Board(size=(9, 9)).add(4, 4).add(0, 0).add(4, 5)  # black on (4,4),(4,5)
    assert Evaluator("b")(board) > 0
    assert Evaluator("w")(board) < 0
