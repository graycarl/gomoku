import pytest

from gomoku.board import Board, other


def test_empty_board_defaults_to_black() -> None:
    board = Board(size=(5, 5))
    assert board.next_color == "b"
    assert board.step == 0
    assert board.pieces == ()


def test_add_places_pieces_and_alternates_colors() -> None:
    board = Board(size=(5, 5)).add(2, 2)
    assert board.last_piece.color == "b"
    assert board.next_color == "w"

    board = board.add(1, 1)
    assert board.last_piece.color == "w"
    assert board.step == 2


def test_add_rejects_occupied_position() -> None:
    board = Board(size=(5, 5)).add(2, 2)
    with pytest.raises(RuntimeError):
        board.add(2, 2)


def test_boards_are_immutable() -> None:
    board = Board(size=(5, 5))
    board.add(2, 2)
    assert board.pieces == ()


def test_candidate_positions_on_empty_board_is_center() -> None:
    assert Board(size=(7, 9)).get_candidate_positions() == [(3, 4)]


def test_candidate_positions_stay_on_board_and_exclude_stones() -> None:
    board = Board(size=(5, 5)).add(0, 0)
    candidates = board.get_candidate_positions(radius=1)
    assert candidates
    assert all(board.contains(x, y) for x, y in candidates)
    assert (0, 0) not in candidates


def test_next_boards_yields_one_board_per_candidate() -> None:
    board = Board(size=(5, 5)).add(2, 2)
    boards = list(board.next_boards())
    assert len(boards) == len(board.get_candidate_positions())
    assert all(b.step == board.step + 1 for b in boards)


def test_iter_position_covers_whole_board() -> None:
    board = Board(size=(4, 3)).add(1, 1)
    positions = list(board.iter_position())
    assert len(positions) == 12
    assert sum(piece is not None for _, _, piece in positions) == 1


def test_other_flips_color() -> None:
    assert other("b") == "w"
    assert other("w") == "b"
