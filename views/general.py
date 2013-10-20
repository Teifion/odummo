"""
Views related to the system that don't involve playing the game itself.
"""

from pyramid.renderers import get_renderer

from ..lib import (
    db,
)

from ..config import config

def menu(request):
    """
    The main menu with a list of links relevant to the player (e.g. ongoing games, preferences).
    """
    config['check_blocked'](request)
    the_user = config['get_user_func'](request)
    layout = get_renderer(config['layout']).implementation()
    
    # We call but don't query this so that we can assign a profile
    # if none exists
    db.get_profile(the_user.id)
    
    game_list    = db.get_game_list(the_user.id)
    waiting_list = db.get_waiting_game_list(the_user.id)
    recent_list  = db.get_recent_game_list(the_user.id)
    
    return dict(
        title        = "Odummo menu",
        layout       = layout,
        the_user     = the_user,
        
        game_list    = list(game_list),
        waiting_list = list(waiting_list),
        recent_list  = list(recent_list),
    )

def stats(request):
    config['check_blocked'](request)
    the_user = config['get_user_func'](request)
    db.get_profile(the_user.id)
    layout = get_renderer(config['layout']).implementation()
    
    stats = db.get_stats(the_user.id)
    
    return dict(
        title    = "Odummo stats",
        layout   = layout,
        the_user = the_user,
        
        stats    = stats,
    )

def preferences(request):
    config['check_blocked'](request)
    the_user = config['get_user_func'](request)
    profile = db.get_profile(the_user.id)
    layout = get_renderer(config['layout']).implementation()
    message = ""
    
    if "preferred_colour" in request.params:
        preferred_colour = request.params['preferred_colour']
        if preferred_colour == "true":
            profile.preferred_colour = True
        else:
            profile.preferred_colour = False
        
        matchmaking = request.params['matchmaking']
        if matchmaking == "true":
            profile.matchmaking = True
        else:
            profile.matchmaking = False
        
        message = "Changes saved"
    
    return dict(
        title    = "Ultimate O's and X's preferences",
        layout   = layout,
        the_user = the_user,
        profile  = profile,
        message  = message,
    )

def head_to_head_stats(request):
    config['check_blocked'](request)
    the_user = config['get_user_func'](request)
    message  = ""
    
    if "opponent_name" in request.params:
        opponent_name = request.params['opponent_name'].strip().upper()
        opponent = db.find_user(opponent_name)
        
    else:
        opponent_id = int(request.params['opponent_id'])
        opponent = db.find_user(opponent_id)
    
    stats = None
        
    if opponent is not None:
        stats = db.get_stats(the_user.id, opponent.id)
    else:
        message = "No opponent could be found"
    
    return dict(
        stats    = stats,
        message  = message,
        opponent = opponent,
    )

def matchmake(request):
    config['check_blocked'](request)
    layout = get_renderer(config['layout']).implementation()
    
    the_user = config['get_user_func'](request)
    profile = db.get_profile(the_user.id)
    
    result = db.find_match(profile)
    
    if isinstance(result, str):
        return dict(
            title    = "Wordy matchmaking",
            layout   = layout,
            message  = result,
        )
    
    game_id = db.new_game([the_user.id, result])
    return HTTPFound(location=request.route_url("odummo.view_game", game_id=game_id))
