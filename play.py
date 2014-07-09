"""
Python scripts to simulate the game "The Resistance: Coup designed by Rikki Tahta
The purpose of this project is to model human personalities and predict/score
behaviors and bluffs in order to win the game.

"""

__author__ = "William Dizon"
__license__ = "GNU GPL v3.0"
__version__ = "0.0.1"
__email__ = "wdchromium@gmail.com"

from itertools import cycle
from collections import Counter, defaultdict
from coup import *
from heuristics import PERSONALITIES

class simulations(object):
    PLAYERS = 5
    ACTIONS = defaultdict(list)
    BLOCKS_S = defaultdict(list)
    BLOCKS_V = defaultdict(list)
    DOUBTS_P = defaultdict(list)
    DOUBTS_A = defaultdict(list)
    DOUBTS_W = defaultdict(list)
    WINS = defaultdict(int)
    
    def sim_calculated_actions_calculated_targets_more_calculated_blocks_random_doubts(self):
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

        testgame = Play_Coup(self.PLAYERS, PERSONALITIES.keys())
        
        for acting_player in cycle(testgame.players):
            if not acting_player.influence_remaining:
                continue
            elif len(testgame) == 1:
                self.WINS[acting_player.saved_personality] += 1
                return acting_player.alpha
                
            while 1:
                try:
                    action = acting_player.random_naive_priority()
                    #print '{0} performing {1} (coins={2})'.format(acting_player.status, action, acting_player.coins)
                    
                    if action == 'income':
                        acting_player.perform(action)
                        self.ACTIONS[acting_player.alpha].append(action)
                        break
                    if action == 'tax':
                        acting_player.perform(action)
                        self.ACTIONS[acting_player.alpha].append(action)
                        break
                    elif action == 'coup':
                        random_player = acting_player.select_opponent(testgame.players)
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                        random_player.remove_suspicion(str(random_target))
                        self.ACTIONS[acting_player.alpha].append(action)
                        break
                    elif action == 'foreign_aid':
                        for savior in testgame.filter_out_players([acting_player]):
                            if savior.will_intervene(action, acting_player):
                                for spectators in testgame.filter_out_players([acting_player, savior]):
                                    spectators.didnt_block_as['spectator'].extend([action])
                                raise BlockedAction(action, acting_player, None, savior)
                        else:
                            acting_player.perform(action)
                            self.ACTIONS[acting_player.alpha].append(action)
                            break
                    elif action == 'steal':
                        random_player = acting_player.select_opponent(testgame.players)
                        if action in random_player.calculate('probable', 'blocks') and random() > .33:
                            raise RethinkAction(action, acting_player, random_player)
                        elif action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)
                        else:
                            for savior in testgame.filter_out_players([acting_player, random_player]):
                                if savior.will_intervene(action, acting_player, random_player):
                                    raise BlockedAction(action, acting_player, random_player, savior)
                                    
                            for doubter in testgame.filter_out_players([acting_player]):
                                if doubter.will_callout(action, acting_player):
                                    if action in acting_player.valid_blocks:
                                        acting_player.perform(action, random_player)
                                    raise QuestionInfluence(action, acting_player, doubter)
                        
                            acting_player.perform(action, random_player)
                            self.ACTIONS[acting_player.alpha].append(action)
                            for spectators in testgame.filter_out_players([acting_player, savior]):
                                spectators.didnt_block_as['spectator'].extend([action])
                            break
                    elif action == 'assassinate':
                        random_player = acting_player.select_opponent(testgame.players)
                        if action in random_player.calculate('probable', 'blocks') and random() > .33:
                            raise RethinkAction(action, acting_player, random_player)
                        elif action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)
                        else:
                            for savior in testgame.filter_out_players([acting_player, random_player]):
                                if savior.will_intervene(action, acting_player, random_player):
                                    raise BlockedAction(action, acting_player, random_player, savior)
                                    
                            for doubter in testgame.filter_out_players([acting_player]):
                                if doubter.will_callout(action, acting_player):
                                    if action in acting_player.valid_actions:
                                        position, random_target = random_player.random_remaining_influence
                                        acting_player.perform(action, random_target)
                                        random_player.remove_suspicion(str(random_target))
                                    raise QuestionInfluence(action, acting_player, doubter)
                            position, random_target = random_player.random_remaining_influence
                            acting_player.perform(action, random_target)
                            random_player.remove_suspicion(str(random_target))
                            self.ACTIONS[acting_player.alpha].append(action)
                            for spectators in testgame.filter_out_players([acting_player, random_player]):
                                spectators.didnt_block_as['spectator'].extend([action])
                            break
                    elif action == 'exchange':
                        for doubter in testgame.filter_out_players([acting_player]):
                            if doubter.will_callout(action, acting_player):
                                if action in acting_player.valid_actions:
                                    acting_player.perform(action, testgame.court_deck)
                                raise QuestionInfluence(action, acting_player, doubter)
                        self.ACTIONS[acting_player.alpha].append(action)
                        break
                except (IllegalAction, IllegalTarget):
                    pass
                except BlockedAction as e:
                    if e.spectator:
                        self.BLOCKS_S[e.spectator.saved_personality].append(action)
                    else:
                        self.BLOCKS_V[e.victim.saved_personality].append(action)
                    break
                except RethinkAction:
                    pass
                except QuestionInfluence as e:
                    if e.performer_is_honest:
                        #will need refinement for captain/ambassador on blocked steal
                        if action in acting_player.left.ACTIONS and not acting_player.left.revealed:
                            acting_player.restore('left', testgame.court_deck)
                        elif action in acting_player.right.ACTIONS and not acting_player.right.revealed:
                            acting_player.restore('right', testgame.court_deck)
                    self.DOUBTS_A[e.doubter.saved_personality].append(action)
                    self.DOUBTS_W[e.doubter.saved_personality].append(e.performer_is_honest)
                    break

                    
                    
                
        
if __name__ == "__main__":
    c = Counter()
    for _ in range(1000):
        c.update([simulations().sim_calculated_actions_calculated_targets_more_calculated_blocks_random_doubts(),])
        
    for i,v in c.most_common():
        print('{0}{1}'.format(i.ljust(25), v))
    
    print
    print 'ACTIONS'
    for inf in simulations.ACTIONS:
        print '  {0}{1}'.format(inf.ljust(25), dict(Counter(simulations.ACTIONS[inf]).most_common()))
        
    print 'BLOCKS'
    print '  Spectator'
    for inf in simulations.BLOCKS_S:
        print '    {0}{1}'.format(inf.ljust(23), dict(Counter(simulations.BLOCKS_S[inf]).most_common()))
    
    print '  Victim'      
    for inf in simulations.BLOCKS_V:
      
        print '    {0}{1}'.format(inf.ljust(23), dict(Counter(simulations.BLOCKS_V[inf]).most_common()))
    
    print 'CALLOUTS'
    for inf in simulations.DOUBTS_A:
        print '  {0}{1}'.format(inf.ljust(25), dict(Counter(simulations.DOUBTS_A[inf]).most_common()))
        print '  {0}{1}'.format(''.ljust(25), dict(Counter(simulations.DOUBTS_W[inf]).most_common()))
    