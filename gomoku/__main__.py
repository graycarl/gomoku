import argparse
from .app import App


parser = argparse.ArgumentParser(prog='Gomoku',
                                 description='Gomoku game application')
parser.add_argument('size', type=int, nargs='?', default=15)
parser.add_argument('-p', '--profile', action='store_true',
                    help='Enable profile')

args = parser.parse_args()

app = App(boardsize=args.size, profile=args.profile)
app.run()
