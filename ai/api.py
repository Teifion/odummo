"""
A set of functions allowing you to run games from a CLI script.
"""

from collections import namedtuple
import argparse

try:
    from ai import cli_f
    from lib import rules
except ValueError:
    from . import cli_f
    from ..lib import rules
except ImportError:
    from . import cli_f
    from ..lib import rules

BoardObject = namedtuple('BoardObject', ['current_state', 'turn'])
PotentialMove = namedtuple('PotentialMove', ['square', 'flips'])

def _tuple_to_square_id(t):
    return t[0] + (t[1]*8)

def new_game():
    return str(rules.empty_board)

def is_move_valid(current_state, player, square):
    if isinstance(square, tuple):
        square = _tuple_to_square_id(square)
    
    return rules.is_move_valid(current_state, turn=player, square_id=square)

def make_move(current_state, player, square):
    if isinstance(square, tuple):
        square = _tuple_to_square_id(square)
    
    if is_move_valid(current_state, player, square) != "Valid":
        raise Exception("Invalid move by %s" % player)
    
    new_state = rules.new_board(current_state, turn=player, square_id=square)
    end_result = rules.check_for_win(BoardObject(new_state, player+1))
    
    return new_state, end_result

def all_potential_moves(current_state, player):
    squares = range(64)
    prelude = lambda square: PotentialMove(square, rules.get_flips(current_state, turn=player, square_id=square))
    
    return map(
        prelude,
        filter(
            lambda square: rules.is_move_valid(current_state, player, square) == "Valid",
            squares,
        )
    )

def visual_board(b):
    r = [" " + "-"*8]
    for i in range(8):
        r.append('|' + b[i*8:(i+1)*8] + '|')
    r.append(" " + "-"*8)
    return "\n".join(r)

def run_game(step1, step2):
    """step1 and step2 take the current board and the current player
    they return the move they want to make.
    
    This function will return a list of the moves made
    and the final result of the game."""
    
    # We use this to avoid an if statement later
    steps = [None, step2, step1]
    
    b = new_game()
    moves = []
    
    game_over = False
    player = 2
    while not game_over:
        try:
            square = steps[player](b, player)
        except Exception:
            print("Board: '%s'" % b)
            print("Player: %s" % player)
            print("\n\n")
            raise
        
        moves.append((player, square))
        new_board, end = make_move(b, player, square)
        
        # print("")
        # print("Player %s moved to %s" % (3-player, square))
        # print(visual_board(new_board))
        # print("")
        
        if end:
            game_over = True
        
        b = str(new_board)
        
        # Oscillate between 1 and 2
        player = (3 - player)
    
    return moves, b

def run_many_games(game_count, ai1, ai2):
    """
    Each ai is expected to implement 3 functions:
    
    initialise() - No arguments, called before a series of games takes place
    
    step(board, player) - Given a copy of the board and their player number
        expected to return the square to play
    
    game_over(moves, board, player) - Given a copy of the moves made, the final board result and their player number
    
    shutdown() - No arguments, called at the end of a series (to allow things like comits etc)
    """
    
    ai1.initialise()
    ai2.initialise()
    
    for i in range(game_count):
        moves, board = run_game(ai1.step, ai2.step)
        
        ai1.game_over(moves, board, '1')
        ai2.game_over(moves, board, '2')
        
        yield moves, board
    
    ai1.shutdown()
    ai2.shutdown()
