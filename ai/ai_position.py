from random import choice
from functools import reduce
from . import api

"""
A simple AI that attempts to value corners and sides higher but otherwise
move based on the number of flips it will perform.
"""

name = "Position"

_corners = 20
_sides = 10
_normal = 0
_bad = -10

def _value(possible_move):
    sx = possible_move.square % 8
    sy = int((possible_move.square - sx) / 8)
    
    if (sx, sy) in ((0,0), (7,0), (0,7), (7,7)):
        return _corners + len(possible_move.flips)
    
    if sx in (0,7) or sy in (0,7):
        return _sides + len(possible_move.flips)
    
    if sx in (1,6) or sy in (1,6):
        return _bad + len(possible_move.flips)
    
    return _normal + len(possible_move.flips)

def initialise():
    pass

def step(b, player):
    moves = api.all_potential_moves(b, player)
    prelude = lambda a, b: a if _value(a) > _value(b) else b
    return reduce(prelude, moves).square

def game_over(moves, board, player):
    pass

def shutdown():
    pass
