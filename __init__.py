def odummo_nimblescan():
    try:
        from ...nimblescan import api
    except ImportError:
        try:
            from ..nimblescan import api
        except ImportError:
            return
    
    api.register('odummo.menu', "Odummo - Menu", ['games'], (lambda r: True), api.make_forwarder("odummo.menu"))
    api.register('odummo.new_game', "Odummo - New game", ['games'], (lambda r: True), api.make_form_forwarder("odummo.new_game", []), '<label for="ns_opponent">Opponent:</label> <input type="text" name="opponent_name" id="ns_opponent" value="" style="display:inline-block;"/>')
    api.register('odummo.stats', "Odummo - Stats", ['games'], (lambda r: True), api.make_forwarder("odummo.stats"))
    api.register('odummo.preferences', "Odummo - Preferences", ['games'], (lambda r: True), api.make_forwarder("odummo.preferences"))

def odummo_notifications():
    try:
        from ...communique import register, send
    except ImportError:
        try:
            from ..communique import register, send
        except ImportError:
            return
    
    from .lib.notifications import forward_to_game, forward_to_profile
    
    register('odummo.new_move', 'New move', 'http://localhost:6543/static/images/communique/odummo.png', forward_to_game)
    register('odummo.end_game', 'Game over', 'http://localhost:6543/static/images/communique/odummo.png', forward_to_game)
    register('odummo.win_game', 'Victory!', 'http://localhost:6543/static/images/communique/odummo.png', forward_to_game)

def includeme(config):
    from .views import (
        general,
        game,
    )
    
    odummo_notifications()
    odummo_nimblescan()
    
    # General views
    config.add_route('odummo.menu', '/menu')
    config.add_route('odummo.stats', '/stats')
    config.add_route('odummo.head_to_head_stats', '/head_to_head_stats')
    config.add_route('odummo.preferences', '/preferences')
    
    config.add_view(general.menu, route_name='odummo.menu', renderer='templates/general/menu.pt', permission='loggedin')
    config.add_view(general.stats, route_name='odummo.stats', renderer='templates/general/stats.pt', permission='loggedin')
    config.add_view(general.preferences, route_name='odummo.preferences', renderer='templates/general/preferences.pt', permission='loggedin')
    config.add_view(general.head_to_head_stats, route_name='odummo.head_to_head_stats', renderer='templates/general/head_to_head_stats.pt', permission='loggedin')
    
    # Game views
    config.add_route('odummo.new_game', '/new_game')
    config.add_route('odummo.new_ai_game', '/new_ai_game')
    config.add_route('odummo.ai_move', '/ai_move/{game_id}')
    config.add_route('odummo.rematch', '/rematch/{game_id}')
    
    config.add_route('odummo.view_game', '/game/{game_id}')
    config.add_route('odummo.make_move', '/make_move/{game_id}')
    config.add_route('odummo.matchmake', '/matchmake')
    config.add_route('odummo.check_turn', '/check_turn/{game_id}')
    
    config.add_view(game.new_game, route_name='odummo.new_game', renderer='templates/game/new_game.pt', permission='loggedin')
    config.add_view(game.new_ai_game, route_name='odummo.new_ai_game', renderer='templates/game/new_ai_game.pt', permission='loggedin')
    config.add_view(game.rematch, route_name='odummo.rematch', renderer='string', permission='loggedin')
    config.add_view(game.ai_move, route_name='odummo.ai_move', permission='loggedin')
    
    config.add_view(game.view_game, route_name='odummo.view_game', renderer='templates/game/view_game.pt', permission='loggedin')
    config.add_view(game.make_move, route_name='odummo.make_move', renderer='templates/game/make_move.pt', permission='loggedin')
    config.add_view(general.matchmake, route_name='odummo.matchmake', renderer='templates/general/matchmake.pt', permission='loggedin')
    config.add_view(game.check_turn, route_name='odummo.check_turn', renderer='string', permission='loggedin')
    
    return config
