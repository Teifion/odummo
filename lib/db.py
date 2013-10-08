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
import datetime

# from . import (
#     rules,
# )

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