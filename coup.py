"""
Python scripts to simulate the game "The Resistance: Coup designed by Rikki Tahta
The purpose of this project is to model human personalities and predict/score
behaviors and bluffs in order to win the game.

"""

__author__ = "William Dizon"
__license__ = "GNU GPL v3.0"
__version__ = "0.0.1"
__email__ = "wdchromium@gmail.com"

class Play_Coup(object):
    ACTIONS = {
        'all': ['income', 'foreign_aid', 'coup', 'steal', 'tax', 'assassinate', 'exchange'],
        'blockable': ['assassinate', 'steal', 'foreign_aid'],
        'targets_influence': ['coup', 'assassinate'],
        'targets_player': ['steal'],
        'bluffable': ['steal', 'tax', 'assassinate', 'exchange'],
        }
    
    def __init__(self, players):
        from random import shuffle
        
        self.players = {i:AI_Persona() for i in range(players)}
        self.court_deck = [Contessa() for _ in range(3)] + \
                          [Ambassador() for _ in range(3)] + \
                          [Duke() for _ in range(3)] + \
                          [Assassin() for _ in range(3)] + \
                          [Captain() for _ in range(3)]
        
        shuffle(self.court_deck)

        for p in range(players):
            self.players[p].left = self.court_deck.pop()
            self.players[p].right = self.court_deck.pop()

    def random_targetable_player(self,
                                 safe_player,
                                 influence_amount=[1,2]):
        from random import choice
        try:
            return choice([self.players[i] for i,v in self.players.items() \
                           if v.influence_remaining in influence_amount \
                           and v is not safe_player])
        except IndexError:
            return None

    def random_targetable_player_by_coins(self,
                                          safe_player,
                                          coins=[2,12]):
        from random import choice
        try:
            return choice([self.players[i] for i,v in self.players.items() \
                           if v.influence_remaining and \
                           coins[0] <= v.coins <= coins[1] and \
                           v is not safe_player])
        except IndexError:
            return None

    def random_richest_player(self,
                              safe_player):
        return sorted([v for i,v in self.players.items() \
                       if v is not safe_player and \
                       v.influence_remaining], \
                      key=lambda p: p.coins, reverse=True)[0]
        

