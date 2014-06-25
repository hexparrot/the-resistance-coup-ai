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

    def test_ai_persona(self):
        a = AI_Persona()
        self.assertIsInstance(a, Player)

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
        self.assertIsNot(a.select_opponent(z, [1,2], [0,12]), testgame.players[0])

        self.assertIsNone(a.select_opponent(z, influence=[1]))
        self.assertIsNone(a.select_opponent(z, coin_range=[3,12]))

        self.assertIsInstance(a.select_opponent(z), Player)

        testgame.players[1].coins = 3
        testgame.players[2].coins = 5
        testgame.players[3].coins = 12
        self.assertIs(a.select_opponent(z, coin_range=[3,3]), testgame.players[1])
        self.assertIs(a.select_opponent(z, coin_range=[6,12]), testgame.players[3])

        testgame.players[4].left.reveal()
        self.assertIs(a.select_opponent(z, influence=[1]), testgame.players[4])        

    def test_ai_persona_will_intervene(self):
        a = AI_Persona()
        a.left = Contessa()
        a.right = Captain()

        
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
                    break
                except (IllegalTarget, IllegalAction):
                    pass

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
                    break
                except (IllegalTarget, IllegalAction):
                    pass

    def test_gameplay_random_actions_random_targets_block_all_no_doubts(self):
        """
        AI PROFILE:
        
        Action          Used        Targets     Blocked     
        income          yes
        foreign_aid     yes                     any available duke
        coup            yes
        steal           yes         random      any available captain/ambassador
        tax             yes
        assassinate     yes         random      any available contessa
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
                        for savior in range(PLAYERS):
                            if savior != i and action in testgame.players[savior].valid_blocks:
                                raise BlockedAction("{0} ({1}) blocks {2}'s ({3}) {4}".format(testgame.players[savior].alpha,
                                                                                              savior,
                                                                                              acting_player.alpha,
                                                                                              i,
                                                                                              action))
                        else:
                            random_player = testgame.random_targetable_player(acting_player)
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
                    break
                except (IllegalTarget, IllegalAction):
                    pass
                except BlockedAction as e:
                    break

    def test_gameplay_random_actions_calculated_targets_block_all_no_doubts(self):
        """
        AI PROFILE:
        
        Action          Used        Targets     Blocked     
        income          yes
        foreign_aid     yes                     any available duke
        coup            yes
        steal           yes         richest     any available captain/ambassador
        tax             yes
        assassinate     yes         weakest     any available contessa
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
                        for savior in range(PLAYERS):
                            if savior != i and action in testgame.players[savior].valid_blocks:
                                raise BlockedAction("{0} ({1}) blocks {2}'s ({3}) {4}".format(testgame.players[savior].alpha,
                                                                                              savior,
                                                                                              acting_player.alpha,
                                                                                              i,
                                                                                              action))
                        else:
                            if action == 'steal':
                                random_player = testgame.random_richest_player(acting_player)
                                testgame.players[i].perform(action, random_player)
                            elif action in Play_Coup.ACTIONS['targets_influence']:
                                random_player = testgame.random_targetable_player(acting_player, [1]) or \
                                                testgame.random_richest_player(acting_player)
                                position, random_target = random_player.random_remaining_influence
                                testgame.players[i].perform(action, random_target)
                            elif action in Play_Coup.ACTIONS['targets_player']:
                                random_player = testgame.random_richest_player(acting_player)
                                testgame.players[i].perform(action, random_player)
                    else:
                        if action in Play_Coup.ACTIONS['targets_influence']:
                            random_player = testgame.random_targetable_player(acting_player, [1]) or \
                                            testgame.random_richest_player(acting_player)
                            position, random_target = random_player.random_remaining_influence
                            testgame.players[i].perform(action, random_target)
                        elif action == 'exchange':
                            testgame.players[i].perform(action, testgame.court_deck)
                        else:
                            testgame.players[i].perform(action)
                    break
                except (IllegalTarget, IllegalAction):
                    pass
                except BlockedAction as e:
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
                            raise BlockedAction("{0} blocks {1}'s ({2}) {3}".format(random_player.alpha,
                                                                                    acting_player.alpha,
                                                                                    i,
                                                                                    action))
                        else:
                            testgame.players[i].perform(action, random_player)
                    elif action == 'assassinate':
                        random_player = testgame.random_targetable_player(acting_player, [1])or \
                                        testgame.random_richest_player(acting_player)
                        if 'assassinate' in random_player.valid_blocks:
                            raise BlockedAction("{0} blocks {1}'s ({2}) {3}".format(random_player.alpha,
                                                                                    acting_player.alpha,
                                                                                    i,
                                                                                    action))
                        else:
                            position, random_target = random_player.random_remaining_influence
                            testgame.players[i].perform(action, random_target)
                    elif action == 'foreign_aid':
                        for savior in range(PLAYERS):
                            if savior != i and action in testgame.players[savior].valid_blocks:
                                raise BlockedAction("{0} ({1}) blocks {2}'s ({3}) {4}".format(testgame.players[savior].alpha,
                                                                                              savior,
                                                                                              acting_player.alpha,
                                                                                              i,
                                                                                              action))
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
                    break
                except (IllegalTarget, IllegalAction):
                    pass
                except BlockedAction as e:
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

