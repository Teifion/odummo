import datetime
import transaction
from ..lib import (
    db,
    rules,
    notifications,
)

import re
from pyramid import testing
from pyramid.httpexceptions import HTTPFound

from ..models import (
    OdummoProfile,
    OdummoMove,
    OdummoGame,
)

from ..config import config

"""
I've got a class defined in test_f which does the following.

class DBTestClass(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = routes(testing.setUp())
    
    def tearDown(self):
        DBSession.execute("ROLLBACK")
        self.session.remove()
    
    def get_app(self, auth):
        # Auth is a username of the user you're authing as
        # Code that returns a testapp and cookie data
    
    def make_request(self, app, path, data, msg="", expect_forward=False):
        # Makes a request and checks for errors
        # Provides a custome message on failure
        # Allows expected fowards

Sadly I couldn't work out how to detatch this part from my
main framework. The key part is it'll allow us to use the db connection.
"""

try:
    from ....core.lib.test_f import DBTestClass
except Exception:
    class DBTestClass(object):
        pass

"""
This assumes the path prefix is "odummo".
"""

class OdummoDBTester(DBTestClass):
    def ttest_notifications(self):
        r = testing.DummyRequest()
        
        # We don't test the validity, just that they'll work if we pass them data
        result = notifications.forward_to_game(r, "1")
        self.assertTrue(isinstance(result, HTTPFound))

# def make_view(self, app, view, matchdict={}, params={}, msg="", request=None):
#     if request is None:
#         request = DummyRequest()
    
#     request.matchdict = matchdict
#     request.params = params
#     return view(request)
    
    def test_views(self):
        with transaction.manager:
            config['DBSession'].execute('DELETE FROM odummo_moves')
            config['DBSession'].execute('DELETE FROM odummo_games')
            config['DBSession'].execute('COMMIT')
        
        User = config['User']
        u1, u2, u3 = config['DBSession'].query(User.id, User.name).filter(User.id > 1).limit(3)
        
        with transaction.manager:
            p1 = db.get_profile(user_id=u1.id)
            p2 = db.get_profile(user_id=u2.id)
            p3 = db.get_profile(user_id=u3.id)
            
            p1.matchmaking = True
            p1.last_move = datetime.datetime.now()
            p2.matchmaking = True
            p2.last_move = datetime.datetime.now()
            p3.matchmaking = True
            p3.last_move = datetime.datetime.now()
            config['DBSession'].add(p1)
            config['DBSession'].add(p2)
            config['DBSession'].add(p3)
        
        app, cookies = self.get_app()
        
        self.make_request(app, "/odummo/menu", cookies, msg="Error loading the menu screen for odummo")
        
        # Preferences
        page_result = self.make_request(app, "/odummo/preferences", cookies,
            msg="Error loading the preferences screen")
        
        form = page_result.form  
        form.set("matchmaking", "true")
        page_result = form.submit('form.submitted')
        
        self.check_request_result(
            page_result,
            "",
            {},
            msg = "Error updaing preferences"
        )
        
        # Matchmaking
        # self.make_request(app, "/odummo/matchmake", cookies,
        #     msg="Error attempting to matchmake",
        #     expect_forward = re.compile(r"odummo/game/[0-9]+")
        # )
        
        # Stats
        self.make_request(app, "/odummo/stats", cookies, msg="Error attempting to view stats")
        
        # Head to head stats
        self.make_request(app, "/odummo/head_to_head_stats?opponent_name={}".format(u2.name), cookies,
            msg="Error attempting to view head to head stats"
        )
        
        self.make_request(app, "/odummo/head_to_head_stats?opponent_id=%d" % u2.id, cookies,
            msg="Error attempting to view head to head stats"
        )
        
        # Now lets start a game
        page_result = self.make_request(app, "/odummo/new_game", cookies,
            msg="Error loading the new game screen")
        
        form = page_result.form
        form.set("opponent_name", u2.name)
        page_result = form.submit('form.submitted')
        
        page_result = self.check_request_result(
            page_result,
            "",
            {},
            expect_forward = re.compile(r"odummo/game/[0-9]+"),
            msg = "Error submitting the new game form",
        )
        
        # Get match ID
        the_game = config['DBSession'].query(OdummoGame).order_by(OdummoGame.id.desc()).first()
        
        # View game
        self.make_request(app, "/odummo/game/{}".format(the_game.id), cookies,
            msg="Error viewing the game"
        )
        
        # Make a move
        """
        page_result = self.make_request(app, "/odummo/game/{}".format(the_game.id), cookies,
            msg="Error viewing the game"
        )
        
        page_result = form.submit('form.submitted')
        
        # View it again to make sure it's still okay to view a game
        page_result = self.make_request(app, "/odummo/game/{}".format(the_game.id), cookies,
            msg="Error viewing the game"
        )
        
        # config.add_route('odummo.rematch', '/rematch/{game_id}')
        # config.add_route('odummo.view_game', '/game/{game_id}')
        # config.add_route('odummo.check_status', '/check_status/{game_id}')
        # config.add_route('odummo.check_turn', '/check_turn/{game_id}')
        # config.add_route('odummo.make_move', '/make_move/{game_id}')
        # config.add_route('odummo.test_move', '/test_move/{game_id}')
        
        # View once more now the game has ended
        
        self.make_request(app, "/odummo/menu", cookies, msg="Error loading the menu screen for odummo after ensuring games were added")
        """
