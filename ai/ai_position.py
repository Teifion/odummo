from random import choice
from functools import reduce
from . import api
from collections import defaultdict

"""
This is an AI designed to lose every time or close to it.
"""

name = "Position 2"

str_values = """
9 0 6 6 6 6 0 9
0 0 1 1 1 1 0 0
6 1 8 4 4 8 1 6
6 1 4 3 3 4 1 6
6 1 4 3 3 4 1 6
6 1 8 4 4 8 1 6
0 0 1 1 1 1 0 0
9 0 6 6 6 6 0 9
""".replace(" ", "").replace("\n", "", 1)

values = {}
for y, line in enumerate(str_values.split("\n")):
    for x, v in enumerate(line):
        values[(x,y)] = int(v)

def _location_value(possible_move):
    sx = possible_move.square % 8
    sy = int((possible_move.square - sx) / 8)
    
    return values[(sx, sy)]

def _take_value(square):
    sx, sy = square
    return values[(sx, sy)] * 3

def _value(possible_move):
    sx = possible_move.square % 8
    sy = int((possible_move.square - sx) / 8)
    
    result = _location_value(possible_move) * 100
    result += sum(map(_take_value, possible_move.flips))
    return result

def initialise():
    pass

def step(b, player):
    moves = api.all_potential_moves(b, player)
    
    possibles = defaultdict(list)
    for m in moves:
        v = _value(m)
        possibles[v].append(m)
    
    keys = list(possibles.keys())
    keys.sort()
    keys.reverse()
    
    return choice(possibles[keys[0]]).square

def game_over(moves, board, player):
    pass

def shutdown():
    pass
