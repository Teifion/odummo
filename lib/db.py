"""
This module contains all the functions that interact with the database.

All should be considered impure.
"""

from random import random
import transaction
from ..config import config

from ..models import (
    OdummoProfile,
    OdummoMove,
    OdummoGame,
)

from sqlalchemy import or_, not_, and_
from sqlalchemy import func
from datetime import datetime, timedelta

from . import (
    rules,
)

ai_move_delay = timedelta(minutes=3)
# ai_move_delay = timedelta()

def get_profile(user_id):
    the_profile = config['DBSession'].query(OdummoProfile).filter(OdummoProfile.user == user_id).first()
    
    if the_profile is None:
        the_profile = add_empty_profile(user_id)
    
    return the_profile

def add_empty_profile(user_id):
    the_profile = OdummoProfile()
    the_profile.user = user_id
    
    config['DBSession'].add(the_profile)
    return the_profile

def get_game_list(user_id):
    "Games waiting for us to make our move"
    User = config['User']
    
    filters = (
        or_(
            # I want to do something like this but can't work out how
            # and_(OdummoGame.player1 == user_id, func.mod(OdummoGame.turn, 2) == 0, User.id == OdummoGame.player2),
            # and_(OdummoGame.player2 == user_id, func.mod(OdummoGame.turn, 2) == 1, User.id == OdummoGame.player1),
            
            and_(OdummoGame.player1 == user_id, "mod(odummo_games.turn, 2) = 0", User.id == OdummoGame.player2),
            and_(OdummoGame.player2 == user_id, "mod(odummo_games.turn, 2) = 1", User.id == OdummoGame.player1),
        ),
        OdummoGame.winner == None,
    )
    
    return config['DBSession'].query(OdummoGame.id, User.name, OdummoGame.turn).filter(*filters)

def get_waiting_game_list(user_id):
    "Games waiting for our opponent to make a move"
    User = config['User']
    
    filters = (
        or_(
            and_(OdummoGame.player1 == user_id, "mod(odummo_games.turn, 2) = 1", User.id == OdummoGame.player2),
            and_(OdummoGame.player2 == user_id, "mod(odummo_games.turn, 2) = 0", User.id == OdummoGame.player1),
        ),
        OdummoGame.winner == None,
    )
    
    return config['DBSession'].query(OdummoGame.id, User.name, OdummoGame.turn).filter(*filters)

def get_recent_game_list(user_id, limit=5):
    "The most recently completed games, we return the id of the winner as a 4th attribute"
    User = config['User']
    
    filters = (
        or_(
            and_(OdummoGame.player1 == user_id, User.id == OdummoGame.player2),
            and_(OdummoGame.player2 == user_id, User.id == OdummoGame.player1),
        ),
        OdummoGame.winner != None,
    )
    
    return config['DBSession'].query(
        OdummoGame.id, User.name, OdummoGame.turn, OdummoGame.winner
    ).filter(*filters).order_by(OdummoGame.id.desc()).limit(limit)

def find_user(identifier):
    User = config['User']
    
    if type(identifier) == str:
        found = config['DBSession'].query(User.id).filter(User.name == identifier).first()
        if found == None:
            return None
        return config['get_user']({'id':found[0], 'name':identifier})
    
    elif type(identifier) == int:
        found = config['DBSession'].query(User.name).filter(User.id == identifier).first()
        if found == None:
            return None
        return config['get_user']({'id':identifier, 'name':found[0]})
    
    else:
        raise KeyError("No handler for identifier type of '{}'".format(type(identifier)))

def new_game(p1, p2, rematch=None):
    # 50% chance for either player to be player 1
    if random() > 0.5:
        p1, p2 = p2, p1
    
    game               = OdummoGame()
    game.player1       = p1
    game.player2       = p2
    game.started       = datetime.now()
    game.turn          = 0
    game.source        = rematch
    
    game.current_state = str(rules.empty_board)
    game.active_board  = -1
    
    config['DBSession'].add(game)
    
    # Get game ID
    game_id = config['DBSession'].query(OdummoGame.id).filter(
        OdummoGame.player1 == p1,
        OdummoGame.player2 == p2,
    ).order_by(OdummoGame.id.desc()).first()[0]
    
    return game_id

def get_game(game_id):
    the_game = config['DBSession'].query(OdummoGame).filter(OdummoGame.id == game_id).first()
    
    if the_game == None:
        raise ValueError("We were unable to find the game")
    
    return the_game

def perform_move(the_game, square):
    new_state = rules.new_board(the_game.current_state, the_game.turn, square)
    the_game.current_state = new_state
    
    add_turn(the_game, square)
    the_game.turn += 1
    
    end_result = rules.check_for_win(the_game)
    
    if end_result == "1":
        the_game.winner = the_game.player1
        
    elif end_result == "2":
        the_game.winner = the_game.player2
        
    elif " " not in the_game.current_state or end_result == "Draw":
        the_game.winner = -1
    
    config['DBSession'].add(the_game)

def add_turn(the_game, square):
    new_turn           = OdummoMove()
    new_turn.game      = the_game.id
    new_turn.player    = rules.current_player(the_game)
    
    new_turn.move      = square
    new_turn.timestamp = datetime.now()
    
    config['DBSession'].add(new_turn)

