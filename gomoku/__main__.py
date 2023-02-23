import argparse
from .board import Board
from . import gui


parser = argparse.ArgumentParser(prog='Gomoku',
                                 description='Gomoku game application')
parser.add_argument('size', type=int, nargs='?', default=15)
parser.add_argument('-p', '--profile', action='store_true',
                    help='Enable profile')

args = parser.parse_args()

b = Board((15, 15))

app = gui.App(boardsize=args.size, profile=args.profile)
app.mainloop()
