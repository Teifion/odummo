from random import choice
from . import api

name = "Choice"

def initialise():
    pass

def step(b, player):
    all_pm = list(api.all_potential_moves(b, player))
    return choice(all_pm).square

def game_over(moves, board, player):
    pass

def shutdown():
    pass
