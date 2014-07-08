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
        
        self.assertEqual(testgame.filter_out_players([p,pp]), {
            testgame.players[2],    
            testgame.players[3],
            testgame.players[4],        
            })
            
        testgame.players[3].left.reveal()
        testgame.players[3].right.reveal()
            
        self.assertEqual(testgame.filter_out_players([testgame.players[0], testgame.players[1]]), {
            testgame.players[2],    
            testgame.players[4],        
            })
            
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
    
    def test_playerstate(self):
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
        
        self.assertEqual(testgame.playerstate_binary, \
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
        
        self.assertEqual(testgame.playerstate_binary, \
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

    def test_ai_persona_replace_player(self):
        testgame = Play_Coup(5)

        p = testgame.players[0]
        a = AI_Persona.clone(p)
        
        self.assertEqual(a.coins, p.coins)
        self.assertIs(a.left, p.left)
        self.assertIs(a.right, p.right)

        testgame.players[0] = a

        self.assertIs(a, testgame.players[0])
        self.assertIsInstance(a, AI_Persona)

    def test_ai_persona_select_opponent(self):
        testgame = Play_Coup(5)

        p = testgame.players[0]
        
        for i in range(50):
            self.assertIsNot(p, p.select_opponent(testgame.players))

        pppp = testgame.players[4]
        pppp.left.reveal()
        pppp.right.reveal()
        
        for i in range(50):
            self.assertIsNot(p, p.select_opponent(testgame.players))
            self.assertIsNot(pppp, p.select_opponent(testgame.players))

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
     
    def test_actions_for_given_influences(self):
        self.assertEqual(Player.actions_for_influence('Assassin'), ['assassinate'])
        self.assertEqual(Player.actions_for_influence('Contessa'), [])
        self.assertEqual(Player.actions_for_influence('Duke'), ['tax'])
        self.assertEqual(Player.actions_for_influence('Ambassador'), ['exchange'])
        self.assertEqual(Player.actions_for_influence('Captain'), ['steal'])
        
        self.assertEqual(Player.actions_for_influence(['Assassin', 'Duke']), ['assassinate', 'tax'])
        self.assertEqual(Player.actions_for_influence(['Contessa', 'Assassin']), ['assassinate'])
        self.assertEqual(Player.actions_for_influence(['Duke', 'Captain']), ['steal', 'tax'])
        self.assertEqual(Player.actions_for_influence(['Ambassador', 'Ambassador']), ['exchange'])
        self.assertEqual(Player.actions_for_influence(['Captain', 'Assassin']), ['assassinate', 'steal'])
        
        self.assertEqual(Player.actions_for_influence('Assassin Duke'), ['assassinate', 'tax'])
        self.assertEqual(Player.actions_for_influence('Assassin Contessa'), ['assassinate'])
        self.assertEqual(Player.actions_for_influence('Duke Captain'), ['steal', 'tax'])
        self.assertEqual(Player.actions_for_influence('Ambassador Ambassador'), ['exchange'])
        self.assertEqual(Player.actions_for_influence('Captain Assassin'), ['assassinate', 'steal'])

    def test_actions_for_probable_influences(self):
        p = AI_Persona()
        
        p.left = Assassin()
        p.right = Duke()
        
        self.assertEqual(Player.actions_for_influence(p), ['assassinate', 'tax'])
        
        p.left = Contessa()
        p.right = Contessa()
        
        self.assertEqual(Player.actions_for_influence(p), [])

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
        
        self.assertFalse(pp.will_intervene('foreign_aid', p))
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
        
        p.rules['honest_intervention']['foreign_aid'] = {}
        self.assertFalse(p.will_intervene('foreign_aid', pp))
        
        p.rules['calculated_intervention']['foreign_aid'] = {}
        self.assertFalse(p.will_intervene('foreign_aid', pp))
        
        p.rules['calculated_intervention']['foreign_aid'] = {
            'performer': lambda q: q.influence_remaining == 2
            }
        self.assertTrue(p.will_intervene('foreign_aid', pp))

        p.left.reveal()
        p.rules['honest_intervention']['foreign_aid'] = {
            'performer': lambda q: True
            }
        p.rules['calculated_intervention']['foreign_aid'] = {}
        self.assertFalse(p.will_intervene('foreign_aid', pp))
        
        p.rules['honest_intervention']['foreign_aid'] = {}
        p.rules['calculated_intervention']['foreign_aid'] = {}
        
        p.rules['calculated_intervention']['foreign_aid'] = {
            'performer': lambda q: q.influence_remaining == 2
            }
        self.assertTrue(p.will_intervene('foreign_aid', pp))

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
        
    def test_judge_player(self):
        from heuristics import WEIGHTS
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        
        p.public_information['perform'].extend(['steal', 'steal', 'steal'])
        
        self.assertEqual(p.judge_player, {'Captain': WEIGHTS['performed_action'] * 3})
        
        p.not_acting_like['victim'].extend(['steal'])
        
        self.assertEqual(p.judge_player, {
            'Captain': WEIGHTS['performed_action'] * 3 - abs(WEIGHTS['didnt_block_selfishly'] * 1), 
            'Ambassador': -abs(WEIGHTS['didnt_block_selfishly'] * 1)
            })
            
    def test_judge_actions(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        
        p.public_information['perform'].extend(['steal', 'steal', 'steal'])
        self.assertIn('steal', p.judge_actions)
        p.not_acting_like['victim'].extend(['steal'])
        p.public_information['perform'].extend(['assassinate'])
        
        self.assertIn('assassinate', p.judge_actions)
        self.assertNotIn('steal', p.judge_actions)
    
    def test_judge_blocks(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        
        p.public_information['perform'].extend(['steal', 'steal', 'steal']) 
        self.assertIn('steal', p.judge_blocks)        
        
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

    def test_improbable_actions(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        
        p.not_acting_like['spectator'].extend(['steal'])
        self.assertIn('steal', p.improbable_actions)

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
        
        for _ in range(5):
            p.not_acting_like['spectator'].extend(['foreign_aid'])

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
                                                                      
    def test_question_influence(self):
        testgame = Play_Coup(5)
        
        p = testgame.players[0]
        pp = testgame.players[1]
        
        p.left = Duke()
        p.right = Duke()
        pp.left = Assassin()
        pp.right = Duke()
        
        try:
            raise QuestionInfluence('assassinate', p, pp)
        except QuestionInfluence as e:
            self.assertEqual(e.message, "{0} doubts {1} can {2}: performer loses one influence!".format(pp,
                                                                                                        p,
                                                                                                        'assassinate'))
            self.assertFalse(e.performer_is_honest)
            self.assertEqual(p.influence_remaining, 1)
            self.assertEqual(pp.influence_remaining, 2)
            
        try:
            raise QuestionInfluence('assassinate', pp, p)
        except QuestionInfluence as e:
            self.assertEqual(e.message, "{0} doubts {1} can {2}: doubter loses one influence!".format(p,
                                                                                                      pp,
                                                                                                      'assassinate'))
            self.assertTrue(e.performer_is_honest)
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

