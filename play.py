"""
Python scripts to simulate the game "The Resistance: Coup designed by Rikki Tahta
The purpose of this project is to model human personalities and predict/score
behaviors and bluffs in order to win the game.

"""
from __future__ import print_function
from itertools import cycle
from collections import Counter, defaultdict
from coup import *
from heuristics import PERSONALITIES
from random import random

__author__ = "William Dizon"
__license__ = "GNU GPL v3.0"
__version__ = "0.0.1"
__email__ = "wdchromium@gmail.com"

class simulations(object):
    PLAYERS = 5
    ACTIONS = defaultdict(list)
    BLOCKS_SAVIOR = defaultdict(list)
    BLOCKS_VICTIM = defaultdict(list)
    DOUBTS_ACTIONS = defaultdict(list)
    DOUBTS_RIGHT = defaultdict(list)
    DOUBTS_ACTIONS_RIGHT = defaultdict(list)
    DOUBTS_THRESHOLD_RIGHT = defaultdict(list)
    DOUBTS_THRESHOLD_WRONG = defaultdict(list)
    WINS = defaultdict(int)
    ILL_ACT = defaultdict(list)
    ILL_TAR = defaultdict(list)
    RET_ACT_GOOD = defaultdict(list)
    RET_ACT_REGRET = defaultdict(list)
    GUESSED_CONTESSA = defaultdict(int)
    
    def sim_full_on_yomi(self):
        testgame = Play_Coup(self.PLAYERS, PERSONALITIES.keys())

        for acting_player in cycle(testgame.players):
            if not acting_player.influence_remaining:
                continue
            elif len(testgame) == 1:
                self.WINS[acting_player.saved_personality] += 1
                return acting_player.alpha
                
            action_plan = []
            remaining_opponent = None
            
            if len(testgame) == 2:
                remaining_opponent = acting_player.select_opponent(testgame.players)
                action_plan = acting_player.one_on_one_strategy(remaining_opponent.best_guess, True)
            
            while 1:
                try:
                    if action_plan:
                        action = action_plan.pop(0)
                    else:
                        action = acting_player.random_naive_priority()

                    if action == 'income':
                        acting_player.perform(action)
                        self.ACTIONS[acting_player.alpha].append(action)
                        break
                    if action == 'tax':
                        acting_player.perform(action)
                        self.ACTIONS[acting_player.alpha].append(action)
                        break
                    elif action == 'coup':
                        random_player = acting_player.select_opponent(testgame.players) if not remaining_opponent else remaining_opponent
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
                                
                                if acting_player.will_callout('block_foreign_aid', savior) and \
                                    acting_player.plays_numbers and \
                                    random() > AI_Persona.probability_player_influences(testgame.players, savior, 'Duke', acting_player):                                    
                                    if action not in savior.valid_blocks:
                                        acting_player.perform(action)
                                        self.ACTIONS[acting_player.alpha].append(action)
                                    raise QuestionInfluence(acting_player, savior, 'Duke', testgame.court_deck, 'foreign_aid')
                                raise BlockedAction(action, acting_player, None, savior)
                        else:
                            acting_player.perform(action)
                            self.ACTIONS[acting_player.alpha].append(action)
                            break
                    elif action == 'steal':
                        random_player = acting_player.select_opponent(testgame.players) if not remaining_opponent else remaining_opponent
                        if action in random_player.calculate('probable', 'blocks'):
                            raise RethinkAction(action, acting_player, random_player)
                        elif action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)
                        else:
                            for savior in testgame.filter_out_players([acting_player, random_player]):
                                representing = savior.will_intervene(action, acting_player, random_player)
                                if representing:
                                    for spectators in testgame.filter_out_players([acting_player, savior]):
                                        spectators.didnt_block_as['spectator'].extend([action])
                                    raise BlockedAction(action, acting_player, random_player, savior)
                                    
                                    if action not in savior.calculate('judge', 'blocks'):
                                        raise QuestionInfluence(acting_player, savior, representing, testgame.court_deck, 'steal')
                            for doubter in testgame.filter_out_players([acting_player]):
                                if doubter.will_callout(action, acting_player):
                                    if action in acting_player.valid_actions:
                                        acting_player.perform(action, random_player)
                                        self.ACTIONS[acting_player.alpha].append(action)
                                    raise QuestionInfluence(doubter, acting_player, 'Captain', testgame.court_deck, 'steal')
                        
                            acting_player.perform(action, random_player)
                            self.ACTIONS[acting_player.alpha].append(action)
                            for spectators in testgame.filter_out_players([acting_player, savior]):
                                spectators.didnt_block_as['spectator'].extend([action])
                            break
                    elif action == 'assassinate':
                        from random import random
                        random_player = acting_player.select_opponent(testgame.players) if not remaining_opponent else remaining_opponent
                        if action in random_player.calculate('probable', 'blocks'):
                            raise RethinkAction(action, acting_player, random_player)
                        elif random() <= AI_Persona.probability_player_influences(testgame.players, random_player, 'Contessa', acting_player):
                            raise RethinkAction(action, acting_player, random_player)
                        elif action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)
                        else:
                            for savior in testgame.filter_out_players([acting_player, random_player]):
                                if savior.will_intervene(action, acting_player, random_player):
                                    for spectators in testgame.filter_out_players([acting_player, savior]):
                                        spectators.didnt_block_as['spectator'].extend([action])
                                    raise BlockedAction(action, acting_player, random_player, savior)
                                    
                            for doubter in testgame.filter_out_players([acting_player]):
                                if doubter.will_callout(action, acting_player):
                                    if action in acting_player.valid_actions:
                                        position, random_target = random_player.random_remaining_influence
                                        acting_player.perform(action, random_target)
                                        self.ACTIONS[acting_player.alpha].append(action)
                                        random_player.remove_suspicion(str(random_target))
                                    raise QuestionInfluence(doubter, acting_player, 'Assassin', testgame.court_deck, 'assassinate')
                            position, random_target = random_player.random_remaining_influence
                            acting_player.perform(action, random_target)
                            random_player.remove_suspicion(str(random_target))
                            self.ACTIONS[acting_player.alpha].append(action)
                            for spectators in testgame.filter_out_players([acting_player, random_player]):
                                spectators.didnt_block_as['spectator'].extend([action])
                            break
                    elif action == 'exchange':
                        from random import random
                        for doubter in testgame.filter_out_players([acting_player]):
                            probability = AI_Persona.probability_player_influences(testgame.players, acting_player, 'Ambassador', doubter)
                            if doubter.will_callout(action, acting_player) and \
                                doubter.plays_numbers and \
                                random() > probability:
                                if action in acting_player.valid_actions:
                                    acting_player.perform(action, testgame.court_deck)
                                    self.ACTIONS[acting_player.alpha].append(action)
                                raise QuestionInfluence(doubter, acting_player, 'Ambassador', testgame.court_deck, 'exchange')
                        self.ACTIONS[acting_player.alpha].append(action)
                        break
                except IllegalAction as e:
                    self.ILL_ACT[acting_player.alpha].append(e.message)
                except IllegalTarget as e:
                    self.ILL_TAR[acting_player.alpha].append(e.message)
                except BlockedAction as e:
                    if e.spectator:
                        self.BLOCKS_SAVIOR[e.spectator.saved_personality].append(action)
                    else:
                        self.BLOCKS_VICTIM[e.victim.saved_personality].append(action)
                    break
                except RethinkAction as e:
                    if action in e.victim.valid_blocks:
                        self.RET_ACT_GOOD[e.victim.status].append(action)
                    else:
                        self.RET_ACT_REGRET[e.victim.status].append(action)
                except QuestionInfluence as e:
                    self.DOUBTS_ACTIONS[e.doubter.saved_personality].append(e.action)
                    self.DOUBTS_RIGHT[e.doubter.saved_personality].append(e.doubter_is_correct)
                    self.DOUBTS_ACTIONS_RIGHT[e.action].append(e.doubter_is_correct)
                    
                    if e.doubter_is_correct:
                        self.DOUBTS_THRESHOLD_RIGHT[e.doubter.saved_personality].append(e.alleged_bluffer.judge_player.get(e.alleged_influence, 0))
                    else:
                        self.DOUBTS_THRESHOLD_WRONG[e.doubter.saved_personality].append(e.alleged_bluffer.judge_player.get(e.alleged_influence, 0))
                    break
             
                
        
