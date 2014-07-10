"""
Python scripts to simulate the game "The Resistance: Coup designed by Rikki Tahta
The purpose of this project is to model human personalities and predict/score
behaviors and bluffs in order to win the game.

"""

__author__ = "William Dizon"
__license__ = "GNU GPL v3.0"
__version__ = "0.0.1"
__email__ = "wdchromium@gmail.com"

from heuristics import *

class Play_Coup(object):
    ACTIONS = {
        'all': ['income', 'foreign_aid', 'coup', 'steal', 'tax', 'assassinate', 'exchange'],
        'free': ['income', 'foreign_aid', 'coup'],
        'blockable': ['assassinate', 'steal', 'foreign_aid'],
        'targets_influence': ['coup', 'assassinate'],
        'targets_player': ['steal'],
        'bluffable': ['steal', 'tax', 'assassinate', 'exchange'],
        }
    
    def __init__(self, player_count, personalities=[]):
        from random import shuffle, choice
        
        self.players = []
        
        for i in range(player_count):
            if personalities:
                self.players.append(AI_Persona(choice(personalities)))
            else:
                self.players.append(AI_Persona())

        self.court_deck = [Contessa() for _ in range(3)] + \
                          [Ambassador() for _ in range(3)] + \
                          [Duke() for _ in range(3)] + \
                          [Assassin() for _ in range(3)] + \
                          [Captain() for _ in range(3)]
        
        shuffle(self.court_deck)

        for p in range(player_count):
            self.players[p].left = self.court_deck.pop()
            self.players[p].right = self.court_deck.pop()
            
    def __len__(self):
        return sum(1 for p in self.players if p.influence_remaining)
            
    def filter_out_players(self, list_of_players):
        from random import shuffle
        hits = [p for p in self.players if p not in list_of_players and p.influence_remaining]
        shuffle(hits)
        return hits
    
    @property
    def playerstate_binary(self):
        from itertools import chain
        return tuple(chain(*[p.influence_binary for p in self.players]))

