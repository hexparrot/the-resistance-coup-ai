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
            
    def test_game_winner(self):
        testgame = Play_Coup(5)
        
        self.assertIsNone(testgame.winner)
        
        for p in testgame.players:
            p.left.reveal()
            p.right.reveal()
        
        testgame.players[0].left.revealed = False
        
        self.assertIs(testgame.winner, testgame.players[0])

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
        
    def test_membership_of_influence(self):
        p = Player()
        p.left = Assassin()
        p.right = Contessa()
        
        self.assertFalse('Ambassador' in p)
        self.assertTrue('Assassin' in p)
        self.assertFalse('Captain' in p)
        self.assertTrue('Contessa' in p)
        self.assertFalse('Duke' in p)

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
        
        filtered = testgame.filter_out_players([p,pp])
        self.assertNotIn(p, filtered)
        self.assertNotIn(pp, filtered)
        self.assertIn(testgame.players[2], filtered)
        self.assertIn(testgame.players[3], filtered)
        self.assertIn(testgame.players[4], filtered)
            
        testgame.players[3].left.reveal()
        testgame.players[3].right.reveal()
        
        filtered = testgame.filter_out_players([testgame.players[0], testgame.players[1]])
        self.assertNotIn(p, filtered)
        self.assertNotIn(pp, filtered)
        self.assertIn(testgame.players[2], filtered)
        self.assertNotIn(testgame.players[3], filtered)
        self.assertIn(testgame.players[4], filtered)
            
    def test_len_remaining_players(self):
        testgame = Play_Coup(3)
        
        self.assertEqual(len(testgame), 3)
        testgame.players[0].left.reveal()
        self.assertEqual(len(testgame), 3)
        testgame.players[0].right.reveal()
        self.assertEqual(len(testgame), 2)
        testgame.players[1].left.reveal()
        self.assertEqual(len(testgame), 2)
        testgame.players[1].right.reveal()
        self.assertEqual(len(testgame), 1)
        testgame.players[2].left.reveal()
        self.assertEqual(len(testgame), 1)
        testgame.players[2].right.reveal()
        self.assertEqual(len(testgame), 0)
    
    def test_coup_influence_binary(self):
        testgame = Play_Coup(5)
        testgame.players[0].left = Ambassador()
        testgame.players[0].right = Ambassador()
        testgame.players[1].left = Assassin()
        testgame.players[1].right = Assassin()
        testgame.players[2].left = Captain()
        testgame.players[2].right = Captain()
        testgame.players[3].left = Contessa()
        testgame.players[3].right = Contessa()
        testgame.players[4].left = Duke()
        testgame.players[4].right = Duke()
        
        self.assertEqual(testgame.influence_binary, \
                         (1,0,0,0,0, 0,1,0,0,0, 0,0,1,0,0, 0,0,0,1,0, 0,0,0,0,1))
                         
        testgame.players[0].left = Ambassador()
        testgame.players[0].right = Assassin()
        testgame.players[1].left = Assassin()
        testgame.players[1].right = Captain()
        testgame.players[2].left = Captain()
        testgame.players[2].right = Contessa()
        testgame.players[3].left = Contessa()
        testgame.players[3].right = Duke()
        testgame.players[4].left = Duke()
        testgame.players[4].right = Ambassador()
        
        self.assertEqual(testgame.influence_binary, \
                         (1,1,0,0,0, 0,1,1,0,0, 0,0,1,1,0, 0,0,0,1,1, 1,0,0,0,1))
                         
    def test_influence_binary(self):
        p = Player()
        p.left = Assassin()
        p.right = Contessa()
        self.assertEqual(p.influence_binary, (0,1,0,1,0))
        
        p.left = Duke()
        p.right = Ambassador()
        self.assertEqual(p.influence_binary, (1,0,0,0,1))

    def test_ai_persona(self):
        a = AI_Persona()
        self.assertIsInstance(a, Player)
        self.assertIsInstance(a.rules, dict)

        PLAYERS = 5
        testgame = Play_Coup(PLAYERS)

        for i in range(PLAYERS):
            self.assertIsInstance(testgame.players[i].rules, dict)

    def test_ai_persona_clone(self):
        testgame = Play_Coup(5)

        p = testgame.players[0]
        a = p.clone()        
        self.assertEqual(a.coins, p.coins)
        self.assertIsNot(a.left, p.left)
        self.assertIsNot(a.right, p.right)
        
        self.assertEqual(type(a.left), type(p.left))
        self.assertEqual(type(a.right), type(p.right))

        testgame.players[0] = a

        self.assertEqual(str(a), str(testgame.players[0]))
        self.assertIsInstance(a, AI_Persona)

    def test_ai_persona_select_opponent(self):
        testgame = Play_Coup(5)

        p = testgame.players[0]
        
        for i in range(150):
            self.assertIsNot(p, p.select_opponent(testgame.players))

        pppp = testgame.players[4]
        pppp.left.reveal()
        pppp.right.reveal()
        
        for i in range(150):
            self.assertIsNot(p, p.select_opponent(testgame.players))
            self.assertIsNot(pppp, p.select_opponent(testgame.players))
            
        testgame = Play_Coup(2)
        p = testgame.players[0]
        for i in range(150):
            self.assertIsNot(p, p.select_opponent(testgame.players))
            
    def test_probability_player_influences(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        p.left = Assassin()
        p.right = Assassin()
        pp = testgame.players[1]
        pp.left = Contessa()
        pp.right = Contessa()
        ppp = testgame.players[2]
        ppp.left = Duke()
        ppp.right = Contessa()
        
        self.assertAlmostEqual(AI_Persona.probability_player_influences(testgame.players, pp, 'Contessa', None), 0.37142857142857144)
        self.assertAlmostEqual(AI_Persona.probability_player_influences(testgame.players, pp, 'Contessa', p), 0.423076923076923)
        self.assertAlmostEqual(AI_Persona.probability_player_influences(testgame.players, pp, 'Contessa', ppp), 0.2948717948717948) 
        
        pp.right.reveal()
        self.assertAlmostEqual(AI_Persona.probability_player_influences(testgame.players, pp, 'Contessa', None), 0.27472527472527475) 
        self.assertAlmostEqual(AI_Persona.probability_player_influences(testgame.players, pp, 'Contessa', p), 0.3181818181818181) 
        self.assertAlmostEqual(AI_Persona.probability_player_influences(testgame.players, pp, 'Contessa', ppp), 0.16666666666666674) 

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
        
    def test_blocked_actions_cost(self):
        testgame = Play_Coup(5)
        
        z = testgame.players[0]
        
        z.coins = 5
        self.assertEqual(z.coins, 5)
        BlockedAction('assassinate', z, testgame.players[2], None)
        self.assertEqual(z.coins, 2)

    def test_actions_for_influences(self):
        self.assertEqual(Influence.actions_for_influences('Assassin'), ['assassinate'])
        self.assertEqual(Influence.actions_for_influences('Contessa'), [])
        self.assertEqual(Influence.actions_for_influences('Duke'), ['tax'])
        self.assertEqual(Influence.actions_for_influences('Ambassador'), ['exchange'])
        self.assertEqual(Influence.actions_for_influences('Captain'), ['steal'])
        
        self.assertEqual(Influence.actions_for_influences(['Assassin', 'Duke']), ['assassinate', 'tax'])
        self.assertEqual(Influence.actions_for_influences(['Contessa', 'Assassin']), ['assassinate'])
        self.assertEqual(Influence.actions_for_influences(['Duke', 'Captain']), ['steal', 'tax'])
        self.assertEqual(Influence.actions_for_influences(['Ambassador', 'Ambassador']), ['exchange'])
        self.assertEqual(Influence.actions_for_influences(['Captain', 'Assassin']), ['assassinate', 'steal'])
        
        self.assertEqual(Influence.actions_for_influences('Assassin Duke'), ['assassinate', 'tax'])
        self.assertEqual(Influence.actions_for_influences('Assassin Contessa'), ['assassinate'])
        self.assertEqual(Influence.actions_for_influences('Duke Captain'), ['steal', 'tax'])
        self.assertEqual(Influence.actions_for_influences('Ambassador Ambassador'), ['exchange'])
        self.assertEqual(Influence.actions_for_influences('Captain Assassin'), ['assassinate', 'steal'])

    def test_blocks_for_influences(self):
        self.assertEqual(Influence.blocks_for_influences('Assassin'), [])
        self.assertEqual(Influence.blocks_for_influences('Contessa'), ['assassinate'])
        self.assertEqual(Influence.blocks_for_influences('Duke'), ['foreign_aid'])
        self.assertEqual(Influence.blocks_for_influences('Ambassador'), ['steal'])
        self.assertEqual(Influence.blocks_for_influences('Captain'), ['steal'])
        
        self.assertEqual(Influence.blocks_for_influences(['Assassin', 'Duke']), ['foreign_aid'])
        self.assertEqual(Influence.blocks_for_influences(['Contessa', 'Assassin']), ['assassinate'])
        self.assertEqual(Influence.blocks_for_influences(['Duke', 'Captain']), ['foreign_aid', 'steal'])
        self.assertEqual(Influence.blocks_for_influences(['Ambassador', 'Ambassador']), ['steal'])
        self.assertEqual(Influence.blocks_for_influences(['Captain', 'Assassin']), ['steal'])
        
        self.assertEqual(Influence.blocks_for_influences('Assassin Duke'), ['foreign_aid'])
        self.assertEqual(Influence.blocks_for_influences('Assassin Contessa'), ['assassinate'])
        self.assertEqual(Influence.blocks_for_influences('Duke Captain'), ['foreign_aid', 'steal'])
        self.assertEqual(Influence.blocks_for_influences('Ambassador Ambassador'), ['steal'])
        self.assertEqual(Influence.blocks_for_influences('Captain Assassin'), ['steal'])

    def test_actions_for_probable_influences(self):
        p = AI_Persona()
        
        p.left = Assassin()
        p.right = Duke()
        
        self.assertEqual(Influence.actions_for_influences(p), ['assassinate', 'tax'])
        
        p.left = Contessa()
        p.right = Contessa()
        
        self.assertEqual(Influence.actions_for_influences(p), [])
        
    def test_blocks_for_probable_influences(self):
        p = AI_Persona()
        
        p.left = Assassin()
        p.right = Duke()
        
        self.assertEqual(Influence.blocks_for_influences(p), ['foreign_aid'])
        
        p.left = Contessa()
        p.right = Contessa()
        
        self.assertEqual(Influence.blocks_for_influences(p), ['assassinate'])

    def test_deduce(self):
        from heuristics import WEIGHTS
        
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
        from heuristics import WEIGHTS
        
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        
        p.perform('foreign_aid')
        testgame.players[1].didnt_block_as['spectator'].extend(['foreign_aid'])
        
        self.assertIn('Duke', testgame.players[1].improbable_influences)
        self.assertEqual(testgame.players[1].improbable_influences, {
            'Duke': abs(WEIGHTS['didnt_block_selflessly']) * 1 
            })

        ppp = testgame.players[2]
        
        ppp.perform('steal', testgame.players[0])        
        testgame.players[0].didnt_block_as['victim'].extend(['steal'])
        testgame.players[3].didnt_block_as['spectator'].extend(['steal'])
            
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
        from heuristics import WEIGHTS
        
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
        
        self.assertIsNone(pp.will_intervene('foreign_aid', p))
        self.assertIsNone(p.will_intervene('foreign_aid', pp))

        p.left = Duke()
        
        p.rules['honest_intervention']['foreign_aid'] = {
            'performer': lambda q: True
            }
        self.assertEqual(p.will_intervene('foreign_aid', pp), 'Duke')

        p.rules['honest_intervention']['foreign_aid'] = {
            'performer': lambda q: q.coins > 5
            }
        self.assertIsNone(p.will_intervene('foreign_aid', pp))
        
        p.rules['honest_intervention']['foreign_aid'] = {}
        self.assertIsNone(p.will_intervene('foreign_aid', pp))
        
        p.rules['calculated_intervention']['foreign_aid'] = {}
        self.assertIsNone(p.will_intervene('foreign_aid', pp))
        
        p.rules['calculated_intervention']['foreign_aid'] = {
            'performer': lambda q: q.influence_remaining == 2
            }
        self.assertEqual(p.will_intervene('foreign_aid', pp), 'Duke')

        p.left.reveal()
        p.rules['honest_intervention']['foreign_aid'] = {
            'performer': lambda q: True
            }
        p.rules['calculated_intervention']['foreign_aid'] = {}
        self.assertIsNone(p.will_intervene('foreign_aid', pp))
        
        p.rules['honest_intervention']['foreign_aid'] = {}
        p.rules['calculated_intervention']['foreign_aid'] = {}
        
        p.rules['calculated_intervention']['foreign_aid'] = {
            'performer': lambda q: q.influence_remaining == 2
            }
        self.assertEqual(p.will_intervene('foreign_aid', pp), 'Duke')

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

        self.assertIsNone(ppp.will_intervene('steal', p, pp))

        p.coins = 2
        ppp.rules['honest_intervention']['steal'] = {
            'performer': lambda q: True
            }
        self.assertEqual(ppp.will_intervene('steal', p, pp), 'Captain')

        ppp.rules['honest_intervention']['steal'] = {
            'performer': lambda q: False
            }
        self.assertIsNone(ppp.will_intervene('steal', p, pp))

        p.coins = 2
        ppp.rules['calculated_intervention']['steal'] = {
            'performer': lambda q: q.coins + 2 >= 3
            }

        self.assertIn(ppp.will_intervene('steal', p, pp), ['Captain', 'Ambassador'])
            
    def test_wins_duel(self):
        '''this function may be unreliable because it is random which influence is eliminated.
        pp starting vs p has variable winners because of random coup/assassinate flip.
        whomever wins the first wins_duel will be that players conviction from then on,
        which should be hashed on the player + influences'''
        p = AI_Persona()
        p.left = Duke()
        p.right = Assassin()
        
        pp = AI_Persona()
        pp.left = Captain()
        pp.right = Captain()
        
        self.assertTrue(p.wins_duel(pp)) 
        self.assertTrue(pp.wins_duel(p)) #see above note
        
        p = AI_Persona()
        p.left = Duke()
        p.right = Duke()
        
        pp = AI_Persona()
        pp.left = Contessa()
        pp.right = Contessa()
        
        #repeat tests to use saved value   
        for _ in range(100):
            self.assertTrue(p.wins_duel(pp)) 
            self.assertFalse(pp.wins_duel(p))

    def test_plays_numbers(self):
        p = AI_Persona()
        
        self.assertFalse(p.plays_numbers)
        
        p.rules['callout']['plays_numbers'] = False
        self.assertFalse(p.plays_numbers)
        
        p.rules['callout']['plays_numbers'] = True
        self.assertTrue(p.plays_numbers)
        
    def test_judge_player(self):
        from heuristics import WEIGHTS
        testgame = Play_Coup(5)
        p = testgame.players[0]
        
        self.assertEqual(p.judge_player, {})
        
        p.public_information['perform'].extend(['steal', 'steal', 'steal'])
        
        self.assertEqual(p.judge_player, {'Captain': WEIGHTS['performed_action'] * 3})
        
        p.didnt_block_as['victim'].extend(['steal'])
        
        self.assertEqual(p.judge_player, {
            'Captain': WEIGHTS['performed_action'] * 3 - abs(WEIGHTS['didnt_block_selfishly'] * 1), 
            'Ambassador': -abs(WEIGHTS['didnt_block_selfishly'] * 1)
            })
            
    def test_best_guess(self):
        p = AI_Persona()
        p.left = Contessa()
        p.right = Duke()
        
        self.assertEqual(p.best_guess, '')
            
        p.public_information['perform'].extend(['tax'])
        self.assertEqual(p.best_guess, 'Duke')
        
        p.public_information['perform'].extend(['assassinate'])
        self.assertEqual(p.best_guess, 'Assassin Duke')
        
        p.public_information['perform'].extend(['assassinate'])
        self.assertEqual(p.best_guess, 'Assassin Duke')
        
        p.public_information['perform'].extend(['steal'])
        
        matches = 0
        try:
            self.assertEqual(p.best_guess, 'Assassin Duke')
            matches += 1
        except AssertionError:
            self.assertEqual(p.best_guess, 'Assassin Captain')
            matches += 1
        finally:
            self.assertEqual(matches, 1)
            
        pp = AI_Persona()
        pp.left = Contessa()
        pp.right = Duke()
        
        pp.public_information['perform'].extend(['tax', 'tax', 'steal', 'steal', 'assassinate'])
        self.assertEqual(pp.best_guess, 'Captain Duke')
        pp.right.reveal()
        pp.remove_suspicion('Duke')
        
        self.assertEqual(pp.best_guess, 'Captain')
            
    def test_judge_actions(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        
        p.public_information['perform'].extend(['steal', 'steal', 'steal'])
        self.assertIn('steal', p.calculate('judge', 'actions'))
        p.didnt_block_as['victim'].extend(['steal'])
        p.public_information['perform'].extend(['assassinate'])
        
        self.assertIn('assassinate', p.calculate('judge', 'actions')) 
        self.assertNotIn('steal', p.calculate('judge', 'actions'))
    
    def test_judge_blocks(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        
        p.public_information['perform'].extend(['steal', 'steal', 'steal']) 
        self.assertIn('steal', p.calculate('judge', 'blocks'))        
        
    def test_best_probable_actions(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        p.left = Duke()
        p.right = Captain()
        
        self.assertNotIn('assassinate', p.calculate('probable', 'actions'))
        self.assertNotIn('tax', p.calculate('probable', 'actions'))
        self.assertNotIn('steal', p.calculate('probable', 'actions'))
        
        p.public_information['perform'].extend(['steal', 'steal', 'steal'])
        
        self.assertNotIn('assassinate', p.calculate('probable', 'actions'))
        self.assertNotIn('tax', p.calculate('probable', 'actions'))
        self.assertIn('steal', p.calculate('probable', 'actions'))
        
        p.public_information['perform'].extend(['tax','tax','tax'])
        
        self.assertNotIn('assassinate', p.calculate('probable', 'actions'))
        self.assertIn('tax', p.calculate('probable', 'actions'))
        self.assertIn('steal', p.calculate('probable', 'actions'))
        
        p.public_information['perform'].extend(['assassinate'])
        
        self.assertNotIn('assassinate', p.calculate('probable', 'actions'))
        self.assertIn('tax', p.calculate('probable', 'actions'))
        self.assertIn('steal', p.calculate('probable', 'actions'))
        
        p.public_information['perform'].extend(['tax', 'assassinate','assassinate','assassinate'])

        self.assertIn('assassinate', p.calculate('probable', 'actions'))
        self.assertIn('tax', p.calculate('probable', 'actions'))
        self.assertNotIn('steal', p.calculate('probable', 'actions'))
    
    def test_calculate(self):
        p = AI_Persona()
        
        p.left = Contessa()
        p.right = Assassin()
        
        self.assertEqual(p.calculate('probable', 'blocks'), [])
        self.assertEqual(p.calculate('improbable', 'blocks'), [])
        self.assertEqual(p.calculate('judge', 'blocks'), [])
        
        self.assertEqual(p.calculate('probable', 'actions'), [])
        self.assertEqual(p.calculate('improbable', 'actions'), [])
        self.assertEqual(p.calculate('judge', 'actions'), [])
        
        p.public_information['perform'].extend(['tax'])
        
        self.assertEqual(p.calculate('probable', 'blocks'), ['foreign_aid'])
        self.assertEqual(p.calculate('improbable', 'blocks'), [])
        self.assertEqual(p.calculate('judge', 'blocks'), ['foreign_aid'])
        
        self.assertEqual(p.calculate('probable', 'actions'), ['tax'])
        self.assertEqual(p.calculate('improbable', 'actions'), [])
        self.assertEqual(p.calculate('judge', 'actions'), ['tax'])
        
        p.public_information['perform'].extend(['steal'])
        
        self.assertEqual(p.calculate('probable', 'blocks'), ['foreign_aid', 'steal'])
        self.assertEqual(p.calculate('improbable', 'blocks'), [])
        self.assertEqual(p.calculate('judge', 'blocks'), ['foreign_aid', 'steal'])
        
        self.assertEqual(p.calculate('probable', 'actions'), ['steal', 'tax'])
        self.assertEqual(p.calculate('improbable', 'actions'), [])
        self.assertEqual(p.calculate('judge', 'actions'), ['steal', 'tax'])
        
        p.didnt_block_as['spectator'].extend(['foreign_aid', 'foreign_aid', 'foreign_aid'])
        
        self.assertEqual(p.calculate('probable', 'blocks'), ['foreign_aid', 'steal'])
        self.assertEqual(p.calculate('improbable', 'blocks'), ['foreign_aid'])
        self.assertEqual(p.calculate('judge', 'blocks'), ['steal'])
        
        self.assertEqual(p.calculate('probable', 'actions'), ['steal', 'tax'])
        self.assertEqual(p.calculate('improbable', 'actions'), ['tax'])
        self.assertEqual(p.calculate('judge', 'actions'), ['steal'])
        
        p.public_information['perform'].extend(['assassinate', 'assassinate', 'steal'])
        
        self.assertEqual(p.calculate('probable', 'blocks'), ['steal'])
        self.assertEqual(p.calculate('improbable', 'blocks'), ['foreign_aid'])
        self.assertEqual(p.calculate('judge', 'blocks'), ['steal'])
        
        self.assertEqual(p.calculate('probable', 'actions'), ['assassinate', 'steal'])
        self.assertEqual(p.calculate('improbable', 'actions'), ['tax'])
        self.assertEqual(p.calculate('judge', 'actions'), ['assassinate', 'steal'])
        
        p.public_information['perform'].extend(['income', 'income', 'income'])
        p.public_information['spectator'].extend(['assassinate'])
        p.public_information['perform'].extend(['assassinate'])
        
        self.assertEqual(p.calculate('probable', 'blocks'), ['assassinate'])
        self.assertEqual(p.calculate('improbable', 'blocks'), ['foreign_aid'])
        self.assertEqual(p.calculate('judge', 'blocks'), ['assassinate'])
        
        self.assertEqual(p.calculate('probable', 'actions'), ['assassinate'])
        self.assertEqual(p.calculate('improbable', 'actions'), ['tax'])
        self.assertEqual(p.calculate('judge', 'actions'), ['assassinate'])

    def test_probable_blocks(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        
        p.public_information['perform'].extend(['tax'])
        self.assertIn('foreign_aid', p.calculate('probable', 'blocks'))
        
        p.perform('steal', testgame.players[1])
        self.assertIn('steal', p.calculate('probable', 'blocks'))
        
    def test_improbable_blocks(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        
        p.didnt_block_as['spectator'].extend(['steal'])
        self.assertIn('steal', p.calculate('improbable', 'blocks')) 
        self.assertNotIn('assassinate', p.calculate('improbable', 'blocks'))
        self.assertNotIn('foreign_aid', p.calculate('improbable', 'blocks'))
        
        p.perform('income')
        self.assertIn('steal', p.calculate('improbable', 'blocks'))
        self.assertNotIn('assassinate', p.calculate('improbable', 'blocks'))
        self.assertIn('foreign_aid', p.calculate('improbable', 'blocks'))
        
        p.didnt_block_as['spectator'].extend(['assassinate'])
        p.didnt_block_as['spectator'].extend(['assassinate'])
        
        self.assertNotIn('steal', p.calculate('improbable', 'blocks'))
        self.assertIn('assassinate', p.calculate('improbable', 'blocks'))
        self.assertIn('foreign_aid', p.calculate('improbable', 'blocks'))   

    def test_improbable_actions(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        
        p.didnt_block_as['spectator'].extend(['steal'])
        self.assertIn('steal', p.calculate('improbable', 'actions'))

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
        self.assertIsNone(ppp.will_intervene('steal', p, pp))

        ppp.rules['calculated_intervention']['steal'] = {
            'victim': lambda q: q.coins
            }
        self.assertIsNone(ppp.will_intervene('steal', p, pp))

        pp.coins = 1
        self.assertIsNotNone(ppp.will_intervene('steal', p, pp))

        pp.coins = 2
        self.assertIsNotNone(ppp.will_intervene('steal', p, pp))

        ppp.rules['calculated_intervention']['steal'] = {
            'victim': lambda q: q.coins >= 5
            }

        self.assertFalse(ppp.will_intervene('steal', p, pp))
        pp.coins = 5
        self.assertIsNotNone(ppp.will_intervene('steal', p, pp))

    def test_will_callout(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        pp = testgame.players[1]
        
        self.assertFalse(pp.will_callout('tax', p)) #no rule
        
        pp.rules['callout'] = {
            'threshold': -3,
            'min_actions': 3,
            'min_inactions': 3
            }
        
        self.assertFalse(pp.will_callout('tax', p))

        p.perform('tax')
        self.assertFalse(pp.will_callout('tax', p))

        p.perform('tax')
        self.assertFalse(pp.will_callout('tax', p))
        
        for _ in range(6):
            p.didnt_block_as['spectator'].extend(['foreign_aid'])
        self.assertFalse(pp.will_callout('tax', p))
        
        p.perform('tax')
        self.assertTrue(pp.will_callout('tax', p))
        
        pp.rules['callout'] = {
            'threshold': -30,
            'min_actions': 3,
            'min_inactions': 3
            }
            
        self.assertFalse(pp.will_callout('tax', p))
        
        pp.rules['callout'] = {
            'threshold': -3,
            'min_actions': 3,
            'min_inactions': 3
            }
        
        self.assertTrue(pp.will_callout('tax', p))
        
        pp.rules['callout'] = {
            'threshold': -3,
            'min_actions': 12,
            'min_inactions': 12
            }
        
        self.assertFalse(pp.will_callout('tax', p))

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
    
    def test_one_on_one_strategy(self):
        p = AI_Persona()
        p.left = Contessa()
        p.right = Duke()
        
        p.coins = 2
        self.assertEqual(p.one_on_one_strategy('', False), [])
        self.assertEqual(p.one_on_one_strategy('', True), [])
        
        p.coins = 0
        self.assertEqual(p.one_on_one_strategy('Assassin Contessa', False), ['steal', 'tax', 'foreign_aid', 'income'])
        self.assertEqual(p.one_on_one_strategy('Assassin Contessa', True), ['tax', 'foreign_aid', 'income'])
        
        p.coins = 7
        self.assertEqual(p.one_on_one_strategy('Assassin Contessa', True), ['coup'])
        self.assertEqual(p.one_on_one_strategy('Assassin Contessa', False), ['coup'])
        
        p.coins = 2
        self.assertNotIn(p.one_on_one_strategy('Duke Duke', True), ['coup'])
        self.assertNotIn(p.one_on_one_strategy('Duke Duke', True), ['assassinate'])
        
        p.coins = 6
        self.assertNotIn(p.one_on_one_strategy('Duke Duke', True), ['coup'])
        self.assertNotIn(p.one_on_one_strategy('Duke Duke', True), ['assassinate'])
        self.assertNotIn(p.one_on_one_strategy('Duke Duke', False), ['assassinate'])
    
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
                                                                      
    def test_question_influence(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        pp = testgame.players[1]
        
        p.left = Duke()
        p.right = Duke()
        pp.left = Assassin()
        pp.right = Duke()
        
        try:
            raise QuestionInfluence(p, pp, 'Assassin', testgame.court_deck, 'assassinate')
        except QuestionInfluence as e:
            self.assertEqual(e.message, "{0} doubts {1} influences a {2}: former loses one influence!".format(e.doubter,
                                                                                                              e.alleged_bluffer,
                                                                                                              'Assassin'))
            self.assertEqual(e.action, 'assassinate')
            self.assertFalse(e.doubter_is_correct)
            self.assertEqual(p.influence_remaining, 1)
            self.assertEqual(pp.influence_remaining, 2)
            
        try:
            raise QuestionInfluence(pp, p, 'Contessa', testgame.court_deck, 'block_assassinate')
        except QuestionInfluence as e:
            self.assertEqual(e.message, "{0} doubts {1} influences a {2}: latter loses one influence!".format(e.doubter,
                                                                                                              e.alleged_bluffer,
                                                                                                              'Contessa'))
            self.assertEqual(e.action, 'block_assassinate')
            self.assertTrue(e.doubter_is_correct)
            self.assertEqual(p.influence_remaining, 0)
            self.assertEqual(pp.influence_remaining, 2)
    
    def test_exchange_revealed_influence(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        
        self.assertEqual(len(testgame.court_deck), 5)
        self.assertFalse(p.left.revealed)
        p.left.reveal()
        self.assertTrue(p.left.revealed)
        p.restore('left', testgame.court_deck)
        self.assertFalse(p.left.revealed)
        self.assertEqual(len(testgame.court_deck), 5)

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

