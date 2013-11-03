"""
A set of functions allowing you to run games from a CLI script.
"""

import importlib
import sys
from collections import namedtuple
import argparse

try:
    from ai import cli_f, api
    from lib import rules
except ValueError:
    from .ai import cli_f
    from .lib import rules
except ImportError:
    from .ai import cli_f
    from .lib import rules

def main():
    """
    example call: python3 cli.py most choice
    
    This will pit most against choice
    """
    parser = argparse.ArgumentParser(description='Odummo command line.', prog="Odummo")
    parser.add_argument('ai1', help='The first AI being used')
    parser.add_argument('ai2', help='The second AI being used')
    parser.add_argument('game_count', help='The number of games played')
    parser.add_argument('-p', dest="profile", action="store_true", help='Enable profiling')
    parser.add_argument('-v', dest="verbose", action="store_true", help='Show progress')
    args = parser.parse_args()
    
    ai1 = importlib.import_module("ai.ai_%s" % args.ai1)
    ai2 = importlib.import_module("ai.ai_%s" % args.ai2)
    
    print("Player 1: %s" % (ai1.name))
    print("Player 2: %s" % (ai2.name))
    
    game_count = int(args.game_count)
    game_iter = api.run_many_games(game_count, ai1, ai2)
    
    if args.verbose:
        game_iter = cli_f.progressbar(game_iter, "Running matches: ", 40, with_eta=True, count=game_count)
    
    scores = [0,0]
    for moves, board in game_iter:
        p1 = len(list(filter((lambda s: s == '1'), board)))
        p2 = len(list(filter((lambda s: s == '2'), board)))
        
        if p1 > p2:
            scores[0] += 1
        else:
            scores[1] += 1
    
    ai1.shutdown()
    ai2.shutdown()
    
    print("Player 1 (%s): %s/%s" % (ai1.name, scores[0], game_count))
    print("Player 2 (%s): %s/%s" % (ai2.name, scores[1], game_count))

if __name__ == '__main__':
    main()
