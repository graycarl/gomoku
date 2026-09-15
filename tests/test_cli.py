from gomoku.__main__ import Options, parse_args


def test_defaults() -> None:
    options = parse_args([])
    assert options == Options(size=15, profile=False)


def test_overrides() -> None:
    options = parse_args(["7", "--profile"])
    assert options == Options(size=7, profile=True)
