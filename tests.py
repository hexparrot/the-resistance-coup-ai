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
        p.income()
        self.assertEquals(p.coins, 3)

    def test_foreign_aid(self):
        p = Player()
        p.foreign_aid()
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
        p.coup(influence)
        
        self.assertTrue(getattr(pp, position).revealed)
        self.assertEqual(p.coins, 0)

        with self.assertRaises(RuntimeError): 
            p.coup(pp.right)

    def test_perform(self):
        p = Player()
        pp = Player()
        with self.assertRaises(RuntimeError): 
            p.perform('dance')

        with self.assertRaises(RuntimeError):
            p.perform('dance', pp)

        with self.assertRaises(RuntimeError):
            p.perform('assasinate')

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

        pp.income()
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

        with self.assertRaises(RuntimeError):
            p.perform('assassinate', pp)

        self.assertEquals(pp.influence_remaining, 2)
        self.assertEquals(p.coins, 2)
        p.income()
        
        p.perform('assassinate', pp)
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
        
        p.left = Assassin()
        p.right = Duke()
        self.assertEqual(p.valid_actions, ['assassinate', 'tax'])

        p.left = Contessa()
        p.right = Ambassador()
        self.assertEqual(p.valid_actions, ['exchange'])

        p.left = Captain()
        p.right = Captain()
        self.assertEqual(p.valid_actions, ['steal'])

    def test_player_available_blocks(self):
        p = Player()

        p.left = Assassin()
        p.right = Duke()
        self.assertEqual(p.valid_blocks, ['foreign_aid'])

        p.left = Contessa()
        p.right = Ambassador()
        self.assertEqual(p.valid_blocks, ['assassinate', 'steal'])

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
        p.coup(influence)
        self.assertEquals(pp.influence_remaining, 1)

        if position == 'left':
            self.assertTrue(pp.left.revealed)
            self.assertFalse(pp.right.revealed)
        elif position == 'right':
            self.assertTrue(pp.right.revealed)
            self.assertFalse(pp.left.revealed)

        position, influence = pp.random_remaining_influence
        p.coins = 7
        p.coup(influence)

        self.assertEquals(pp.influence_remaining, 0)

        with self.assertRaises(RuntimeError): 
            position, influence = pp.random_remaining_influence


if __name__ == "__main__":
    unittest.main()




