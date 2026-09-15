"""Command line entry point: ``python -m gomoku`` or ``gomoku``."""

from __future__ import annotations

import argparse

from .app import App


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gomoku", description="Gomoku game application"
    )
    parser.add_argument(
        "size",
        type=int,
        nargs="?",
        default=15,
        help="board size, e.g. 15 for a 15x15 board (default: %(default)s)",
    )
    parser.add_argument(
        "-p",
        "--profile",
        action="store_true",
        help="write cProfile stats to /tmp/gomoku/",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    App(boardsize=args.size, profile=args.profile).run()


if __name__ == "__main__":
    main()
