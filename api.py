"""
A set of functions allowing you to run games from a CLI script.
"""

from ai import cli_f
from collections import namedtuple
from lib import rules

BoardObject = namedtuple('BoardObject', ['current_state', 'turn'])
PotentialMove = namedtuple('PotentialMove', ['square', 'flips'])

def _tuple_to_square_id(t):
    return t[0] + (t[1]*8)

def new_game():
    return str(rules.empty_board)

def is_move_valid(current_state, player, square):
    if isinstance(square, tuple):
        square = _tuple_to_square_id(square)
    
    return rules.is_move_valid(current_state, turn=player+1, square_id=square)

def make_move(current_state, player, square):
    if isinstance(square, tuple):
        square = _tuple_to_square_id(square)
    
    new_state = rules.new_board(current_state, turn=player+1, square_id=square)
    end_result = rules.check_for_win(BoardObject(new_state, player+1))
    
    return new_state, end_result

def all_moves(current_state, player):
    squares = range(64)
    prelude = lambda square: PotentialMove(square, rules.get_flips(current_state, turn=player+1, square_id=square))
    
    return map(prelude, squares)

def all_valid_moves(current_state, player):
    return filter(
        lambda pm: len(pm.flips) > 0,
        all_moves(current_state, player),
    )

def visual_board(b):
    r = []
    for i in range(8):
        r.append(b[i*8:(i+1)*8])
    return "\n".join(r)

def run_game(step1, step2):
    """step1 and step2 take the current board and the current player
    they return the move they want to make.
    
    This function will return a list of the moves made
    and the final result of the game."""
    
    # We use this to avoid an if statement later
    steps = [None, step1, step2]
    
    b = new_game()
    moves = []
    
    game_over = False
    player = 1
    while not game_over:
        square = steps[player](b, player)
        moves.append((player, square))
        b, end = make_move(b, player, square)
        
        if end:
            game_over = True
        
        # Oscillate between 1 and 2
        player = (3 - player)
    
    return moves, b

from random import choice
def random_step(b, player):
    valid = list(all_valid_moves(b, player))
    return choice(valid).square

def most_flips(b, player):
    valid = all_valid_moves(b, player)
    most = PotentialMove(-1, [])
    
    for v in valid:
        if most is None or len(v.flips) > len(most.flips):
            most = v
    
    return most.square

def main():
    scores = [0,0]
    
    for i in cli_f.progressbar(range(100), "Running matches: ", 40, with_eta=True):
        moves, board = run_game(random_step, most_flips)
        
        p1 = len(list(filter((lambda s: s == '1'), board)))
        p2 = len(list(filter((lambda s: s == '2'), board)))
        
        if p1 > p2:
            scores[0] += 1
        else:
            scores[1] += 1
        
    print("Player 1 (random_step): %s/100" % scores[0])
    print("Player 2 (most_flips): %s/100" % scores[1])

if __name__ == '__main__':
    main()
