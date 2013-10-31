import unittest

b1 = """
        
        
        
   12   
   21   
   21   
   21   
   211  """.replace("\n", "")

from ..lib import rules

class OdummoRuleTester(unittest.TestCase):
    def test_validity(self):
        print(rules.is_move_valid(b1, 1+1, 62))
        print(rules.is_move_valid(b1, 2+1, 62))
