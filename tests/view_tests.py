import datetime
import transaction
from ..lib import (
    db,
    rules,
    notifications,
)

import re
import random
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
    def test_notifications(self):
        r = testing.DummyRequest()
        
        # We don't test the validity, just that they'll work if we pass them data
        result = notifications.forward_to_game(r, "1")
        self.assertTrue(isinstance(result, HTTPFound))
    
    def test_views(self):
        # We use this to ensure it's never our turn first
        random.seed(500)
        
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
        self.make_request(app, "/odummo/matchmake", cookies,
            msg="Error attempting to matchmake",
            expect_forward = re.compile(r"odummo/game/[0-9]+")
        )
        
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
        game_id = the_game.id
        
        # View game
        self.make_request(app, "/odummo/game/{}".format(game_id), cookies,
            msg="Error viewing the game"
        )
        
        # Make a move, this one should fail as it's not our turn
        page_result = self.make_request(app, "/odummo/make_move/{}?square=0".format(game_id), cookies,
            msg="Error making a bad move (Not our turn)"
        )
        self.assertIn("It is not your turn", str(page_result))
        
        # We now make it our turn
        with transaction.manager:
            the_game.turn += 1
            config['DBSession'].add(the_game)
        del(the_game)
        
        # Make a move, this one should fail as it's not next to a tile
        page_result = self.make_request(app, "/odummo/make_move/{}?square=0".format(game_id), cookies,
            msg="Error making a bad move (Not next to any other tiles)"
        )
        self.assertIn("You must place your tile next to at least one other tile", str(page_result))
        
        # Make a move, this one should fail as it's not next to a tile
        page_result = self.make_request(app, "/odummo/make_move/{}?square=18".format(game_id), cookies,
            msg="Error making a bad move (No tiles will get flipped)"
        )
        self.assertIn("You must flip at least one piece to be able to claim a square", str(page_result))
        
        # Make a move, this one should work
        self.make_request(app, "/odummo/make_move/{}?square=19".format(game_id), cookies,
            msg="Error making a bad move (No tiles will get flipped)",
            expect_forward = "/odummo/game/{}".format(game_id)
        )
        
        # Now lets check for win conditions
        the_game = config['DBSession'].query(OdummoGame).filter(OdummoGame.id == game_id).first()
        with transaction.manager:
            the_game.turn += 1
            # Top left square is empty, bottom right is the same as us
            the_game.current_state = " " + ("1"*62) + "2"
            config['DBSession'].add(the_game)
            del(the_game)
        
        # End the game!
        self.make_request(app, "/odummo/make_move/{}?square=0".format(game_id), cookies,
            msg="Error making a final move",
            expect_forward = "/odummo/game/{}".format(game_id)
        )
        
        the_game = config['DBSession'].query(OdummoGame).filter(OdummoGame.id == game_id).first()
        self.assertEqual(the_game.current_state,
                "2111111112111111112111111112111111112111111112111111112111111112",
                msg="Winning move not correctly saved")
        
        self.assertEqual(the_game.winner, the_game.player1)
        
        # Try to view it again anyway
        self.make_request(app, "/odummo/game/{}".format(game_id), cookies,
            msg="Error viewing the game once completed"
        )
        
        self.fail("Rematch is not yet tested")
        self.fail("Check turn is not yet tested")