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
    pass

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
    pass

def matchmake(request):
    pass