def find_match(profile):
    """
    We want to find:
     - Someone we're not currently playing against
     - Someone with matchmaking turned on
     - Someone that's made a move in the last 2 days
     - Prioritiesd by the difference in their win/loss ratio
    """
    
    # First we find who we are currently playing against
    filters = (
        or_(
            OdummoGame.player1 == profile.user,
            OdummoGame.player2 == profile.user,
        ),
        OdummoGame.winner == None,
    )
    
    current_opponents = [profile.user]
    for p1, p2 in config['DBSession'].query(OdummoGame.player1, OdummoGame.player2).filter(*filters):
        current_opponents.extend([p1, p2])
    current_opponents = set(current_opponents)
    
    # Two days ago
    last_allowed_move = datetime.now() - timedelta(days=2)
    
    # Our winloss ratio
    winloss = profile.wins/max(profile.losses,1)
    
    # Order by
    ordering = "ABS((odummo_profiles.wins/GREATEST(odummo_profiles.losses,1)) - {}) ASC".format(winloss)
    
    # The query that tries to find our opponent
    opponent = config['DBSession'].query(OdummoProfile.user).filter(
        not_(OdummoProfile.user.in_(current_opponents)),
        OdummoProfile.matchmaking == True,
        OdummoProfile.last_move > last_allowed_move,
    ).order_by(ordering).first()
    
    if opponent is None:
        return "We couldn't find anybody to match you against. Remeber, we'll only match you against someone that's made a move in the last two days, isn't someone you're already playing against and has matchmaking enabled."
    
    return opponent[0]

def completed_games(user_id, opponent_id=None):
    if opponent_id != None:
        filters = (
            or_(
                and_(OdummoGame.player1 == user_id, OdummoGame.player2 == opponent_id),
                and_(OdummoGame.player2 == user_id, OdummoGame.player1 == opponent_id),
            ),
            OdummoGame.winner != None,
        )
    else:
        filters = (
            or_(OdummoGame.player1 == user_id, OdummoGame.player2 == user_id),
            OdummoGame.winner != None,
        )
    return config['DBSession'].query(func.count(OdummoGame.id)).filter(*filters).first()[0]

def games_in_progress(user_id, opponent_id=None):
    if opponent_id != None:
        filters = (
            or_(
                and_(OdummoGame.player1 == user_id, OdummoGame.player2 == opponent_id),
                and_(OdummoGame.player2 == user_id, OdummoGame.player1 == opponent_id),
            ),
            OdummoGame.winner == None,
        )
    else:
        filters = (
            or_(OdummoGame.player1 == user_id, OdummoGame.player2 == user_id),
            OdummoGame.winner == None,
        )
    return config['DBSession'].query(func.count(OdummoGame.id)).filter(*filters).first()[0]
    
def games_won(user_id, opponent_id=None):
    filters = [
        OdummoGame.winner == user_id,
    ]
    if opponent_id != None:
        filters.append(or_(
            OdummoGame.player1 == opponent_id,
            OdummoGame.player2 == opponent_id
        ))
    
    return config['DBSession'].query(func.count(OdummoGame.id)).filter(*filters).first()[0]

def games_lost(user_id, opponent_id=None):
    if opponent_id != None:
        filters = (
            OdummoGame.winner == opponent_id,
            or_(
                OdummoGame.player1 == user_id,
                OdummoGame.player2 == user_id
            ))
    else:
        filters = (
            or_(OdummoGame.player1 == user_id, OdummoGame.player2 == user_id),
            OdummoGame.winner != user_id,
            OdummoGame.winner != None,
        )
    return config['DBSession'].query(func.count(OdummoGame.id)).filter(*filters).first()[0]

def games_drawn(user_id, opponent_id=None):
    if opponent_id != None:
        filters = (
            or_(
                and_(OdummoGame.player1 == user_id, OdummoGame.player2 == opponent_id),
                and_(OdummoGame.player2 == user_id, OdummoGame.player1 == opponent_id),
            ),
            OdummoGame.winner == -1,
        )
    else:
        
        filters = (
            or_(OdummoGame.player1 == user_id, OdummoGame.player2 == user_id),
            OdummoGame.winner == -1,
        )
    return config['DBSession'].query(func.count(OdummoGame.id)).filter(*filters).first()[0]

def get_stats(user_id, opponent_id=None):
    stats = dict(
        completed_games   = completed_games(user_id, opponent_id),
        games_in_progress = games_in_progress(user_id, opponent_id),
        
        games_won   = games_won(user_id, opponent_id),
        games_lost  = games_lost(user_id, opponent_id),
        games_drawn = games_drawn(user_id, opponent_id),
    )
    
    stats['win_ratio'] = rules.win_ratio(stats['games_won'], stats['completed_games'])
    
    return stats

def find_ongoing_ai_game(user_id):
    return config['DBSession'].query(
        OdummoGame
    ).filter(
        or_(
            and_(OdummoGame.player1 == user_id, OdummoGame.player2 == -1),
            and_(OdummoGame.player2 == user_id, OdummoGame.player1 == -1)
        ),
        OdummoGame.winner == None
    ).first()

def new_ai_game(user_id):
    return new_game(user_id, -1)

def is_it_ai_move(the_game):
    if the_game.winner != None:
        return False
    
    if rules.current_player(the_game) == -1:
        last_move = get_last_move(the_game.id)
        
        # No last move but it's the AI's turn? Make a move!
        if last_move is None:
            return True
        
        # Make sure we're not making moves too fast
        if (last_move.timestamp + ai_move_delay) < datetime.now():
            return True
    
    return False

def get_last_move(game_id):
    return config['DBSession'].query(OdummoMove).filter(OdummoMove.game == game_id).order_by(OdummoMove.timestamp.desc()).first()

from ..ai.ai_position import step as ai_step
def make_ai_move(the_game):
    if the_game.player1 == -1: p = 2
    else: p = 1
    
    square = ai_step(the_game.current_state, p)
    
    perform_move(the_game, square)