class Player(object):
    def __init__(self):
        self.coins = 2
        self.left = None
        self.right = None
        self.public_information = { #increase likelihood
            'perform': [], #player did this action
            'victim': [], #player blocked somebody doing this to him
            'spectator': [] #player blocked action when not involved in action
            }
        self.didnt_block_as = { #decrease likelihood
            'victim': [], #player didnt block even while targetted
            'spectator': [] #didnt block an uninvolved action
            }

    def __str__(self):
        return '{0} {1}'.format(self.left, self.right)
        
    def __contains__(self, inf):
        return inf in [str(self.left), str(self.right)]

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
        for k,v in IMPLIED_INFORMATION['perform'].items():
            if influence in v:
                self.public_information['perform'] = [a for a in self.public_information['perform'] if a != k]
                break
        for k,v in IMPLIED_INFORMATION['block'].items():
            if influence in v:
                self.public_information['victim'] = [a for a in self.public_information['victim'] if a != k]
                self.public_information['spectator'] = [a for a in self.public_information['spectator'] if a != k]
                break
            
    def restore(self, position, court_deck):
        from random import shuffle

        card = getattr(self, position)
        card.revealed = False
        self.remove_suspicion(card)
        
        court_deck.append(card)

        shuffle(court_deck)
        setattr(self, position, court_deck.pop())

    @property
    def judge_player(self):
        return {k:self.probable_influences.get(k, 0) - self.improbable_influences.get(k, 0) for k in set(self.probable_influences).union(set(self.improbable_influences))}
    
    @property
    def best_guess(self):
        infs = sorted(self.judge_player.items(), reverse=True, key=lambda i: i[1])
        return ' '.join(sorted([i for i,v in infs if v > 0][0:self.influence_remaining]))
    
    @property
    def probable_influences(self):
        from collections import Counter
        from itertools import chain
        
        performed = Counter(chain(*[IMPLIED_INFORMATION['perform'][i] for i in self.public_information['perform'] if IMPLIED_INFORMATION['perform'].get(i)]))
        victim = Counter(chain(*[IMPLIED_INFORMATION['block'][i] for i in self.public_information['victim'] if IMPLIED_INFORMATION['block'].get(i)]))
        spectator = Counter(chain(*[IMPLIED_INFORMATION['block'][i] for i in self.public_information['spectator'] if IMPLIED_INFORMATION['block'].get(i)]))

        result = Counter()
        for _ in range(WEIGHTS['performed_action']):
            result.update(performed)

        for _ in range(WEIGHTS['blocked_selfishly']):
            result.update(victim)

        for _ in range(WEIGHTS['blocked_selflessly']):
            result.update(spectator)

        return dict(result.most_common())

    @property
    def improbable_influences(self):
        from collections import Counter
        from itertools import chain
        
        performed = Counter(chain(*[IMPLIED_INFORMATION['suboptimal_move'][i] for i in self.public_information['perform'] if IMPLIED_INFORMATION['suboptimal_move'].get(i)]))
        victim = Counter(chain(*[IMPLIED_INFORMATION['block'][i] for i in self.didnt_block_as['victim'] if IMPLIED_INFORMATION['block'].get(i)]))
        spectator = Counter(chain(*[IMPLIED_INFORMATION['block'][i] for i in self.didnt_block_as['spectator'] if IMPLIED_INFORMATION['block'].get(i)]))

        result = Counter()
        for _ in range(abs(WEIGHTS['suboptimal_move'])):
            result.update(performed)

        for _ in range(abs(WEIGHTS['didnt_block_selfishly'])):
            result.update(victim)

        for _ in range(abs(WEIGHTS['didnt_block_selflessly'])):
            result.update(spectator)
        
        return dict(result.most_common())

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
    
    @property
    def influence_binary(self):
        influences = ['Ambassador', 'Assassin', 'Captain', 'Contessa', 'Duke']
        return tuple(1 if inf in self else 0 for inf in influences)
        
    @classmethod
    def actions_for_influences(cls, influences):
        actions = []
        for inf in Influence.__subclasses__():
            if inf.__name__ in influences:
                actions.extend(inf.ACTIONS)
        return sorted(actions)
        
    @classmethod
    def blocks_for_influences(cls, influences):
        blocks = []
        for inf in Influence.__subclasses__():
            if inf.__name__ in influences:
                blocks.extend(inf.BLOCKS)
        return sorted(blocks)
        
    def calculate(self, likelihood, type_of_action):
        if type_of_action == 'actions':
            if likelihood == 'probable':
                infs = sorted(self.probable_influences.items(), reverse=True, key=lambda i: i[1])
                infs = [inf for inf, score in infs[0:2]]
                return self.actions_for_influences(infs)
            elif likelihood == 'improbable':
                infs = sorted(self.improbable_influences.items(), reverse=True, key=lambda i: i[1])
                infs = [inf for inf, score in infs[0:2]]
                return self.actions_for_influences(infs)
            elif likelihood == 'judge':
                return self.actions_for_influences(self.best_guess)
        elif type_of_action == 'blocks':
            if likelihood == 'probable':
                infs = sorted(self.probable_influences.items(), reverse=True, key=lambda i: i[1])
                infs = [inf for inf, score in infs[0:2]]
                return self.blocks_for_influences(infs)
            elif likelihood == 'improbable':
                infs = sorted(self.improbable_influences.items(), reverse=True, key=lambda i: i[1])
                infs = [inf for inf, score in infs[0:2]]
                return self.blocks_for_influences(infs)
            elif likelihood == 'judge':
                return self.blocks_for_influences(self.best_guess)

