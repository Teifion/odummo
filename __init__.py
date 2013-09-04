def includeme(config):
    from .views import (
        general,
        game,
    )
    
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
    config.add_route('odummo.rematch', '/rematch/{game_id}')
    
    config.add_route('odummo.view_game', '/game/{game_id}')
    config.add_route('odummo.make_move', '/make_move/{game_id}')
    config.add_route('odummo.matchmake', '/matchmake')
    
    config.add_view(game.new_game, route_name='odummo.new_game', renderer='templates/game/new_game.pt', permission='loggedin')
    config.add_view(game.rematch, route_name='odummo.rematch', renderer='string', permission='loggedin')
    
    config.add_view(game.view_game, route_name='odummo.view_game', renderer='templates/game/view_game.pt', permission='loggedin')
    config.add_view(game.make_move, route_name='odummo.make_move', renderer='string', permission='loggedin')
    config.add_view(general.matchmake, route_name='odummo.matchmake', renderer='templates/general/matchmake.pt', permission='loggedin')
    
    return config
