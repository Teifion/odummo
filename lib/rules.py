"""
This module contains all functions relating to the rules of a game, but not
nessesarily the running of a game itself.
"""

empty_board = " "*24 + "   12   " + "   21   " + " "*24

def current_player(the_game):
    if the_game.turn % 2 == 0:
        return the_game.player1
    else:
        return the_game.player2

def is_move_valid(current_state, turn, square):
    player = (turn % 2) + 1
    
    return True
