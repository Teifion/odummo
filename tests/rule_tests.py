import unittest
from collections import namedtuple

BoardObject = namedtuple('BoardObject', ['current_state', 'turn'])

b0 = '1111111 22221111221111112222222122121221222112112222111122221111'

b1 = """
        
        
        
   12   
   21   
   21   
   21   
   211  """.replace("\n", "")

from ..lib import rules

class OdummoRuleTester(unittest.TestCase):
    def test_validity(self):
        # print(rules.is_move_valid(b1, 1+1, 62))
        # print(rules.is_move_valid(b1, 2+1, 62))
        
        # print(rules.check_for_win(BoardObject(b0, 1)))
        # print(rules.check_for_win(BoardObject(b0, 2)))
        pass