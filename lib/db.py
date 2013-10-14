"""
This module contains all the functions that interact with the database.

All should be considered impure.
"""

import transaction
from ..config import config

from ..models import (
    OdummoProfile,
    OdummoMove,
    OdummoGame,
)

from sqlalchemy import or_, not_, and_
from sqlalchemy import func
from datetime import datetime

from . import (
    rules,
)

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
    game               = OdummoGame()
    game.player1       = p1.id
    game.player2       = p2.id
    game.started       = datetime.now()
    game.turn          = 0
    game.source        = rematch
    
    game.current_state = str(rules.empty_board)
    game.active_board  = -1
    
    config['DBSession'].add(game)
    
    # Get game ID
    game_id = config['DBSession'].query(OdummoGame.id).filter(
        OdummoGame.player1 == p1.id,
        OdummoGame.player2 == p2.id,
    ).order_by(OdummoGame.id.desc()).first()[0]
    
    return game_id

def get_game(game_id):
    the_game = config['DBSession'].query(OdummoGame).filter(OdummoGame.id == game_id).first()
    
    if the_game == None:
        raise ValueError("We were unable to find the game")
    
    return the_game

def perform_move(the_game, square):
    board = list(the_game.current_state)
    board[square] = str((the_game.turn % 2) + 1)
    the_game.current_state = "".join(board)
    
    add_turn(the_game, square)
    the_game.turn += 1
    
    end_result = rules.check_for_win(the_game)
    
    if end_result in ("1", "2"):
        end_game(the_game)
    elif " " not in the_game.current_state:
        draw_game(the_game)
    
    config['DBSession'].add(the_game)

def add_turn(the_game, square):
    new_turn           = OdummoMove()
    new_turn.game      = the_game.id
    new_turn.player    = rules.current_player(the_game)
    
    new_turn.move      = square
    new_turn.timestamp = datetime.now()
    
    config['DBSession'].add(new_turn)
