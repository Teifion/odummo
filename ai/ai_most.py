from . import api
from .api import PotentialMove

name = "Most"

def initialise():
    pass

def step(b, player):
    moves = api.all_potential_moves(b, player)
    most = PotentialMove(-1, [])
    
    for pm in moves:
        if most is None or len(pm.flips) > len(most.flips):
            most = pm
    
    return most.square

def game_over(moves, board, player):
    pass

def shutdown():
    pass
