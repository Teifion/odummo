"""
This module contains all functions relating to the rules of a game, but not
nessesarily the running of a game itself.
"""

from itertools import takewhile
from collections import defaultdict

empty_board = " "*24 + "   12   " + "   21   " + " "*24

def current_player(the_game):
    if the_game.turn % 2 == 0:
        return the_game.player1
    else:
        return the_game.player2

def expand_board(board):
    result = defaultdict(lambda: None)
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

def do_search(board, player, start, direction):
    """Board is an expanded board
    Player is 1 or 2
    Start is the X,Y pair of the first tile
    Direction is a pair such as (-1, -1) showing direction.
    
    The result is a list of all the tiles flipped in that direction."""
    
    # Opponent is the opposite of us
    if str(player) == '1': opponent = '2'
    else: opponent = '1'
    
    x, y = start
    dx, dy = direction
    
    # Returns true on opponents tiles
    prelude = lambda xy: board[xy] == opponent
    
    # Generate a series of values in a given direction
    # Example: (1,1), (2,2), (3,3), (4,4)
    def gen(gx, gy):
        for i in range(9):
            gx += dx
            gy += dy
            yield gx, gy
    
    samples = list(gen(x,y))
    result = list(takewhile(prelude, samples))
    
    last_tile = samples[len(result)]
    
    # If the last tile we landed on was one of our own then return the
    # list of matched tiles
    if board[last_tile] == str(player):
        return result
    else:
        return []

def get_flips(current_state, turn, square_id):
    """
    Returns the number of flips a given move will cause
    """
    player = (turn % 2) + 1
    
    sx = square_id % 8
    sy = int((square_id - sx) / 8)
    square = (sx, sy)
    
    board = expand_board(current_state)
    
    count = 0
    
    searches = (
        do_search(board, player, square, (-1, -1)),
        do_search(board, player, square, (-1, 0)),
        do_search(board, player, square, (-1, 1)),
        
        do_search(board, player, square, (0, -1)),
        do_search(board, player, square, (0, 1)),
        
        do_search(board, player, square, (1, -1)),
        do_search(board, player, square, (1, 0)),
        do_search(board, player, square, (1, 1)),
    )
    
    flips = []
    for s in searches:
        flips.extend(s)
    
    return flips

def is_move_valid(current_state, turn, square_id):
    player = (turn % 2) + 1
    
    sx = square_id % 8
    sy = int((square_id - sx) / 8)
    square = (sx, sy)
    
    board = expand_board(current_state)
    
    # First, is the square empty?
    if board[square] != ' ':
        return "The square is already taken up by another piece"
    
    # Ensure we are placing our tile next to at least one other tiles
    surrounding_squares = (
        board[(sy-1, sx-1)], board[(sy-1, sx)], board[(sy-1, sx+1)],
        board[(sy-0, sx-1)],                    board[(sy-0, sx+1)],
        board[(sy+1, sx-1)], board[(sy+1, sx)], board[(sy+1, sx+1)],
    )
    
    if '1' not in surrounding_squares and '2' not in surrounding_squares:
        return "You must place your tile next to at least one other tile"
    
    # Which tiles (if any) are flipped?
    flips = get_flips(current_state, turn, square_id)
    if len(flips) < 1:
        return "You must flip at least one piece to be able to claim a square"
    
    # return "Should be valid"
    return "Valid"

def set_state_by_colour(current_state, preferred_colour, player_is_player1):
    # Swap them to A and B now so we can swap them back to 1 and 2 later
    # without repeating this step
    current_state = current_state.replace("1", "A").replace("2", "B")
    
    if player_is_player1:
        if preferred_colour:
            current_state = current_state.replace("A", "1").replace("B", "2")
        else:
            current_state = current_state.replace("B", "1").replace("A", "2")
    else:
        if preferred_colour:
            current_state = current_state.replace("B", "1").replace("A", "2")
        else:
            current_state = current_state.replace("A", "1").replace("B", "2")
    
    return current_state


def new_board(current_state, turn, square_id):
    """Takes a board, current turn and a move
    Returns a flattened board of the new state"""
    
    player = (turn % 2) + 1
    
    sx = square_id % 8
    sy = int((square_id - sx) / 8)
    square = (sx, sy)
    
    board = expand_board(current_state)
    
    flips = get_flips(current_state, turn, square_id)
    
    for f in flips:
        board[f] = str(player)
    board[square] = str(player)
    
    return flatten_board(board)

def check_for_win(the_game):
    return False

def win_ratio(wins, total_games, decimal_points=2):
    if total_games == 0: return 0
    if wins == 0: return 0
    return round(100 * (wins / total_games), decimal_points)
