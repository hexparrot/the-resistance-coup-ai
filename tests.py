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
        p.coup(pp.left)
        self.assertTrue(pp.left.revealed)
        self.assertEqual(p.coins, 0)

        with self.assertRaises(RuntimeError): 
            p.coup(pp.right)

    def test_perform(self):
        p = Player()
        with self.assertRaises(RuntimeError): 
            p.perform('dance')

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
        

if __name__ == "__main__":
    unittest.main()




