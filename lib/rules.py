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

def expand_board(board):
    result = {}
    for y in range(8):
        for x in range(8):
            result[(x,y)] = board[(y*8)+x]
    return result

def flatten_board(board):
    def _g():
        for y in range(8):
            for x in range(8):
                yield board[(x,y)]
    return "".join(_g())
    

def is_move_valid(current_state, turn, square):
    player = (turn % 2) + 1
    
    sx = square % 8
    sy = (square - sx) / 8
    square = (sx, sy)
    
    board = expand_board(current_state)
    
    # First, is the square empty?
    if board[square] != ' ':
        return "The square is already taken up by another piece"
    
    return "Valid"

def check_for_win(the_game):
    return False