class Player(object):
    PERFORMED_ACTION = {
        'steal': 'Captain',
        'tax': 'Duke',
        'assassinate': 'Assassin',
        }
    BLOCKED_ACTION = {
        'foreign_aid': 'Duke',
        'steal': 'Ambassador/Captain',
        'assassinate': 'Contessa'
        }
    
    def __init__(self):
        self.coins = 2
        self.left = None
        self.right = None
        self.public_information = {
            'perform': [],
            'victim': [],
            'spectator': []
            }

    def __str__(self):
        return '{0} {1}'.format(self.left, self.right)

    def perform(self, action, player_target=None):
        from itertools import chain

        if player_target and \
           (player_target is self.left or \
           player_target is self.right):
            raise IllegalTarget("you may not target yourself")
        
        for inf in chain([Influence,], Influence.__subclasses__()):
            if hasattr(inf, action):
                if player_target is None:
                    getattr(inf, action)(self)
                else:
                    getattr(inf, action)(self, player_target)
                self.public_information['perform'].append(action)
                break
        else:
            raise IllegalAction("no action %s" % action)

    def influences(self, influence):
        return (not self.left.revealed and str(self.left) == influence) or \
               (not self.right.revealed and str(self.right) == influence)

    def remove_suspicion(self, influence):
        for k,v in self.PERFORMED_ACTION.items():
            if v == influence:
                self.public_information['perform'] = [a for a in self.public_information['perform'] if a != k]
                break
        for k,v in self.BLOCKED_ACTION.items():
            if v == influence:
                self.public_information['victim'] = [a for a in self.public_information['perform'] if a != k]
                self.public_information['spectator'] = [a for a in self.public_information['perform'] if a != k]
                break

    @property
    def best_guesses(self):
        from collections import Counter

        PERFORMED_WEIGHT = 1
        VICTIM_SAVE_WEIGHT = 1
        SPECTATOR_SAVE_WEIGHT = 2
        
        performed = Counter(self.PERFORMED_ACTION[i] for i in self.public_information['perform'] if self.PERFORMED_ACTION.get(i))
        victim = Counter(self.BLOCKED_ACTION[i] for i in self.public_information['victim'] if self.BLOCKED_ACTION.get(i))
        spectator = Counter(self.BLOCKED_ACTION[i] for i in self.public_information['spectator'] if self.BLOCKED_ACTION.get(i))

        result = Counter()
        for _ in range(PERFORMED_WEIGHT):
            result.update(performed)

        for _ in range(VICTIM_SAVE_WEIGHT):
            result.update(victim)

        for _ in range(SPECTATOR_SAVE_WEIGHT):
            result.update(spectator)

        return [inf for inf, freq in result.most_common(2)][0:2]

    @property
    def valid_actions(self):
        actions = set()
        if not self.left.revealed:
            actions.update(self.left.ACTIONS)
        if not self.right.revealed:
            actions.update(self.right.ACTIONS)
        return list(actions)

    @property
    def valid_blocks(self):
        blocks = set()
        if not self.left.revealed:
            blocks.update(self.left.BLOCKS)
        if not self.right.revealed:
            blocks.update(self.right.BLOCKS)
        return list(blocks)

    @property
    def alpha(self):
        return ' '.join(sorted([str(self.left), str(self.right)]))

    @property
    def status(self):
        return ' '.join([str(i) if not i.revealed else '<%s>' % str(i) for i in (self.left, self.right) ])

    @property
    def influence_remaining(self):
        return sum(1 for i in (self.left, self.right) if not i.revealed)

class AI_Persona(Player):        
    def __init__(self, personality='passive'):
        Player.__init__(self)

        from personalities import PERSONALITIES
        from copy import deepcopy

        self.personality = personality
        self.rules = deepcopy(PERSONALITIES[personality])
        
    def select_opponent(self, all_players):
        from random import choice
        return choice([v for i,v in all_players.items() if v is not self])

    def naive_priority(self):
        if self.coins >= 10:
            return 'coup'
        if 'assassinate' in self.valid_actions:
            if self.coins < 3:
                return 'income'
            elif self.coins > 4:
                return 'coin'
            elif self.coins >= 7:
                return 'coup'
            return 'assassinate'
        elif 'tax' in self.valid_actions:
            if self.coins < 7:
                return 'tax'
            else:
                return 'coup'
        elif self.influences('Ambassador'):
            return 'switch'
        elif 'steal' in self.valid_actions:
            if self.coins < 7:
                return 'coin'
            else:
                return 'coup'
        else:
            if self.coins < 7:
                return 'coin'
            else:
                return 'coup'

    def random_naive_priority(self):
        from random import choice

        action = self.naive_priority()

        if action == 'switch':
            return choice(['exchange'] + ['foreign_aid'] * 3 + ['income'])
        elif action == 'coin':
            if 'steal' in self.valid_actions:
                return choice(['steal'] * 3 + ['foreign_aid'] + ['income'])
            return choice(['steal'] + ['foreign_aid'] * 3 + ['income'])
        elif action == 'assassinate':
            return choice(['assassinate'] * 5 + ['foreign_aid'] + ['income'])
        else:
            return action        

    def will_intervene(self, action, performer, victim=None):
        try:
            if action in self.valid_blocks:
                participants = self.rules['honest_intervention'][action]
                for p, cond in participants.items():
                    if cond and not cond(locals()[p]):
                        break
                else:
                    return True
        except KeyError:
            pass

        try:
            participants = self.rules['calculated_intervention'][action]
            for p, cond in participants.items():
                if cond and not cond(locals()[p]):
                    break
            else:
                return True
        except KeyError as e:
            pass

        return False

    @property
    def random_remaining_influence(self):
        if self.influence_remaining == 2:
            import random
            choice = random.choice(['left', 'right'])
            return (choice, getattr(self, choice))
        elif self.influence_remaining == 1:
            if self.left.revealed:
                return ('right', self.right)
            return ('left', self.left)
        else:
            raise IllegalTarget("player already has no remaining influence")    

    @staticmethod
    def clone(player):
        n = AI_Persona()
        n.coins = player.coins
        n.left = player.left
        n.right = player.right
        return n 