class AI_Persona(Player):        
    def __init__(self, personality='passive'):
        Player.__init__(self)
        self.personalize(personality)
        
    def personalize(self, personality):
        from copy import deepcopy
        self.rules = deepcopy(PERSONALITIES[personality])
        self.saved_personality = personality
        
    def select_opponent(self, all_players):
        from random import choice
        return choice([v for v in all_players if v is not self and v.influence_remaining])

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
        elif action == 'tax':
            return choice(['tax'] * 5 + ['assassinate'])
        else:
            return action
            
    def one_on_one_strategy(self, influences, honest=True):
        action_plan = []
        if self.coins >= 10:
            action_plan = ['coup']
        else:
            try:
                action_plan.extend(AI_Persona.offensive_priority(influences))
                action_plan.extend(AI_Persona.buildup_priority(influences))
            except KeyError:
                pass
        
        if honest:
            return [a for a in action_plan if a in self.valid_actions + Play_Coup.ACTIONS['free']]
        else:
            return action_plan

    def will_intervene(self, action, performer, victim=None):
        try:
            rules = self.rules['honest_intervention'][action].items()
            
            if action in self.valid_blocks and len(rules):
                for participant, lambda_func in rules:
                    if lambda_func and not lambda_func(locals()[participant]):
                        break
                else:
                    return True  
        except KeyError:
            pass

        try:
            rules = self.rules['calculated_intervention'][action].items()
            
            if len(rules):
                for participant, lambda_func in rules:
                    if lambda_func and not lambda_func(locals()[participant]):
                        break
                else:
                    return True  
        except KeyError:
            pass
        
        return False
        
    def will_callout(self, action, performer):
        try:
            if sum(len(v) for k,v in performer.public_information.items()) >= self.rules['callout']['min_actions'] and \
                sum(len(v) for k,v in performer.didnt_block_as.items()) >= self.rules['callout']['min_inactions'] and \
                performer.judge_player[[a.__name__ for a in Influence.__subclasses__() if action in a.ACTIONS][0]] <= self.rules['callout']['threshold']:
                return True
        except KeyError:
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

    @classmethod
    def offensive_priority(cls, influences):
        return {
            'Ambassador': ['assassinate', 'coup'],
            'Assassin': ['steal', 'assassinate', 'coup'],
            'Captain': ['assassinate', 'coup'],
            'Contessa': ['steal', 'coup'],
            'Duke': ['steal', 'assassinate', 'coup'],
            'Ambassador Ambassador': ['assassinate', 'coup'],
            'Assassin Assassin': ['steal', 'assassinate', 'coup'],
            'Captain Captain': ['assassinate', 'coup'],
            'Contessa Contessa': ['steal', 'coup'],
            'Duke Duke': ['steal', 'assassinate', 'coup'],
            'Ambassador Assassin': ['assassinate', 'coup'],
            'Ambassador Captain': ['assassinate', 'coup'],
            'Ambassador Contessa': ['coup'],
            'Ambassador Duke': ['assassinate', 'coup'],
            'Assassin Captain': ['assassinate', 'coup'],
            'Assassin Contessa': ['steal', 'coup'],
            'Assassin Duke': ['steal', 'assassinate', 'coup'],
            'Captain Contessa': ['coup'],
            'Captain Duke': ['assassinate', 'coup'],
            'Contessa Duke': ['steal', 'coup']
            }[influences]

    @classmethod
    def buildup_priority(cls, influences):
        return {
            'Ambassador': ['tax', 'foreign_aid', 'income'],
            'Assassin': ['tax', 'foreign_aid', 'income'],  
            'Captain': ['tax', 'foreign_aid', 'income'],
            'Contessa': ['tax', 'foreign_aid', 'income'],
            'Duke': ['tax', 'income'],
            'Ambassador Ambassador': ['tax', 'foreign_aid', 'income'],
            'Assassin Assassin': ['tax', 'foreign_aid', 'income'],
            'Captain Captain': ['tax', 'foreign_aid', 'income'],
            'Contessa Contessa': ['tax', 'foreign_aid', 'income'],
            'Duke Duke': ['tax', 'income'],
            'Ambassador Assassin': ['tax', 'foreign_aid', 'income'],
            'Ambassador Captain': ['tax', 'foreign_aid', 'income'],
            'Ambassador Contessa': ['tax', 'foreign_aid', 'income'],
            'Ambassador Duke': ['tax', 'income'],
            'Assassin Captain': ['tax', 'foreign_aid', 'income'],
            'Assassin Contessa': ['tax', 'foreign_aid', 'income'],
            'Assassin Duke': ['tax', 'income'],
            'Captain Contessa': ['tax', 'foreign_aid', 'income'],
            'Captain Duke': ['tax', 'income'],
            'Contessa Duke': ['tax', 'income']
            }[influences]

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
        from random import randint

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

class EndTurn(Exception):
    pass

class RethinkAction(Exception):
    def __init__(self, action, performer, victim):
        self.action = action
        self.performer = performer
        self.victim = victim

        self.message = '{0} rethinks {1} on {2}'.format(performer.status, action, victim.status)

class BlockedAction(Exception):
    def __init__(self, action, performer, victim, spectator):
        self.action = action
        self.performer = performer
        self.victim = victim
        self.spectator = spectator

        if self.victim:
            if action == 'assassinate':
                self.performer.coins -= 3
                
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

class QuestionInfluence(Exception):
    def __init__(self, action, performer, doubter):
        self.action = action
        self.performer = performer
        self.doubter = doubter
        
        if action in self.performer.valid_actions:
            self.message = "{0} doubts {1} can {2}: doubter loses one influence!".format(self.doubter,
                                                                                         self.performer,
                                                                                         self.action)
            self.performer_is_honest = True
            influence = self.doubter.random_remaining_influence[1]
            influence.reveal()
            self.doubter.remove_suspicion(str(influence))
        else:
            self.message = "{0} doubts {1} can {2}: performer loses one influence!".format(self.doubter,
                                                                                           self.performer,
                                                                                           self.action)
            self.performer_is_honest = False
            influence = self.performer.random_remaining_influence[1]
            influence.reveal()
            self.performer.remove_suspicion(str(influence))
