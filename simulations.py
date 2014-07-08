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
from random import choice, random
from coup import *

class simulations(object):
    PLAYERS = 5    

    def run(self, simulation_to_run, num):
        from collections import Counter
        wins = Counter()
        for _ in range(num):
            wins.update([getattr(self, simulation_to_run)(),])
        return dict(wins)
        
    @classmethod
    def available_simulations(cls):
        return sorted([method for method in dir(cls) if callable(getattr(cls, method)) and method.startswith('sim_')])
    
    def sim_random_actions_random_targets_no_blocking(self):  
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
        
        testgame = Play_Coup(self.PLAYERS)
        
        for acting_player in cycle(testgame.players):
            if not acting_player.influence_remaining:
                continue
            elif len(testgame) == 1:
                return acting_player.alpha

            while 1:
                try:
                    action = choice(Play_Coup.ACTIONS['all'])
                    if action == 'steal':
                        random_player = acting_player.select_opponent(testgame.players)
                        acting_player.perform(action, random_player)
                    elif action == 'assassinate':
                        random_player = acting_player.select_opponent(testgame.players)
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                    elif action == 'foreign_aid':
                        acting_player.perform(action)
                    elif action == 'exchange':
                        acting_player.perform(action, testgame.court_deck)
                    elif action == 'coup':
                        random_player = acting_player.select_opponent(testgame.players)
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                    else:
                        acting_player.perform(action)
                except (IllegalTarget, IllegalAction):
                    pass
                else:
                    break

    def sim_random_actions_random_targets_selfish_blocks_no_doubts(self):
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

        testgame = Play_Coup(self.PLAYERS)

        for acting_player in cycle(testgame.players):
            if not acting_player.influence_remaining:
                continue
            elif len(testgame) == 1:
                return acting_player.alpha

            while 1:
                try:
                    action = choice(Play_Coup.ACTIONS['all'])
                    if action == 'steal':
                        random_player = acting_player.select_opponent(testgame.players)
                        if action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)
                        acting_player.perform(action, random_player)
                    elif action == 'assassinate':
                        random_player = acting_player.select_opponent(testgame.players)
                        if action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                    elif action == 'foreign_aid':
                        random_player = acting_player.select_opponent(testgame.players)
                        if action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, None, random_player)
                        acting_player.perform(action)
                    elif action == 'exchange':
                        acting_player.perform(action, testgame.court_deck)
                    elif action == 'coup':
                        random_player = acting_player.select_opponent(testgame.players)
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                    else:
                        acting_player.perform(action)
                except (IllegalTarget, IllegalAction):
                    pass
                except BlockedAction:
                    break
                else:
                    break

    def sim_naive_actions_calculated_targets_selfish_blocks_no_doubts(self):
        """
        AI PROFILE:
        
        Action          Used        Targets     Blocked     
        income          yes
        foreign_aid     yes                     any available duke
        coup            yes
        steal           yes         unlikely    victim only
        tax             yes
        assassinate     yes         unlikely    victim only
        exchange        yes         unlikely    no

        """

        testgame = Play_Coup(self.PLAYERS)

        for acting_player in cycle(testgame.players):
            if not acting_player.influence_remaining:
                continue
            elif len(testgame) == 1:
                return acting_player.alpha

            while 1:
                try:
                    action = acting_player.random_naive_priority()
                    if action == 'steal':
                        random_player = acting_player.select_opponent(testgame.players)
                        if action in random_player.calculate('probable', 'blocks'):
                            raise RethinkAction(action, acting_player, random_player)
                        if action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)
                        acting_player.perform(action, random_player)
                    elif action == 'assassinate':
                        random_player = acting_player.select_opponent(testgame.players)
                        if action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                    elif action == 'foreign_aid':
                        for savior in testgame.filter_out_players([acting_player]):
                            if action in savior.valid_blocks:
                                raise BlockedAction(action, acting_player, None, savior)
                        acting_player.perform(action)
                    elif action == 'exchange':
                        acting_player.perform(action, testgame.court_deck)
                    elif action == 'coup':
                        random_player = acting_player.select_opponent(testgame.players)
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                    else:
                        acting_player.perform(action)
                except (IllegalTarget, IllegalAction):
                    pass
                except RethinkAction:
                    pass
                except BlockedAction:
                    break
                else:
                    break


    def sim_naive_actions_calculated_targets_calculated_blocks_no_doubts(self):
        """
        AI PROFILE:
        
        Action          Used        Targets     Blocked     
        income          yes
        foreign_aid     yes                     victim/by ai profile
        coup            yes
        steal           yes         unlikely    victim/by ai profile
        tax             yes
        assassinate     yes         unlikely    victim/by ai profile
        exchange        yes         random      no

        """
        
        testgame = Play_Coup(self.PLAYERS)

        for acting_player in cycle(testgame.players):
            if not acting_player.influence_remaining:
                continue
            elif len(testgame) == 1:
                return acting_player.alpha

            while 1:
                try:
                    action = acting_player.random_naive_priority()
                    if action == 'steal':
                        random_player = acting_player.select_opponent(testgame.players)
                        if action in random_player.calculate('probable', 'blocks'):
                            raise RethinkAction(action, acting_player, random_player)
                        if action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)

                        for savior in testgame.filter_out_players([acting_player, random_player]):
                            if savior.will_intervene(action, acting_player, random_player):
                                raise BlockedAction(action, acting_player, random_player, savior)
                        acting_player.perform(action, random_player)
                    elif action == 'assassinate':
                        random_player = acting_player.select_opponent(testgame.players)
                        if action in random_player.calculate('probable', 'blocks'):
                            raise RethinkAction(action, acting_player, random_player)
                        if action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)

                        for savior in testgame.filter_out_players([acting_player, random_player]):
                            if savior.will_intervene(action, acting_player, random_player):
                                raise BlockedAction(action, acting_player, random_player, savior)
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                        random_player.remove_suspicion(str(random_target))
                    elif action == 'foreign_aid':
                        for savior in testgame.filter_out_players([acting_player]):
                            if savior.will_intervene(action, acting_player):
                                raise BlockedAction(action, acting_player, None, savior)
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
                except RethinkAction:
                    pass
                else:
                    break

    def sim_calculated_actions_calculated_targets_more_calculated_blocks_no_doubts(self):
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

        testgame = Play_Coup(self.PLAYERS)

        for acting_player in cycle(testgame.players):
            if not acting_player.influence_remaining:
                continue
            elif len(testgame) == 1:
                return acting_player.alpha

            while 1:
                try:
                    action = acting_player.random_naive_priority()
                    if action == 'steal':
                        random_player = acting_player.select_opponent(testgame.players)
                        if (action in random_player.calculate('probable', 'blocks') and random() > .24):
                            raise RethinkAction(action, acting_player, random_player)
                        if action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)

                        for savior in testgame.filter_out_players([acting_player, random_player]):
                            if savior.will_intervene(action, acting_player, random_player):
                                raise BlockedAction(action, acting_player, random_player, savior)
                        acting_player.perform(action, random_player)
                    elif action == 'assassinate':
                        random_player = acting_player.select_opponent(testgame.players)
                        if (action in random_player.calculate('probable', 'blocks') and random() > .24):
                            raise RethinkAction(action, acting_player, random_player)
                        if action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)

                        for savior in testgame.filter_out_players([acting_player, random_player]):
                            if savior.will_intervene(action, acting_player, random_player):
                                raise BlockedAction(action, acting_player, random_player, savior)
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                        random_player.remove_suspicion(str(random_target))
                    elif action == 'foreign_aid':
                        for savior in testgame.filter_out_players([acting_player]):
                            if savior.will_intervene(action, acting_player):
                                raise BlockedAction(action, acting_player, None, savior)
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
                except RethinkAction:
                    pass
                else:
                    break

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

        testgame = Play_Coup(self.PLAYERS)

        for acting_player in cycle(testgame.players):
            if not acting_player.influence_remaining:
                continue
            elif len(testgame) == 1:
                return acting_player.alpha
                
            performer_will_restore = False

            while 1:
                try:
                    action = acting_player.random_naive_priority()
                    random_player = acting_player.select_opponent(testgame.players)
                    
                    if action not in ['coup', 'assassinate', 'income'] and \
                        action not in acting_player.calculate('judge', 'actions') and \
                        action not in Play_Coup.ACTIONS['free']:
                        for doubter in testgame.filter_out_players([acting_player]):
                            try:
                                if doubter.will_callout(action, acting_player):
                                    raise QuestionInfluence(action, acting_player, doubter)
                            except (IndexError, KeyError):
                                #indexerror if action not influence-specific
                                #keyerror if inf doesnt exist in acting_player.judge_player
                                pass
                            except QuestionInfluence as e:
                                if e.performer_is_honest:
                                    performer_will_restore = True
                                    if action == 'steal':
                                        acting_player.perform(action, random_player)
                                        raise EndTurn
                                    if not random_player.influence_remaining and \
                                        random_player is doubter:
                                        raise EndTurn
                                else:
                                    raise EndTurn

                    if action == 'steal':
                        if (action in random_player.calculate('probable', 'blocks') and random() > .24):
                            raise RethinkAction(action, acting_player, random_player)
                        if action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)

                        for savior in testgame.filter_out_players([acting_player, random_player]):
                            if savior.will_intervene(action, acting_player, random_player):
                                for spectators in testgame.filter_out_players([acting_player, savior]):
                                    spectators.not_acting_like['spectator'].extend([action])
                                raise BlockedAction(action, acting_player, random_player, savior)
                        acting_player.perform(action, random_player)
                    elif action == 'assassinate':
                        if (action in random_player.calculate('probable', 'blocks') and random() > .24):
                            raise RethinkAction(action, acting_player, random_player)
                        if action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)

                        for savior in testgame.filter_out_players([acting_player, random_player]):
                            if savior.will_intervene(action, acting_player, random_player):
                                for spectators in testgame.filter_out_players([acting_player, savior]):
                                    spectators.not_acting_like['spectator'].extend([action])
                                raise BlockedAction(action, acting_player, random_player, savior)
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                        random_player.remove_suspicion(str(random_target))
                    elif action == 'foreign_aid':
                        for savior in testgame.filter_out_players([acting_player]):
                            if savior.will_intervene(action, acting_player):
                                for spectators in testgame.filter_out_players([acting_player, savior]):
                                    spectators.not_acting_like['spectator'].extend([action])
                                raise BlockedAction(action, acting_player, None, savior)
                        acting_player.perform(action)
                    elif action == 'exchange':
                        acting_player.perform(action, testgame.court_deck)
                    elif action == 'coup':
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                        random_player.remove_suspicion(str(random_target))
                    else:
                        acting_player.perform(action)
                except (IllegalTarget, IllegalAction):
                    pass
                except EndTurn:
                    if performer_will_restore:
                        #will need refinement for captain/ambassador on blocked steal
                        if action in acting_player.left.ACTIONS:
                            acting_player.remove_suspicion(str(acting_player.left))
                            acting_player.restore('left', testgame.court_deck)
                        else:
                            acting_player.remove_suspicion(str(acting_player.right))
                            acting_player.restore('right', testgame.court_deck)
                    break
                except BlockedAction:
                    break
                except RethinkAction:
                    pass
                else:
                    if performer_will_restore:
                        #will need refinement for captain/ambassador on blocked steal
                        if action in acting_player.left.ACTIONS:
                            acting_player.remove_suspicion(str(acting_player.left))
                            acting_player.restore('left', testgame.court_deck)
                        else:
                            acting_player.remove_suspicion(str(acting_player.right))
                            acting_player.restore('right', testgame.court_deck)
                    break