if __name__ == "__main__":
    c = Counter()
    for _ in range(1000):
        c.update([simulations().sim_full_on_yomi(),])
        
    for i,v in c.most_common():
        print('{0}{1}'.format(i.ljust(25), v))
    
    print()
    print('ACTIONS')
    for inf in simulations.ACTIONS:
        print('  {0}{1}'.format(inf.ljust(25), dict(Counter(simulations.ACTIONS[inf]).most_common())))

    print('WINS')
    for pers in simulations.WINS:
        print('    {0}{1}'.format(pers.ljust(23), simulations.WINS[pers]))

    print('BLOCKS')
    print('  Spectator')
    for pers in simulations.BLOCKS_SAVIOR:
        print('    {0}{1}'.format(pers.ljust(23), dict(Counter(simulations.BLOCKS_SAVIOR[pers]).most_common())))

    print('  Victim')      
    for pers in simulations.BLOCKS_VICTIM:
        print('    {0}{1}'.format(pers.ljust(23), dict(Counter(simulations.BLOCKS_VICTIM[pers]).most_common())))
    
    print('CALLOUTS')
    print('  Actions')
    for pers in simulations.DOUBTS_ACTIONS:
        print('    {0}{1}'.format(pers.ljust(25), dict(Counter(simulations.DOUBTS_ACTIONS[pers]).most_common())))
        print('    {0}{1}'.format(''.ljust(25), dict(Counter(simulations.DOUBTS_RIGHT[pers]).most_common())))
    for action in simulations.DOUBTS_ACTIONS_RIGHT:
        print('    {0}{1}'.format(action.ljust(25), dict(Counter(simulations.DOUBTS_ACTIONS_RIGHT[action]).most_common())))        
    
    print('  DOUBTER WRONG- Threshold:Frequency')
    for personality in simulations.DOUBTS_THRESHOLD_WRONG:
        print('    {0}{1}'.format(personality.ljust(25), ''.join('{0}:{1}  '.format(str(k).rjust(3),str(v).ljust(3)) for k,v in sorted(Counter(simulations.DOUBTS_THRESHOLD_WRONG[personality]).most_common()))))

    print('  DOUBTER RIGHT- Threshold:Frequency')
    for personality in simulations.DOUBTS_THRESHOLD_RIGHT:
        print('    {0}{1}'.format(personality.ljust(25), ''.join('{0}:{1}  '.format(str(k).rjust(3),str(v).ljust(3)) for k,v in sorted(Counter(simulations.DOUBTS_THRESHOLD_RIGHT[personality]).most_common()))))

    print('EXCEPTIONS')
    print('  IllegalAction')
    for inf in simulations.ILL_ACT:
        print('    {0}{1}'.format(inf.ljust(25), dict(Counter(simulations.ILL_ACT[inf]).most_common())))
    print('  IllegalTarget')
    for inf in simulations.ILL_TAR:
        print('    {0}{1}'.format(inf.ljust(25), dict(Counter(simulations.ILL_TAR[inf]).most_common())))
    print('  RethinkAction (victim influences listed)')
    print('    Good to rethink')
    for inf in simulations.RET_ACT_GOOD:
        print('      {0}{1}'.format(inf.ljust(25), dict(Counter(simulations.RET_ACT_GOOD[inf]).most_common())))
    print('    Should have followed through')
    for inf in simulations.RET_ACT_REGRET:
        print('      {0}{1}'.format(inf.ljust(25), dict(Counter(simulations.RET_ACT_REGRET[inf]).most_common())))
    