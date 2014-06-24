import unittest
from coup import *

class TestCoup(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_player_class(self):
        p = Player()
        self.assertEquals(p.coins, 2)
        self.assertIsNone(p.left)
        self.assertIsNone(p.left)

    def test_income(self):
        p = Player()
        p.perform('income')
        self.assertEquals(p.coins, 3)

    def test_foreign_aid(self):
        p = Player()
        p.perform('foreign_aid')
        self.assertEquals(p.coins, 4)

    def test_influence_adding(self):
        p = Player()
        i = Influence()
        p.left = i
        self.assertIs(p.left, i)

        ii = Influence()
        p.right = ii
        self.assertIs(p.right, ii)

    def test_get_killed(self):
        p = Player()
        p.left = Influence()
        self.assertFalse(p.left.revealed)
        p.left.reveal()
        self.assertTrue(p.left.revealed)

    def test_swap_influence(self):
        p = Player()
        p.left = i = Influence()
        p.left.reveal()
        p.left = ii = Influence()
        self.assertIsNot(i, ii)
        self.assertFalse(p.left.revealed)  

    def test_influence_class(self):
        i = Influence()
        self.assertFalse(i.revealed, False)

    def test_coup(self):
        p = Player()
        pp = Player()

        p.left = Influence()
        pp.left = Influence()
        pp.right = Influence()

        p.coins = 7
        self.assertFalse(pp.left.revealed)

        position, influence = pp.random_remaining_influence
        p.perform('coup', influence)
        
        self.assertTrue(getattr(pp, position).revealed)
        self.assertEqual(p.coins, 0)

        with self.assertRaises(IllegalAction): 
            p.perform('coup', pp.right)

    def test_perform(self):
        p = Player()
        pp = Player()
        pp.left = Duke()
        
        with self.assertRaises(IllegalAction): 
            p.perform('dance')

        with self.assertRaises(IllegalAction):
            p.perform('dance', pp)

        with self.assertRaises(IllegalAction):
            p.perform('dance', pp.left)

        with self.assertRaises(TypeError):
            p.perform('assassinate')

        p.coins = 3
        p.perform('assassinate', pp.left)
        
        with self.assertRaises(IllegalAction):
            p.perform('assassinate', pp.left)

        p.coins = 3

        with self.assertRaises(IllegalTarget):
            p.perform('assassinate', pp.left)

    def test_subclass_class(self):
        for i in (Captain, Duke, Assassin, Ambassador, Contessa):
            instance = i()
            self.assertFalse(instance.revealed)
            instance.reveal()
            self.assertTrue(instance.revealed)

    def test_captain_steal(self):
        p = Player()
        pp = Player()

        self.assertEquals(p.coins, 2)
        self.assertEquals(pp.coins, 2)

        p.perform('steal', pp)
        self.assertEquals(p.coins, 4)
        self.assertEquals(pp.coins, 0)

        p.perform('steal', pp)
        self.assertEquals(p.coins, 4)
        self.assertEquals(pp.coins, 0)

        pp.perform('income')
        self.assertEquals(pp.coins, 1)
        p.perform('steal', pp)
        self.assertEquals(p.coins, 5)
        self.assertEquals(pp.coins, 0)
        
    def test_duke_tax(self):
        p = Player()

        self.assertEquals(p.coins, 2)
        p.perform('tax')
        self.assertEquals(p.coins, 5)

    def test_influence_remaining(self):
        p = Player()

        p.left = Influence()
        p.right = Influence()
        self.assertEquals(p.influence_remaining, 2)

        p.left.reveal()
        self.assertEquals(p.influence_remaining, 1)
        p.right.reveal()
        self.assertEquals(p.influence_remaining, 0)
        
    def test_assassin_assassinate(self):
        p = Player()
        pp = Player()

        p.left = Assassin()
        pp.left = Influence()
        pp.right = Influence()

        self.assertEquals(pp.influence_remaining, 2)
        position, influence = pp.random_remaining_influence

        with self.assertRaises(IllegalAction):
            p.perform('assassinate', influence)

        self.assertEquals(pp.influence_remaining, 2)
        self.assertEquals(p.coins, 2)
        p.perform('income')

        position, influence = pp.random_remaining_influence
        
        p.perform('assassinate', influence)
        self.assertEquals(p.coins, 0)
        self.assertEquals(pp.influence_remaining, 1)

    def test_ambassador_exchange(self):
        #badtest
        p = Player()
        p.left = Assassin()
        p.right = Contessa()

        self.assertEquals(p.influence_remaining, 2)
        p.perform('exchange')
        self.assertEquals(p.influence_remaining, 2)

        p.left.reveal()
        self.assertEquals(p.influence_remaining, 1)
        p.perform('exchange')
        self.assertEquals(p.influence_remaining, 1)

    def test_friendly_influence_strings(self):
        self.assertEquals(str(Ambassador()), 'Ambassador')
        self.assertEquals(str(Assassin()), 'Assassin')
        self.assertEquals(str(Captain()), 'Captain')
        self.assertEquals(str(Contessa()), 'Contessa')
        self.assertEquals(str(Duke()), 'Duke')

    def test_friendly_player_strings(self):
        p = Player()
        p.left = Assassin()
        p.right = Contessa()
        self.assertEqual(str(p), "Assassin Contessa")
        p.left = Duke()
        self.assertEqual(str(p), "Duke Contessa")
        p.right = Captain()
        self.assertEqual(str(p), "Duke Captain")

    def test_friendly_player_strings_alpha(self):
        p = Player()
        p.left = Assassin()
        p.right = Contessa()
        self.assertEqual(p.alpha, "Assassin Contessa")
        p.left = Duke()
        self.assertEqual(p.alpha, "Contessa Duke")
        p.right = Captain()
        self.assertEqual(p.alpha, "Captain Duke")

    def test_player_available_actions(self):
        p = Player()

        p.left = Contessa()
        p.right = Ambassador()
        self.assertEqual(p.valid_actions, ['exchange'])

        p.left = Captain()
        p.right = Captain()
        self.assertEqual(p.valid_actions, ['steal'])

        p.left = Assassin()
        p.right = Duke()
        self.assertEqual(p.valid_actions, ['assassinate', 'tax'])

        p.left.reveal()
        self.assertEqual(p.valid_actions, ['tax'])

    def test_player_available_blocks(self):
        p = Player()

        p.left = Assassin()
        p.right = Duke()
        self.assertEqual(p.valid_blocks, ['foreign_aid'])

        p.left = Contessa()
        p.right = Ambassador()
        self.assertEqual(p.valid_blocks, ['assassinate', 'steal'])

        p.right.reveal()
        self.assertEqual(p.valid_blocks, ['assassinate'])

        p.left = Captain()
        p.right = Captain()
        self.assertEqual(p.valid_blocks, ['steal'])

    def test_player_return_available_influence(self):
        p = Player()
        pp = Player()

        pp.left = Assassin()
        pp.right = Duke()

        self.assertEquals(pp.influence_remaining, 2)
        position, influence = pp.random_remaining_influence

        p.coins = 7
        p.perform('coup', influence)
        self.assertEquals(pp.influence_remaining, 1)

        if position == 'left':
            self.assertTrue(pp.left.revealed)
            self.assertFalse(pp.right.revealed)
        elif position == 'right':
            self.assertTrue(pp.right.revealed)
            self.assertFalse(pp.left.revealed)

        position, influence = pp.random_remaining_influence
        p.coins = 7
        p.perform('coup', influence)

        self.assertEquals(pp.influence_remaining, 0)

        with self.assertRaises(IllegalTarget): 
            position, influence = pp.random_remaining_influence

    def test_player_list_remaining_influences_friendly(self):
        p = Player()

        p.left = Assassin()
        p.right = Duke()

        self.assertEqual(p.status, "Assassin Duke")

        p.left.reveal()
        self.assertEqual(p.status, "<Assassin> Duke")

        p.right.reveal()
        self.assertEqual(p.status, "<Assassin> <Duke>")

    def test_gameplay_no_blocks(self):
        from itertools import cycle
        from random import choice, randint

        PLAYERS = 5
        testgame = Play_Coup(PLAYERS)

        for i in cycle(xrange(PLAYERS)):
            if not testgame.players[i].influence_remaining:
                continue
            elif sum(1 for p in xrange(PLAYERS) if testgame.players[p].influence_remaining) == 1:
                break

            available_actions = ['income', 'foreign_aid', 'coup', 'steal', 'tax', 'assassinate', 'exchange']
            
            while 1:
                try:
                    action = choice(available_actions)
                    if action in ['coup', 'assassinate']:
                        random_player = testgame.players[randint(0,PLAYERS-1)]
                        position, random_target = random_player.random_remaining_influence
                        testgame.players[i].perform(action, random_target)
                    elif action in ['steal']:
                        random_player = testgame.players[randint(0,PLAYERS-1)]
                        testgame.players[i].perform(action, random_player)
                    else:
                        testgame.players[i].perform(action)
                    break
                except (IllegalTarget, IllegalAction):
                    pass

if __name__ == "__main__":
    unittest.main()




