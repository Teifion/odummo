"""
Views relating to games of Odummo.
"""

import transaction
import datetime
from datetime import timedelta

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from pyramid.renderers import get_renderer

from ..lib import (
    db,
    rules,
)

from ..config import config

try:
    try:
        from ...communique import send as com_send
    except ImportError:
        try:
            from ....communique import send as com_send
        except ImportError:
            raise
except Exception as e:
    def com_send(*args, **kwargs):
        pass

def new_game(request):
    config['check_blocked'](request)
    the_user = config['get_user_func'](request)
    layout = get_renderer(config['layout']).implementation()
    
    message = ""
    flash_colour = "A00"
    
    if "opponent_name" in request.params:
        opponent_name = request.params['opponent_name'].strip().upper()
        opponent = db.find_user(opponent_name)
        
        # Failure :(
        if opponent == None:
            message = """I'm sorry, we cannot find any opponent by the name of '{}'""".format(opponent_name)
            
        else:
            game_id = db.new_game(the_user, opponent)
            return HTTPFound(location=request.route_url("odummo.view_game", game_id=game_id))
    
    return dict(
        title        = "Odummo",
        layout       = layout,
        the_user     = the_user,
        message      = message,
        flash_colour = flash_colour,
    )

def view_game(request):
    config['check_blocked'](request)
    the_user = config['get_user_func'](request)
    profile = db.get_profile(the_user.id)
    layout = get_renderer(config['layout']).implementation()
    
    game_id  = int(request.matchdict['game_id'])
    the_game = db.get_game(game_id)
    message  = ""
    
    if the_game.player1 == the_user.id:
        opponent = db.find_user(the_game.player2)
        
    else:
        opponent = db.find_user(the_game.player2)
    
    winner = None
    if the_game.winner != None:
        winner = db.find_user(the_game.winner)
    
    return dict(
        title     = "Odummo: {}".format(opponent.name),
        layout    = layout,
        the_user  = the_user,
        the_game  = the_game,
        your_turn = rules.current_player(the_game) == the_user.id,
        profile   = profile,
        winner    = winner,
        message   = message,
        opponent  = opponent,
    )

def make_move(request):
    config['check_blocked'](request)
    the_user = config['get_user_func'](request)
    layout = get_renderer(config['layout']).implementation()
    
    message = ""
    flash_colour = "A00"
    
    game_id  = int(request.matchdict['game_id'])
    square   = int(request.params['square'])
    
    the_game = db.get_game(game_id)
    current_player = rules.current_player(the_game)
    
    if current_player == the_user.id:
        try:
            if not rules.is_move_valid(the_game.current_state, the_game.turn, square):
                raise Exception("Invalid move")
            db.perform_move(the_game, square)
            com_send(rules.current_player(the_game), "odummo.new_move", "{} has made a move".format(the_user.name), str(game_id), timedelta(hours=24))
            return HTTPFound(location=request.route_url("odummo.view_game", game_id=game_id))
        except Exception as e:
            raise
            message = e.args[0]
    else:
        message = "It is not your turn"
    
    return dict(
        title        = "Odummo",
        layout       = layout,
        the_user     = the_user,
        the_game     = the_game,
        message      = message,
        flash_colour = flash_colour,
    )

def rematch(request):
    config['check_blocked'](request)
    the_user = config['get_user_func'](request)
    game_id  = int(request.matchdict['game_id'])
    the_game = db.get_game(game_id)
    
    # Not a player? Send them back to the menu
    if the_user.id != the_game.player1 and the_user.id != the_game.player2:
        return HTTPFound(location=request.route_url("odummo.menu"))
    
    # Not over yet? Send them back to the game in question.
    if the_game.winner == None:
        return HTTPFound(location=request.route_url("odummo.view_game", game_id=game_id))
    
    if the_user.id == the_game.player1:
        opponent = db.find_user(the_game.player2)
    else:
        opponent = db.find_user(the_game.player1)
    
    newgame_id = db.new_game(the_user, opponent, rematch=game_id)
    the_game.rematch = newgame_id
    
    # com_send(opponent.id, "odummo.new_game", "{} has started a game against you".format(the_user.name), str(newgame_id), timedelta(hours=24))
    return HTTPFound(location=request.route_url("odummo.view_game", game_id=newgame_id))

def check_turn(request):
    config['check_blocked'](request)
    request.do_not_log = True
    
    the_user = config['get_user_func'](request)
    game_id  = int(request.matchdict['game_id'])
    
    the_game = db.get_game(game_id)
    if rules.current_player(the_game) == the_user.id:
        return "True"
    return "False"

def check_turn(request):
    config['check_blocked'](request)
    request.do_not_log = True
    
    the_user = config['get_user_func'](request)
    game_id  = int(request.matchdict['game_id'])
    
    the_game = db.get_game(game_id)
    if rules.current_player(the_game) == the_user.id:
        return "True"
    return "False"
