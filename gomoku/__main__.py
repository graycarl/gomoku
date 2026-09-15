"""Command line entry point: ``python -m gomoku`` or ``gomoku``."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import cast

from .app import App

DEFAULT_SIZE = 15


@dataclass(frozen=True)
class Options:
    """Typed result of command line parsing."""

    size: int = DEFAULT_SIZE
    profile: bool = False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gomoku", description="Gomoku game application"
    )
    parser.add_argument(
        "size",
        type=int,
        nargs="?",
        default=DEFAULT_SIZE,
        help="board size, e.g. 15 for a 15x15 board (default: %(default)s)",
    )
    parser.add_argument(
        "-p",
        "--profile",
        action="store_true",
        help="write cProfile stats to /tmp/gomoku/",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> Options:
    """Parse ``argv`` into a fully typed :class:`Options`."""
    args = build_parser().parse_args(argv)
    # argparse stores options as ``Any``; the parser above fixes their types.
    return Options(size=cast("int", args.size), profile=cast("bool", args.profile))


def main(argv: list[str] | None = None) -> None:
    options = parse_args(argv)
    App(boardsize=options.size, profile=options.profile).run()


if __name__ == "__main__":
    main()
