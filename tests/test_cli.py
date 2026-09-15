from gomoku.__main__ import build_parser


def test_defaults() -> None:
    args = build_parser().parse_args([])
    assert args.size == 15
    assert args.profile is False


def test_overrides() -> None:
    args = build_parser().parse_args(["7", "--profile"])
    assert args.size == 7
    assert args.profile is True