class Influence(object):
    def __init__(self):
        self.revealed = False

    def __str__(self):
        return str(self.__class__.__name__)

    def reveal(self):
        self.revealed = True

    @staticmethod
    def income(active_player):
        active_player.coins += 1

    @staticmethod
    def foreign_aid(active_player):
        active_player.coins += 2

    @staticmethod
    def coup(active_player, inf_target):
        if active_player.coins >= 7:
            active_player.coins -= 7
            inf_target.reveal()
        else:
            raise IllegalAction("insufficient currency to coup")

class Captain(Influence):
    ACTIONS = ['steal']
    BLOCKS = ['steal']
    
    @staticmethod
    def steal(active_player, player_target):
        if player_target.coins >= 2:
            player_target.coins -= 2
            active_player.coins += 2
        else:
            available_coins = player_target.coins
            player_target.coins -= available_coins
            active_player.coins += available_coins
        
class Duke(Influence):
    ACTIONS = ['tax']
    BLOCKS = ['foreign_aid']
    
    @staticmethod
    def tax(active_player):
        active_player.coins += 3

class Assassin(Influence):
    ACTIONS = ['assassinate']
    BLOCKS = []
    
    @staticmethod
    def assassinate(active_player, inf_target):
        if active_player.coins >= 3:
            if not inf_target.revealed:
                active_player.coins -= 3
                inf_target.reveal()
            else:
                raise IllegalTarget("influence target already eliminated")
        else:
            raise IllegalAction("insufficient currency to assassinate")

class Ambassador(Influence):
    ACTIONS = ['exchange']
    BLOCKS = ['steal']
    
    @staticmethod
    def exchange(self, court_deck):
        from random import randint, shuffle

        available_influence = []
        available_influence.append(court_deck.pop())
        available_influence.append(court_deck.pop())

        if not self.left.revealed:
            available_influence.append(self.left)
        if not self.right.revealed:
            available_influence.append(self.right)

        if not self.left.revealed:
            self.left = available_influence.pop(randint(0, len(available_influence)-1))
        if not self.right.revealed:
            self.right = available_influence.pop(randint(0, len(available_influence)-1))

        court_deck.extend(available_influence)

class Contessa(Influence):
    ACTIONS = []
    BLOCKS = ['assassinate']

class IllegalAction(Exception):
    pass

class IllegalTarget(Exception):
    pass

class RethinkAction(Exception):
    def __init__(self, action, performer, victim):
        self.action = action
        self.performer = performer
        self.victim = victim

        self.message = '{0} rethinks {1} on {2}'.format(performer, action, victim)

class BlockedAction(Exception):
    def __init__(self, action, performer, victim, spectator):
        self.action = action
        self.performer = performer
        self.victim = victim
        self.spectator = spectator

        if self.victim:
            if not spectator:
                self.message = "{0} blocks {1}'s {2}".format(self.victim,
                                                             self.performer,
                                                             self.action)
                self.victim.public_information['victim'].append(action)
            else:
                self.message = '{0} performs {1} on {2}--blocked by {3}'.format(performer,
                                                                                action,
                                                                                victim,
                                                                                spectator)
                self.spectator.public_information['spectator'].append(action)
        elif not self.victim:
            self.message = "{0} blocks {1}'s {2}".format(spectator,
                                                         performer,
                                                         action)
            self.spectator.public_information['spectator'].append(action)


        
