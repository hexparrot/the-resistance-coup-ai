#!/usr/bin/env python2.7
"""
Python scripts to simulate the game "The Resistance: Coup designed by Rikki Tahta
The purpose of this project is to model human personalities and predict/score
behaviors and bluffs in order to win the game.

"""

__author__ = "William Dizon"
__license__ = "GNU GPL v3.0"
__version__ = "0.0.1"
__email__ = "wdchromium@gmail.com"

import unittest
from coup import *
from heuristics import *

class TestCoup(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_player_class(self):
        p = Player()
        self.assertEqual(p.coins, 2)
        self.assertIsNone(p.left)
        self.assertIsNone(p.left)

    def test_income(self):
        p = Player()
        p.perform('income')
        self.assertEqual(p.coins, 3)

    def test_foreign_aid(self):
        p = Player()
        p.perform('foreign_aid')
        self.assertEqual(p.coins, 4)

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
        p = AI_Persona()
        pp = AI_Persona()

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

        self.assertEqual(p.coins, 2)
        self.assertEqual(pp.coins, 2)

        p.perform('steal', pp)
        self.assertEqual(p.coins, 4)
        self.assertEqual(pp.coins, 0)

        p.perform('steal', pp)
        self.assertEqual(p.coins, 4)
        self.assertEqual(pp.coins, 0)

        pp.perform('income')
        self.assertEqual(pp.coins, 1)
        p.perform('steal', pp)
        self.assertEqual(p.coins, 5)
        self.assertEqual(pp.coins, 0)
        
    def test_duke_tax(self):
        p = Player()

        self.assertEqual(p.coins, 2)
        p.perform('tax')
        self.assertEqual(p.coins, 5)

    def test_influence_remaining(self):
        p = Player()

        p.left = Influence()
        p.right = Influence()
        self.assertEqual(p.influence_remaining, 2)

        p.left.reveal()
        self.assertEqual(p.influence_remaining, 1)
        p.right.reveal()
        self.assertEqual(p.influence_remaining, 0)
        
    def test_assassin_assassinate(self):
        p = AI_Persona()
        pp = AI_Persona()

        p.left = Assassin()
        pp.left = Influence()
        pp.right = Influence()

        self.assertEqual(pp.influence_remaining, 2)
        position, influence = pp.random_remaining_influence

        with self.assertRaises(IllegalAction):
            p.perform('assassinate', influence)

        self.assertEqual(pp.influence_remaining, 2)
        self.assertEqual(p.coins, 2)
        p.perform('income')

        position, influence = pp.random_remaining_influence
        
        p.perform('assassinate', influence)
        self.assertEqual(p.coins, 0)
        self.assertEqual(pp.influence_remaining, 1)

    def test_ambassador_exchange(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        p.left = Assassin()
        p.right = Contessa()

        self.assertEqual(len(testgame.court_deck), 5)

        self.assertEqual(p.influence_remaining, 2)
        p.perform('exchange', testgame.court_deck)
        self.assertEqual(p.influence_remaining, 2)

        self.assertTrue(all([not c.revealed for c in testgame.court_deck]))

        p.left.reveal()
        self.assertEqual(p.influence_remaining, 1)
        p.perform('exchange', testgame.court_deck)
        self.assertEqual(p.influence_remaining, 1)

        self.assertTrue(all([not c.revealed for c in testgame.court_deck]))

        self.assertEqual(len(testgame.court_deck), 5)

    def test_friendly_influence_strings(self):
        self.assertEqual(str(Ambassador()), 'Ambassador')
        self.assertEqual(str(Assassin()), 'Assassin')
        self.assertEqual(str(Captain()), 'Captain')
        self.assertEqual(str(Contessa()), 'Contessa')
        self.assertEqual(str(Duke()), 'Duke')

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
        self.assertListEqual(sorted(p.valid_actions), ['exchange'])

        p.left = Captain()
        p.right = Captain()
        self.assertListEqual(sorted(p.valid_actions), ['steal'])

        p.left = Assassin()
        p.right = Duke()
        self.assertListEqual(sorted(p.valid_actions), ['assassinate', 'tax'])

        p.left.reveal()
        self.assertListEqual(sorted(p.valid_actions), ['tax'])

    def test_player_available_blocks(self):
        p = Player()

        p.left = Assassin()
        p.right = Duke()
        self.assertListEqual(sorted(p.valid_blocks), ['foreign_aid'])

        p.left = Contessa()
        p.right = Ambassador()
        self.assertListEqual(sorted(p.valid_blocks), ['assassinate', 'steal'])

        p.right.reveal()
        self.assertListEqual(sorted(p.valid_blocks), ['assassinate'])

        p.left = Captain()
        p.right = Captain()
        self.assertListEqual(sorted(p.valid_blocks), ['steal'])

    def test_player_return_available_influence(self):
        p = AI_Persona()
        pp = AI_Persona()

        pp.left = Assassin()
        pp.right = Duke()

        self.assertEqual(pp.influence_remaining, 2)
        position, influence = pp.random_remaining_influence

        p.coins = 7
        p.perform('coup', influence)
        self.assertEqual(pp.influence_remaining, 1)

        if position == 'left':
            self.assertTrue(pp.left.revealed)
            self.assertFalse(pp.right.revealed)
        elif position == 'right':
            self.assertTrue(pp.right.revealed)
            self.assertFalse(pp.left.revealed)

        position, influence = pp.random_remaining_influence
        p.coins = 7
        p.perform('coup', influence)

        self.assertEqual(pp.influence_remaining, 0)

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

    def test_player_controls_influence(self):
        p = Player()
        
        p.left = Assassin()
        p.right = Duke()

        self.assertTrue(p.influences('Assassin'))
        self.assertTrue(p.influences('Duke'))
        self.assertFalse(p.influences('Contessa'))
        self.assertFalse(p.influences('Captain'))
        self.assertFalse(p.influences('Ambassador'))

        p.left.reveal()
        self.assertFalse(p.influences('Assassin'))
        
    def test_filter_out_players(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        pp = testgame.players[1]
        
        self.assertEqual(testgame.filter_out_players([p,pp]), {
            testgame.players[2],    
            testgame.players[3],
            testgame.players[4],        
            })
        
        self.assertEqual(testgame.filter_out_players([0,1]), {
            testgame.players[2],    
            testgame.players[3],
            testgame.players[4],        
            })

    def test_ai_persona(self):
        a = AI_Persona()
        self.assertIsInstance(a, Player)
        self.assertIsInstance(a.rules, dict)

        PLAYERS = 5
        testgame = Play_Coup(PLAYERS)

        for i in range(PLAYERS):
            self.assertIsInstance(testgame.players[i].rules, dict)

    def test_ai_persona_replace_player(self):
        testgame = Play_Coup(5)

        p = testgame.players[0]
        a = AI_Persona.clone(p)
        
        self.assertEqual(a.coins, p.coins)
        self.assertIs(a.left, p.left)
        self.assertIs(a.right, p.right)

    def test_ai_persona_replace_player(self):
        testgame = Play_Coup(5)

        a = AI_Persona.clone(testgame.players[0])
        testgame.players[0] = a

        self.assertIs(a, testgame.players[0])
        self.assertIsInstance(a, AI_Persona)

    def test_ai_persona_select_opponent(self):
        testgame = Play_Coup(5)

        a = AI_Persona.clone(testgame.players[0])
        testgame.players[0] = a

        z = testgame.players

        self.assertIsNot(a.select_opponent(z), a)
        self.assertIsNot(a.select_opponent(z), testgame.players[0])

        self.assertIsInstance(a.select_opponent(z), Player)

    def test_record_actions(self):
        testgame = Play_Coup(5)

        z = testgame.players[0]

        z.perform('income')
        self.assertEqual(z.public_information['perform'][0], 'income')
        z.perform('assassinate', testgame.players[1].left)
        self.assertEqual(z.public_information['perform'][1], 'assassinate')

        BlockedAction('assassinate', z, testgame.players[2], None)
        self.assertEqual(testgame.players[2].public_information['victim'][0], 'assassinate')

        BlockedAction('foreign_aid', z, None, testgame.players[2])
        self.assertEqual(testgame.players[2].public_information['spectator'][0], 'foreign_aid')

        BlockedAction('steal', z, None, testgame.players[2])
        self.assertEqual(testgame.players[2].public_information['spectator'][1], 'steal')

    def test_deduce(self):
        testgame = Play_Coup(5)

        p = testgame.players[0]

        self.assertEqual(p.probable_influences, {})

        p.public_information['perform'].extend(['tax','tax','tax'])
        p.public_information['spectator'].extend(['foreign_aid','foreign_aid'])

        self.assertEqual(p.probable_influences, {
            'Duke': WEIGHTS['performed_action'] * 3 + WEIGHTS['blocked_selflessly'] * 2
            })

        p.public_information['perform'].append('steal')
        self.assertEqual(p.probable_influences,  {
            'Duke': WEIGHTS['performed_action'] * 3 + WEIGHTS['blocked_selflessly'] * 2,
            'Captain':  WEIGHTS['performed_action'] * 1
            })

        p.public_information['perform'].append('steal')
        self.assertEqual(p.probable_influences, {
            'Duke': WEIGHTS['performed_action'] * 3 + WEIGHTS['blocked_selflessly'] * 2,
            'Captain':  WEIGHTS['performed_action'] * 2
            })

        p.public_information['spectator'].extend(['steal', 'steal', 'steal'])
        self.assertEqual(p.probable_influences, {
            'Duke': WEIGHTS['performed_action'] * 3 + WEIGHTS['blocked_selflessly'] * 2,
            'Captain':  WEIGHTS['performed_action'] * 2 + WEIGHTS['blocked_selflessly'] * 3,
            'Ambassador': WEIGHTS['blocked_selflessly'] * 3
            })

        p.public_information['spectator'].extend(['assassinate'])
        self.assertEqual(p.probable_influences, {
            'Duke': WEIGHTS['performed_action'] * 3 + WEIGHTS['blocked_selflessly'] * 2,
            'Captain':  WEIGHTS['performed_action'] * 2 + WEIGHTS['blocked_selflessly'] * 3,
            'Ambassador': WEIGHTS['blocked_selflessly'] * 3,
            'Contessa': WEIGHTS['blocked_selflessly'] * 1
            })

    def test_allowed_others(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        
        p.perform('foreign_aid')
        testgame.players[1].not_acting_like['spectator'].extend(['foreign_aid'])
        
        self.assertIn('Duke', testgame.players[1].improbable_influences)
        self.assertEqual(testgame.players[1].improbable_influences, {
            'Duke': abs(WEIGHTS['didnt_block_selflessly']) * 1 
            })

        ppp = testgame.players[2]
        
        ppp.perform('steal', testgame.players[0])        
        testgame.players[0].not_acting_like['victim'].extend(['steal'])
        testgame.players[3].not_acting_like['spectator'].extend(['steal'])
            
        self.assertEqual(testgame.players[0].improbable_influences, {
            'Duke': abs(WEIGHTS['suboptimal_move']) * 1,
            'Ambassador': abs(WEIGHTS['didnt_block_selfishly']) * 1,
            'Captain': abs(WEIGHTS['didnt_block_selfishly']) * 1 
            })

        self.assertEqual(testgame.players[3].improbable_influences, {
            'Ambassador': abs(WEIGHTS['didnt_block_selflessly']) * 1,
            'Captain': abs(WEIGHTS['didnt_block_selflessly']) * 1 
            })

    def test_remove_suspicion(self):
        p = AI_Persona()
        p.left = Captain()
        p.right = Assassin()

        p.public_information['perform'].extend(['steal', 'steal', 'steal'])
        self.assertEqual(p.probable_influences, {
            'Captain': WEIGHTS['performed_action'] * 3 
            })
        p.left.reveal()
        p.remove_suspicion('Captain')
        self.assertEqual(p.probable_influences, {})

        pp = AI_Persona()
        pp.left = Captain()
        pp.right = Assassin()

        pp.public_information['perform'].extend(['steal', 'steal', 'steal', 'assassinate'])
        self.assertEqual(pp.probable_influences, {
            'Captain': WEIGHTS['performed_action'] * 3,
            'Assassin': WEIGHTS['performed_action'] * 1
            })
        pp.right.reveal()
        pp.remove_suspicion('Assassin')
        self.assertEqual(pp.probable_influences, {
            'Captain': WEIGHTS['performed_action'] * 3
            })
        
        ppp = AI_Persona()
        ppp.left = Duke()
        ppp.right = Assassin()

        ppp.public_information['spectator'].extend(['foreign_aid', 'foreign_aid'])
        self.assertIn('Duke', ppp.probable_influences)
        ppp.left.reveal()
        ppp.remove_suspicion('Duke')
        self.assertEqual(ppp.probable_influences, {})

    def test_ai_profile_will_intervene_foreign_aid(self):
        p = AI_Persona() #not duke
        p.left = Assassin()
        p.right = Assassin()

        pp = AI_Persona() #not duke
        pp.left = Captain()
        pp.right = Captain()

        self.assertFalse(p.will_intervene('foreign_aid', pp))

        p.left = Duke()
        
        p.rules['honest_intervention']['foreign_aid'] = {
            'performer': lambda q: True
            }
        self.assertTrue(p.will_intervene('foreign_aid', pp))

        p.rules['honest_intervention']['foreign_aid'] = {
            'performer': lambda q: q.coins > 5
            }
        self.assertFalse(p.will_intervene('foreign_aid', pp))

        p.rules['calculated_intervention']['foreign_aid'] = {
            'performer': lambda q: q.influence_remaining == 2
            }
        self.assertTrue(p.will_intervene('foreign_aid', pp))

        pp.left.reveal()
        self.assertFalse(p.will_intervene('foreign_aid', pp))

    def test_ai_profile_will_intervene_steal_performer(self):
        p = AI_Persona() #not captain
        p.left = Assassin()
        p.right = Assassin()

        pp = AI_Persona() #not captain/amb
        pp.left = Contessa()
        pp.right = Contessa()

        ppp = AI_Persona() #captain
        ppp.left = Captain()
        ppp.right = Captain()

        self.assertFalse(ppp.will_intervene('steal', p, pp))

        p.coins = 2
        ppp.rules['honest_intervention']['steal'] = {
            'performer': lambda q: True
            }
        self.assertTrue(ppp.will_intervene('steal', p, pp))

        ppp.rules['honest_intervention']['steal'] = {
            'performer': lambda q: False
            }
        self.assertFalse(ppp.will_intervene('steal', p, pp))

        p.coins = 2
        ppp.rules['calculated_intervention']['steal'] = {
            'performer': lambda q: q.coins + 2 >= 3
            }
        self.assertTrue(ppp.will_intervene('steal', p, pp))
        
    def test_best_probable_actions(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        p.left = Duke()
        p.right = Captain()
        
        self.assertNotIn('assassinate', p.probable_actions)
        self.assertNotIn('tax', p.probable_actions)
        self.assertNotIn('steal', p.probable_actions)
        
        p.public_information['perform'].extend(['steal', 'steal', 'steal'])
        
        self.assertNotIn('assassinate', p.probable_actions)
        self.assertNotIn('tax', p.probable_actions)
        self.assertIn('steal', p.probable_actions)
        
        p.public_information['perform'].extend(['tax','tax','tax'])
        
        self.assertNotIn('assassinate', p.probable_actions)
        self.assertIn('tax', p.probable_actions)
        self.assertIn('steal', p.probable_actions)
        
        p.public_information['perform'].extend(['assassinate'])
        
        self.assertNotIn('assassinate', p.probable_actions)
        self.assertIn('tax', p.probable_actions)
        self.assertIn('steal', p.probable_actions)
        
        p.public_information['perform'].extend(['tax', 'assassinate','assassinate','assassinate'])

        self.assertIn('assassinate', p.probable_actions)
        self.assertIn('tax', p.probable_actions)
        self.assertNotIn('steal', p.probable_actions)

    def test_probable_blocks(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        
        p.public_information['perform'].extend(['tax'])
        self.assertIn('foreign_aid', p.probable_blocks)
        
        p.perform('steal', testgame.players[1])
        self.assertIn('steal', p.probable_blocks)
        
    def test_improbable_blocks(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        
        p.not_acting_like['spectator'].extend(['steal'])
        self.assertIn('steal', p.improbable_blocks)
        self.assertNotIn('assassinate', p.improbable_blocks)
        self.assertNotIn('foreign_aid', p.improbable_blocks)
        
        p.perform('income')
        self.assertIn('steal', p.improbable_blocks)
        self.assertNotIn('assassinate', p.improbable_blocks)
        self.assertIn('foreign_aid', p.improbable_blocks)
        
        p.not_acting_like['spectator'].extend(['assassinate'])
        p.not_acting_like['spectator'].extend(['assassinate'])
        
        self.assertNotIn('steal', p.improbable_blocks)
        self.assertIn('assassinate', p.improbable_blocks)
        self.assertIn('foreign_aid', p.improbable_blocks)   

    def test_ai_profile_will_intervene_steal_victim(self):
        p = AI_Persona() #not captain
        p.left = Assassin()
        p.right = Assassin()

        pp = AI_Persona() #not captain/amb
        pp.left = Contessa()
        pp.right = Contessa()

        ppp = AI_Persona() #captain
        ppp.left = Captain()
        ppp.right = Captain()

        pp.coins = 0
        self.assertFalse(ppp.will_intervene('steal', p, pp))

        ppp.rules['calculated_intervention']['steal'] = {
            'victim': lambda q: q.coins
            }
        self.assertFalse(ppp.will_intervene('steal', p, pp))

        pp.coins = 1
        self.assertTrue(ppp.will_intervene('steal', p, pp))

        pp.coins = 2
        self.assertTrue(ppp.will_intervene('steal', p, pp))

        ppp.rules['calculated_intervention']['steal'] = {
            'victim': lambda q: q.coins >= 5
            }

        self.assertFalse(ppp.will_intervene('steal', p, pp))
        pp.coins = 5
        self.assertTrue(ppp.will_intervene('steal', p, pp))

    def test_naive_priorities(self):
        p = AI_Persona()
        p.left = Assassin()
        p.right = Assassin()

        self.assertEqual(p.naive_priority(), 'income')
        p.coins = 3
        self.assertEqual(p.naive_priority(), 'assassinate')

        p = AI_Persona()
        p.left = Duke()
        p.right = Duke()

        self.assertEqual(p.naive_priority(), 'tax')
        p.coins = 7
        self.assertEqual(p.naive_priority(), 'coup')

        p = AI_Persona()
        p.left = Captain()
        p.right = Captain()

        self.assertEqual(p.naive_priority(), 'coin')
        p.coins = 7
        self.assertEqual(p.naive_priority(), 'coup')

        p = AI_Persona()
        p.left = Contessa()
        p.right = Contessa()

        self.assertEqual(p.naive_priority(), 'coin')
        p.coins = 7
        self.assertEqual(p.naive_priority(), 'coup')

        p = AI_Persona()
        p.left = Ambassador()
        p.right = Ambassador()

        self.assertEqual(p.naive_priority(), 'switch')

        p.coins = 10
        self.assertEqual(p.naive_priority(), 'coup')
        p.coins = 11
        self.assertEqual(p.naive_priority(), 'coup')
        p.coins = 12
        self.assertEqual(p.naive_priority(), 'coup')
    
    def test_random_targetable_player(self):
        testgame = Play_Coup(5)

        p = testgame.players[0]
        self.assertIsNot(testgame.random_targetable_player(p), p)
        self.assertIsInstance(testgame.random_targetable_player(p), Player)

        for _ in range(50):
            self.assertIsNot(testgame.random_targetable_player(p), p)

        pp = testgame.players[1]

        for _ in range(50):
            self.assertIsNot(testgame.random_targetable_player(p), p)

    def test_random_targetable_half_health_player(self):
        testgame = Play_Coup(5)

        p = testgame.players[0]
        self.assertIsNot(testgame.random_targetable_player(p), p)
        self.assertIsNone(testgame.random_targetable_player(p, [1]))

        pp = testgame.players[1]
        pp.left.reveal()
        self.assertIs(testgame.random_targetable_player(p, [1]), pp)
        self.assertIsNot(testgame.random_targetable_player(p, [1]), testgame.players[0])
        self.assertIsNot(testgame.random_targetable_player(p, [1]), testgame.players[2])
        self.assertIsNot(testgame.random_targetable_player(p, [1]), testgame.players[3])
        self.assertIsNot(testgame.random_targetable_player(p, [1]), testgame.players[4])

        ppp = testgame.players[2]
        ppp.left.reveal()
        self.assertIsNot(testgame.random_targetable_player(p, [1]), testgame.players[0])
        self.assertIsNot(testgame.random_targetable_player(p, [1]), testgame.players[3])
        self.assertIsNot(testgame.random_targetable_player(p, [1]), testgame.players[4])

    def test_random_targetable_player_by_coins(self):
        testgame = Play_Coup(5)

        p = testgame.players[0]
        self.assertIsNot(testgame.random_targetable_player_by_coins(p), p)
        self.assertIsNone(testgame.random_targetable_player_by_coins(p, [0,0]))
        self.assertIsNone(testgame.random_targetable_player_by_coins(p, [0,1]))
        self.assertIsNone(testgame.random_targetable_player_by_coins(p, [1,1]))

        pp = testgame.players[1]
        pp.coins = 3
        self.assertIsNot(testgame.random_targetable_player_by_coins(p, [3,12]), p)
        self.assertIs(testgame.random_targetable_player_by_coins(p, [3,12]), pp)

        ppp = testgame.players[2]
        ppp.coins = 12
        self.assertIsNot(testgame.random_targetable_player_by_coins(p, [4,12]), p)
        self.assertIsNot(testgame.random_targetable_player_by_coins(p, [4,12]), pp)
        self.assertIs(testgame.random_targetable_player_by_coins(p, [4,12]), ppp)

        testgame.players[4].left.reveal()
        testgame.players[4].right.reveal()
        self.assertIsNot(testgame.random_targetable_player_by_coins(p, [4,12]), testgame.players[4])                           

    def test_random_targetable_player_by_wealth(self):
        testgame = Play_Coup(5)

        p = testgame.players[0]
        testgame.players[1].coins = 2
        testgame.players[2].coins = 3
        testgame.players[3].coins = 4
        testgame.players[4].coins = 5

        self.assertIs(testgame.random_richest_player(p), testgame.players[4])
        testgame.players[4].left.reveal()
        self.assertIs(testgame.random_richest_player(p), testgame.players[4])
        testgame.players[4].right.reveal()
        self.assertIs(testgame.random_richest_player(p), testgame.players[3])

        testgame.players[2].coins = 4

        self.assertIsNot(testgame.random_richest_player(p), testgame.players[0])
        self.assertIsNot(testgame.random_richest_player(p), testgame.players[1])
        self.assertIsNot(testgame.random_richest_player(p), testgame.players[4])

        for _ in range(50):
            self.assertEqual(testgame.random_richest_player(p).coins, 4)        
    
    def test_cannot_target_self(self):
        testgame = Play_Coup(5)

        p = testgame.players[0]
        p.perform('tax')

        with self.assertRaises(IllegalTarget): 
            p.perform('assassinate', p.left)

        with self.assertRaises(IllegalTarget): 
            p.perform('assassinate', p.right)

    def test_exception_blocked_action(self):
        testgame = Play_Coup(5)
        
        action = 'steal'
        performer = testgame.players[0]
        victim = testgame.players[1]
        spectator = testgame.players[2]

        ex = BlockedAction(action, performer, victim, spectator)

        self.assertEqual(ex.action, action)
        self.assertEqual(ex.performer, performer)
        self.assertEqual(ex.victim, victim)
        self.assertEqual(ex.spectator, spectator)
        self.assertIsInstance(ex.action, str)
        self.assertIsInstance(ex.performer, Player)
        self.assertIsInstance(ex.victim, Player)
        self.assertIsInstance(ex.spectator, Player)
        
        try:
            raise BlockedAction(action, performer, victim, spectator)
        except BlockedAction as e:
            self.assertEqual(e.message, '{0} performs {1} on {2}--blocked by {3}'.format(performer,
                                                                                         action,
                                                                                         victim,
                                                                                         spectator))

        action = 'foreign_aid'
        performer = testgame.players[0]
        victim = None
        spectator = testgame.players[2]
        
        try:
            raise BlockedAction(action, performer, victim, spectator)
        except BlockedAction as e:
            self.assertEqual(e.message, "{0} blocks {1}'s {2}".format(spectator,
                                                                      performer,
                                                                      action))

        action = 'assassinate'
        performer = testgame.players[0]
        victim = testgame.players[1]
        spectator = None
        
        try:
            raise BlockedAction(action, performer, victim, spectator)
        except BlockedAction as e:
            self.assertEqual(e.message, "{0} blocks {1}'s {2}".format(victim,
                                                                      performer,
                                                                      action))

    def test_gameplay_random_actions_random_targets_no_blocks(self):
        """
        AI PROFILE:
        
        Action          Used        Targets     Blocked     
        income          yes
        foreign_aid     yes                     no
        coup            yes
        steal           yes         random      no
        tax             yes
        assassinate     yes         random      no
        exchange        yes         random      no

        """
        from itertools import cycle
        from random import choice, randint

        PLAYERS = 5
        testgame = Play_Coup(PLAYERS)

        for i in cycle(range(PLAYERS)):
            acting_player = testgame.players[i]
            
            if not acting_player.influence_remaining:
                continue
            elif sum(1 for p in range(PLAYERS) if testgame.players[p].influence_remaining) == 1:
                return testgame.players[i].alpha
            
            while 1:
                try:
                    action = choice(Play_Coup.ACTIONS['all'])
                    if action in Play_Coup.ACTIONS['targets_influence']:
                        random_player = testgame.random_targetable_player(acting_player)
                        position, random_target = random_player.random_remaining_influence
                        testgame.players[i].perform(action, random_target)
                    elif action in Play_Coup.ACTIONS['targets_player']:
                        random_player = testgame.random_targetable_player(acting_player)
                        testgame.players[i].perform(action, random_player)
                    elif action == 'exchange':
                        testgame.players[i].perform(action, testgame.court_deck)
                    else:
                        testgame.players[i].perform(action)
                except (IllegalTarget, IllegalAction):
                    pass
                else:
                    break

    def test_gameplay_random_actions_random_targets_honest_blocks_no_doubts(self):
        """
        AI PROFILE:
        
        Action          Used        Targets     Blocked     
        income          yes
        foreign_aid     yes                     if random char is duke
        coup            yes
        steal           yes         random      victim/honest
        tax             yes
        assassinate     yes         random      victim/honest
        exchange        yes         random      no

        """
        from itertools import cycle
        from random import choice, randint

        PLAYERS = 5
        testgame = Play_Coup(PLAYERS)

        for i in cycle(range(PLAYERS)):
            acting_player = testgame.players[i]
            
            if not acting_player.influence_remaining:
                continue
            elif sum(1 for p in range(PLAYERS) if testgame.players[p].influence_remaining) == 1:
                return testgame.players[i].alpha
            
            while 1:
                try:
                    action = choice(Play_Coup.ACTIONS['all'])
                    if action in Play_Coup.ACTIONS['blockable']:
                        random_player = testgame.random_targetable_player(acting_player)
                        if action not in random_player.valid_blocks:
                            if action in Play_Coup.ACTIONS['targets_influence']:
                                position, random_target = random_player.random_remaining_influence
                                testgame.players[i].perform(action, random_target)
                            elif action in Play_Coup.ACTIONS['targets_player']:
                                testgame.players[i].perform(action, random_player)
                    else:
                        if action in Play_Coup.ACTIONS['targets_influence']:
                            random_player = testgame.random_targetable_player(acting_player)
                            position, random_target = random_player.random_remaining_influence
                            testgame.players[i].perform(action, random_target)
                        elif action == 'exchange':
                            testgame.players[i].perform(action, testgame.court_deck)
                        else:
                            testgame.players[i].perform(action)
                except (IllegalTarget, IllegalAction):
                    pass
                else:
                    break

    def test_gameplay_random_actions_calculated_targets_selfish_blocks_no_doubts(self):
        """
        AI PROFILE:
        
        Action          Used        Targets     Blocked     
        income          yes
        foreign_aid     yes                     any available duke
        coup            yes
        steal           yes         richest     victim only
        tax             yes
        assassinate     yes         weakest     victim only
        exchange        yes         random      no

        """
        from itertools import cycle
        from random import choice, randint

        PLAYERS = 5
        testgame = Play_Coup(PLAYERS)

        for i in cycle(range(PLAYERS)):
            acting_player = testgame.players[i]
            
            if not acting_player.influence_remaining:
                continue
            elif sum(1 for p in range(PLAYERS) if testgame.players[p].influence_remaining) == 1:
                return testgame.players[i].alpha
            
            while 1:
                try:
                    action = choice(Play_Coup.ACTIONS['all'])
                    if action == 'steal':
                        random_player = testgame.random_richest_player(acting_player)
                        if 'steal' in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)
                        else:
                            testgame.players[i].perform(action, random_player)
                    elif action == 'assassinate':
                        random_player = testgame.random_targetable_player(acting_player, [1])or \
                                        testgame.random_richest_player(acting_player)
                        if 'assassinate' in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)
                        else:
                            position, random_target = random_player.random_remaining_influence
                            testgame.players[i].perform(action, random_target)
                    elif action == 'foreign_aid':
                        for savior in range(PLAYERS):
                            if savior != i and action in testgame.players[savior].valid_blocks:
                                raise BlockedAction(action, acting_player, None, testgame.players[savior])
                            else:
                                testgame.players[i].perform(action)
                    elif action == 'exchange':
                        testgame.players[i].perform(action, testgame.court_deck)
                    elif action == 'coup':
                        random_player = testgame.random_targetable_player(acting_player, [1]) or \
                                        testgame.random_richest_player(acting_player)
                        position, random_target = random_player.random_remaining_influence
                        testgame.players[i].perform(action, random_target)
                    else:
                        testgame.players[i].perform(action)
                except (IllegalTarget, IllegalAction):
                    pass
                except BlockedAction as e:
                    break
                else:
                    break

    def test_gameplay_naive_actions_calculated_targets_selfish_blocks_no_doubts(self):
        """
        AI PROFILE:
        
        Action          Used        Targets     Blocked     
        income          yes
        foreign_aid     yes                     any available duke
        coup            yes
        steal           yes         anybody     victim only
        tax             yes
        assassinate     yes         weakest     victim only
        exchange        yes         random      no

        """
        from itertools import cycle
        from random import choice, randint

        PLAYERS = 5
        testgame = Play_Coup(PLAYERS)

        for i in cycle(range(PLAYERS)):
            acting_player = testgame.players[i]
            
            if not acting_player.influence_remaining:
                continue
            elif sum(1 for p in range(PLAYERS) if testgame.players[p].influence_remaining) == 1:
                return testgame.players[i].alpha
            
            while 1:
                try:
                    action = acting_player.random_naive_priority()
                    if action == 'steal':
                        random_player = acting_player.select_opponent(testgame.players)
                        if 'steal' in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)
                        else:
                            testgame.players[i].perform(action, random_player)
                    elif action == 'assassinate':
                        random_player = acting_player.select_opponent(testgame.players)
                        if 'assassinate' in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)
                        else:
                            position, random_target = random_player.random_remaining_influence
                            testgame.players[i].perform(action, random_target)
                    elif action == 'foreign_aid':
                        for savior in range(PLAYERS):
                            if savior != i and action in testgame.players[savior].valid_blocks:
                                raise BlockedAction(action, acting_player, None, testgame.players[savior])
                            else:
                                testgame.players[i].perform(action)
                    elif action == 'exchange':
                        testgame.players[i].perform(action, testgame.court_deck)
                    elif action == 'coup':
                        random_player = acting_player.select_opponent(testgame.players)
                        position, random_target = random_player.random_remaining_influence
                        testgame.players[i].perform(action, random_target)
                    else:
                        testgame.players[i].perform(action)
                except (IllegalTarget, IllegalAction):
                    pass
                except BlockedAction as e:
                    break
                else:
                    break

    def test_gameplay_naive_actions_calculated_targets_calculated_blocks_no_doubts(self):
        """
        AI PROFILE:
        
        Action          Used        Targets     Blocked     
        income          yes
        foreign_aid     yes                     victim/by ai profile
        coup            yes
        steal           yes         anybody     victim/by ai profile
        tax             yes
        assassinate     yes         weakest     victim/by ai profile
        exchange        yes         random      no

        """
        from itertools import cycle
        from random import choice, randint

        PLAYERS = 5
        testgame = Play_Coup(PLAYERS)

        for i in cycle(range(PLAYERS)):
            acting_player = testgame.players[i]
            
            if not acting_player.influence_remaining:
                continue
            elif sum(1 for p in range(PLAYERS) if testgame.players[p].influence_remaining) == 1:
                return testgame.players[i].alpha
            
            while 1:
                try:
                    action = acting_player.random_naive_priority()

                    if action in Play_Coup.ACTIONS['blockable']:
                        if action == 'steal':
                            random_player = acting_player.select_opponent(testgame.players)
                            if 'steal' in random_player.valid_blocks:
                                raise BlockedAction(action, acting_player, random_player, None)
                            else:
                                for savior in range(PLAYERS):
                                    if savior != i and \
                                       random_player is not testgame.players[savior] and \
                                       testgame.players[savior].will_intervene(action, acting_player, random_player):
                                        raise BlockedAction(action, acting_player, random_player, testgame.players[savior])
                                else:
                                    testgame.players[i].perform(action, random_player)
                        elif action == 'assassinate':
                            random_player = acting_player.select_opponent(testgame.players)
                            if 'assassinate' in random_player.valid_blocks:
                                raise BlockedAction(action, acting_player, random_player, None)
                            else:
                                for savior in range(PLAYERS):
                                    if savior != i and \
                                       random_player is not testgame.players[savior] and \
                                       testgame.players[savior].will_intervene(action, acting_player, random_player):
                                        raise BlockedAction(action, acting_player, random_player, testgame.players[savior])
                                else:
                                    position, random_target = random_player.random_remaining_influence
                                    testgame.players[i].perform(action, random_target)
                        elif action == 'foreign_aid':
                            for savior in range(PLAYERS):
                                if savior != i and testgame.players[savior].will_intervene(action, acting_player):
                                    raise BlockedAction(action, acting_player, None, testgame.players[savior])
                            else:
                                testgame.players[i].perform(action)
                    else:
                        if action == 'exchange':
                            testgame.players[i].perform(action, testgame.court_deck)
                        elif action == 'coup':
                            random_player = acting_player.select_opponent(testgame.players)
                            position, random_target = random_player.random_remaining_influence
                            testgame.players[i].perform(action, random_target)
                        else:
                            testgame.players[i].perform(action)
                except (IllegalTarget, IllegalAction):
                    pass
                except BlockedAction as e:
                    break
                else:
                    break

    def test_gameplay_calculated_actions_calculated_targets_calculated_blocks_no_doubts(self):
        """
        AI PROFILE:
        
        Action          Used        Targets     Blocked     
        income          yes
        foreign_aid     yes                     victim/by ai profile
        coup            yes
        steal           yes         best_guess  victim/by ai profile
        tax             yes
        assassinate     yes         best_guess  victim/by ai profile
        exchange        yes         random      no

        """
        from itertools import cycle
        from random import choice, randint

        PLAYERS = 5
        testgame = Play_Coup(PLAYERS)

        for i in cycle(range(PLAYERS)):
            acting_player = testgame.players[i]
            
            if not acting_player.influence_remaining:
                continue
            elif sum(1 for p in range(PLAYERS) if testgame.players[p].influence_remaining) == 1:
                return testgame.players[i].alpha
            
            while 1:
                try:
                    action = acting_player.random_naive_priority()

                    if action == 'steal':
                        random_player = acting_player.select_opponent(testgame.players)
                        if set(random_player.probable_influences).intersection(set([str(a()) for a in Influence.__subclasses__() if action in a.BLOCKS])):
                            raise RethinkAction(action, acting_player, random_player)
                        if 'steal' in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)
                        else:
                            for savior in range(PLAYERS):
                                if savior != i and \
                                   random_player is not testgame.players[savior] and \
                                   testgame.players[savior].will_intervene(action, acting_player, random_player):
                                    raise BlockedAction(action, acting_player, random_player, testgame.players[savior])
                            else:
                                testgame.players[i].perform(action, random_player)
                    elif action == 'assassinate':
                        random_player = acting_player.select_opponent(testgame.players)
                        if set(random_player.probable_influences).intersection(set([str(a()) for a in Influence.__subclasses__() if action in a.BLOCKS])):
                            raise RethinkAction(action, acting_player, random_player)
                        if 'assassinate' in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)
                        else:
                            for savior in range(PLAYERS):
                                if savior != i and \
                                   random_player is not testgame.players[savior] and \
                                   testgame.players[savior].will_intervene(action, acting_player, random_player):
                                    raise BlockedAction(action, acting_player, random_player, testgame.players[savior])
                            else:
                                position, random_target = random_player.random_remaining_influence
                                testgame.players[i].perform(action, random_target)
                                random_player.remove_suspicion(str(random_target))
                    elif action == 'foreign_aid':
                        for savior in range(PLAYERS):
                            if savior != i and testgame.players[savior].will_intervene(action, acting_player):
                                raise BlockedAction(action, acting_player, None, testgame.players[savior])
                        else:
                            testgame.players[i].perform(action)
                    elif action == 'exchange':
                        testgame.players[i].perform(action, testgame.court_deck)
                    elif action == 'coup':
                        random_player = acting_player.select_opponent(testgame.players)
                        position, random_target = random_player.random_remaining_influence
                        testgame.players[i].perform(action, random_target)
                        random_player.remove_suspicion(str(random_target))
                    else:
                        testgame.players[i].perform(action)
                except (IllegalTarget, IllegalAction):
                    pass
                except BlockedAction:
                    break
                except RethinkAction as e:
                    pass
                else:
                    break

    def test_gameplay_calculated_actions_calculated_targets_more_calculated_blocks_no_doubts(self):
        """
        AI PROFILE:
        
        Action          Used        Targets     Blocked     
        income          yes
        foreign_aid     yes                     victim/by ai profile
        coup            yes
        steal           yes         best_guess  victim/by ai profile
        tax             yes
        assassinate     yes         best_guess  victim/by ai profile
        exchange        yes         random      no

        """
        from itertools import cycle
        from random import random

        PLAYERS = 5
        testgame = Play_Coup(PLAYERS)

        for i in cycle(range(PLAYERS)):
            acting_player = testgame.players[i]
            
            if not acting_player.influence_remaining:
                continue
            elif sum(1 for p in range(PLAYERS) if testgame.players[p].influence_remaining) == 1:
                return testgame.players[i].alpha
            
            while 1:
                try:
                    action = acting_player.random_naive_priority()

                    if action == 'steal':
                        random_player = acting_player.select_opponent(testgame.players)
                        if (action in random_player.probable_blocks and random() > .24) or \
                            action in random_player.valid_blocks:
                            raise RethinkAction(action, acting_player, random_player)

                        for savior in testgame.filter_out_players([acting_player, random_player]):
                            if savior.will_intervene(action, acting_player, random_player):
                                raise BlockedAction(action, acting_player, random_player, savior)
                        else:
                            acting_player.perform(action, random_player)
                    elif action == 'assassinate':
                        random_player = acting_player.select_opponent(testgame.players)
                        if (action in random_player.probable_blocks and random() > .24) or \
                            action in random_player.valid_blocks:
                            raise RethinkAction(action, acting_player, random_player)

                        for savior in testgame.filter_out_players([acting_player, random_player]):
                            if savior.will_intervene(action, acting_player, random_player):
                                raise BlockedAction(action, acting_player, random_player, savior)
                        else:
                            position, random_target = random_player.random_remaining_influence
                            acting_player.perform(action, random_target)
                            random_player.remove_suspicion(str(random_target))
                    elif action == 'foreign_aid':
                        for savior in testgame.filter_out_players([acting_player]):
                            if savior.will_intervene(action, acting_player):
                                raise BlockedAction(action, acting_player, None, savior)
                        else:
                            acting_player.perform(action)
                    elif action == 'exchange':
                        acting_player.perform(action, testgame.court_deck)
                    elif action == 'coup':
                        random_player = acting_player.select_opponent(testgame.players)
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                        random_player.remove_suspicion(str(random_target))
                    else:
                        acting_player.perform(action)
                except (IllegalTarget, IllegalAction):
                    pass
                except BlockedAction:
                    break
                except RethinkAction as e:
                    pass
                else:
                    break

def gameplay_suite():
    suite = unittest.TestSuite()
    gameplay_tests = list(m for m in dir(TestCoup) \
                          if callable(getattr(TestCoup,m)) \
                          and m.startswith('test_gameplay'))
    
    for i in gameplay_tests:
        suite.addTest(TestCoup(i))
    return suite

if __name__ == "__main__":
    RUN_ALL_TESTS = True

    if RUN_ALL_TESTS:
        unittest.main()
    else:
        s = gameplay_suite()
        unittest.TextTestRunner().run(s)

