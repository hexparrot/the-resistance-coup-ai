"""
Python scripts to simulate the game "The Resistance: Coup designed by Rikki Tahta
The purpose of this project is to model human personalities and predict/score
behaviors and bluffs in order to win the game.

"""

__author__ = "William Dizon"
__license__ = "GNU GPL v3.0"
__version__ = "0.0.1"
__email__ = "wdchromium@gmail.com"

from coup import *
from itertools import cycle
from heuristics import PERSONALITIES
from random import random, choice

def run(simulation, players, iterations):
    from collections import Counter
    wins = Counter()
    for _ in range(iterations):
        wins.update([simulation(players).winner.alpha,])
    return dict(wins)

def sim_random_actions_random_targets_no_blocking(players):
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
    testgame = Play_Coup(players, PERSONALITIES.keys())

    for acting_player in cycle(testgame.players):
        if not acting_player.influence_remaining:
            continue
        elif len(testgame) == 1:
            return testgame

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

def sim_random_actions_random_targets_selfish_blocks_no_doubts(players):
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
    testgame = Play_Coup(players, PERSONALITIES.keys())

    for acting_player in cycle(testgame.players):
        if not acting_player.influence_remaining:
            continue
        elif len(testgame) == 1:
            return testgame

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

def sim_naive_actions_calculated_targets_selfish_blocks_no_doubts(players):
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
    testgame = Play_Coup(players, PERSONALITIES.keys())

    for acting_player in cycle(testgame.players):
        if not acting_player.influence_remaining:
            continue
        elif len(testgame) == 1:
            return testgame

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

def sim_naive_actions_calculated_targets_calculated_blocks_no_doubts(players):
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
    testgame = Play_Coup(players, PERSONALITIES.keys())

    for acting_player in cycle(testgame.players):
        if not acting_player.influence_remaining:
            continue
        elif len(testgame) == 1:
            return testgame

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

def sim_calculated_actions_calculated_targets_more_calculated_blocks_no_doubts(players):
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
    testgame = Play_Coup(players, PERSONALITIES.keys())

    for acting_player in cycle(testgame.players):
        if not acting_player.influence_remaining:
            continue
        elif len(testgame) == 1:
            return testgame

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

def sim_calculated_actions_calculated_targets_more_calculated_blocks_systemic_doubts(players):
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
    testgame = Play_Coup(players, PERSONALITIES.keys())

    for acting_player in cycle(testgame.players):
        if not acting_player.influence_remaining:
            continue
        elif len(testgame) == 1:
            return testgame

        while 1:
            try:
                action = acting_player.random_naive_priority()
                #print '{0} performing {1} (coins={2})'.format(acting_player, action, acting_player.coins)

                if action == 'income':
                    acting_player.perform(action)
                    break
                if action == 'tax':
                    acting_player.perform(action)
                    break
                elif action == 'coup':
                    random_player = acting_player.select_opponent(testgame.players)
                    position, random_target = random_player.random_remaining_influence
                    acting_player.perform(action, random_target)
                    random_player.remove_suspicion(str(random_target))
                    break
                elif action == 'foreign_aid':
                    for savior in testgame.filter_out_players([acting_player]):
                        if savior.will_intervene(action, acting_player):
                            for spectators in testgame.filter_out_players([acting_player, savior]):
                                spectators.didnt_block_as['spectator'].extend([action])
                            raise BlockedAction(action, acting_player, None, savior)
                    else:
                        acting_player.perform(action)
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
                                if action in acting_player.valid_actions:
                                    acting_player.perform(action, random_player)
                                raise QuestionInfluence(doubter, acting_player, 'Captain', testgame.court_deck, 'steal')

                        acting_player.perform(action, random_player)
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
                                raise QuestionInfluence(doubter, acting_player, 'Assassin', testgame.court_deck, 'assassinate')
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                        random_player.remove_suspicion(str(random_target))
                        for spectators in testgame.filter_out_players([acting_player, random_player]):
                            spectators.didnt_block_as['spectator'].extend([action])
                        break
                elif action == 'exchange':
                    for doubter in testgame.filter_out_players([acting_player]):
                        if doubter.will_callout(action, acting_player):
                            if action in acting_player.valid_actions:
                                acting_player.perform(action, testgame.court_deck)
                            raise QuestionInfluence(doubter, acting_player, 'Ambassador', testgame.court_deck, 'block_exchange')
                    break
                elif action == 'coup':
                    random_player = acting_player.select_opponent(testgame.players)
                    position, random_target = random_player.random_remaining_influence
                    acting_player.perform(action, random_target)
                    random_player.remove_suspicion(str(random_target))
                    break
            except (IllegalAction, IllegalTarget):
                pass
            except BlockedAction:
                break
            except RethinkAction:
                pass
            except QuestionInfluence:
                break

def sim_refined_actions_calculated_targets_more_calculated_blocks_systemic_doubts(players):
    """
    AI PROFILE:

    Action          Used        Targets     Blocked
    income          yes
    foreign_aid     yes                     by ai profile
    coup            yes
    steal           yes         random      by ai profile
    tax             yes
    assassinate     yes         random      by ai profile
    exchange        yes         random      no

    """
    testgame = Play_Coup(players, PERSONALITIES.keys())

    for acting_player in cycle(testgame.players):
        if not acting_player.influence_remaining:
            continue
        elif len(testgame) == 1:
            return testgame
        elif len(testgame) == 2:
            remaining_opponent = acting_player.select_opponent(testgame.players)
            action_plan = acting_player.one_on_one_strategy(remaining_opponent.best_guess, True)
        else:
            action_plan = []
            remaining_opponent = None

        while 1:
            try:
                if action_plan:
                    action = action_plan.pop(0)
                else:
                    action = acting_player.random_naive_priority()

                if action == 'income':
                    acting_player.perform(action)
                    break
                if action == 'tax':
                    acting_player.perform(action)
                    break
                elif action == 'coup':
                    random_player = acting_player.select_opponent(testgame.players) if not remaining_opponent else remaining_opponent
                    position, random_target = random_player.random_remaining_influence
                    acting_player.perform(action, random_target)
                    random_player.remove_suspicion(str(random_target))
                    break
                elif action == 'foreign_aid':
                    for savior in testgame.filter_out_players([acting_player]):
                        if savior.will_intervene(action, acting_player):
                            for spectators in testgame.filter_out_players([acting_player, savior]):
                                spectators.didnt_block_as['spectator'].extend([action])

                            if action not in savior.calculate('judge', 'blocks'):
                                try:
                                    raise QuestionInfluence(acting_player, savior, 'Duke', testgame.court_deck, 'block_foreign_aid')
                                except QuestionInfluence as e:
                                    if e.doubter_is_correct:
                                        acting_player.perform(action)
                                        break
                                    else:
                                        raise BlockedAction(action, acting_player, None, savior)
                    else:
                        acting_player.perform(action)
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
                                    try:
                                        raise QuestionInfluence(acting_player, savior, representing, testgame.court_deck, 'block_steal')
                                    except QuestionInfluence as e:
                                        if e.doubter_is_correct:
                                            acting_player.perform(action)
                                            break
                                        else:
                                            raise BlockedAction(action, acting_player, None, savior)

                        for doubter in testgame.filter_out_players([acting_player]):
                            if doubter.will_callout(action, acting_player):
                                if action in acting_player.valid_actions:
                                    acting_player.perform(action, random_player)
                                raise QuestionInfluence(doubter, acting_player, 'Captain', testgame.court_deck, 'steal')

                        acting_player.perform(action, random_player)
                        for spectators in testgame.filter_out_players([acting_player, savior]):
                            spectators.didnt_block_as['spectator'].extend([action])
                        break
                elif action == 'assassinate':
                    random_player = acting_player.select_opponent(testgame.players) if not remaining_opponent else remaining_opponent
                    if action in random_player.calculate('probable', 'blocks'):
                        raise RethinkAction(action, acting_player, random_player)
                    elif action in random_player.valid_blocks:
                        raise BlockedAction(action, acting_player, random_player, None)
                    else:
                        for savior in testgame.filter_out_players([acting_player, random_player]):
                            if savior.will_intervene(action, acting_player, random_player):
                                for spectators in testgame.filter_out_players([acting_player, savior]):
                                    spectators.didnt_block_as['spectator'].extend([action])
                                #contessa logic goes here, but is still partially flawed since contessa has no hard tells
                                raise BlockedAction(action, acting_player, random_player, savior)

                        for doubter in testgame.filter_out_players([acting_player]):
                            if doubter.will_callout(action, acting_player):
                                if action in acting_player.valid_actions:
                                    position, random_target = random_player.random_remaining_influence
                                    acting_player.perform(action, random_target)
                                    random_player.remove_suspicion(str(random_target))
                                raise QuestionInfluence(doubter, acting_player, 'Assassin', testgame.court_deck, 'assassinate')
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                        random_player.remove_suspicion(str(random_target))
                        for spectators in testgame.filter_out_players([acting_player, random_player]):
                            spectators.didnt_block_as['spectator'].extend([action])
                        break
                elif action == 'exchange':
                    for doubter in testgame.filter_out_players([acting_player]):
                        if doubter.will_callout(action, acting_player):
                            if action in acting_player.valid_actions:
                                acting_player.perform(action, testgame.court_deck)
                            raise QuestionInfluence(doubter, acting_player, 'Ambassador', testgame.court_deck, 'block_exchange')
                    break
            except IllegalAction:
                pass
            except IllegalTarget:
                pass
            except BlockedAction:
                break
            except RethinkAction:
                pass
            except QuestionInfluence:
                break

def sim_a_full_on_yomi(players):
    testgame = Play_Coup(players, PERSONALITIES.keys())

    for acting_player in cycle(testgame.players):
        if not acting_player.influence_remaining:
            continue
        elif len(testgame) == 1:
            return testgame

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
                    break
                if action == 'tax':
                    acting_player.perform(action)
                    break
                elif action == 'coup':
                    if remaining_opponent:
                        victim = remaining_opponent
                    else:
                        for random_opponent in testgame.filter_out_players([acting_player]):
                            if not acting_player.wins_duel(random_opponent):
                                victim = random_opponent
                                break
                            else:
                                victim = acting_player.select_opponent(testgame.players)

                    position, random_target = victim.random_remaining_influence
                    acting_player.perform(action, random_target)
                    victim.remove_suspicion(str(random_target))
                    break
                elif action == 'foreign_aid':
                    for savior in testgame.filter_out_players([acting_player]):
                        if not savior.wins_duel(acting_player):
                            opponent = savior
                            break
                    else:
                        opponent = None

                    if opponent and opponent.will_intervene(action, acting_player):
                        for spectators in testgame.filter_out_players([acting_player, opponent]):
                            spectators.didnt_block_as['spectator'].extend([action])

                        if acting_player.will_callout('block_foreign_aid', opponent) and \
                            acting_player.plays_numbers and \
                            random() > AI_Persona.probability_player_influences(testgame.players, opponent, 'Duke', acting_player):
                            if action not in opponent.valid_blocks:
                                acting_player.perform(action)
                            raise QuestionInfluence(acting_player, opponent, 'Duke', testgame.court_deck, 'foreign_aid')
                        elif action in opponent.valid_blocks:
                            raise BlockedAction(action, acting_player, None, opponent)

                    acting_player.perform(action)
                    break
                elif action == 'steal':
                    if remaining_opponent:
                        victim = remaining_opponent
                    else:
                        for opponent in testgame.filter_out_players([acting_player]):
                            if not acting_player.wins_duel(opponent) and action not in opponent.calculate('judge', 'blocks'):
                                victim = opponent
                                break
                        else:
                            victim = acting_player.select_opponent(testgame.players)

                    if action in victim.valid_blocks:
                        raise BlockedAction(action, acting_player, victim, None)
                    else:
                        for savior in testgame.filter_out_players([acting_player, victim]):
                            representing = savior.will_intervene(action, acting_player, victim)
                            if representing:
                                #logic to doubt savior (ambassador doesnt leave hints, so excess failed callouts)
                                '''for doubter in testgame.filter_out_players([acting_player, savior, victim]):
                                    if doubter.will_callout('block_steal', savior):
                                        if action not in savior.valid_blocks:
                                            acting_player.perform(action, victim)
                                            self.ACTIONS[acting_player.alpha].append(action)
                                        raise QuestionInfluence(doubter, savior, representing, testgame.court_deck, 'block_steal')
                                '''
                                for spectators in testgame.filter_out_players([acting_player, savior, victim]):
                                    spectators.didnt_block_as['spectator'].extend([action])
                                raise BlockedAction(action, acting_player, victim, savior)

                        for doubter in testgame.filter_out_players([acting_player]):
                            if doubter.will_callout(action, acting_player):
                                if action in acting_player.valid_actions:
                                    acting_player.perform(action, victim)
                                raise QuestionInfluence(doubter, acting_player, 'Captain', testgame.court_deck, 'steal')

                        acting_player.perform(action, victim)
                        for spectators in testgame.filter_out_players([acting_player]):
                            spectators.didnt_block_as['spectator'].extend([action])
                        break
                elif action == 'assassinate':
                    if remaining_opponent:
                        victim = remaining_opponent
                    else:
                        for opponent in testgame.filter_out_players([acting_player]):
                            if not acting_player.wins_duel(opponent) and \
                                random() > AI_Persona.probability_player_influences(testgame.players, opponent, 'Contessa', acting_player):
                                victim = opponent
                                break
                        else:
                            victim = acting_player.select_opponent(testgame.players)

                    if action in victim.valid_blocks:
                        raise BlockedAction(action, acting_player, victim, None)
                    else:
                        for savior in testgame.filter_out_players([acting_player, victim]):
                            representing = savior.will_intervene(action, acting_player, victim)
                            if representing:
                                for spectators in testgame.filter_out_players([acting_player, savior, victim]):
                                    spectators.didnt_block_as['spectator'].extend([action])
                                #omitted logic to doubt savior (contessa doesnt leave hints, so excess failed callouts)
                                raise BlockedAction(action, acting_player, victim, savior)

                        for doubter in testgame.filter_out_players([acting_player]):
                            if doubter.will_callout(action, acting_player):
                                if action in acting_player.valid_actions:
                                    position, random_target = victim.random_remaining_influence
                                    acting_player.perform(action, random_target)
                                    victim.remove_suspicion(str(random_target))
                                raise QuestionInfluence(doubter, acting_player, 'Assassin', testgame.court_deck, 'assassinate')

                        position, random_target = victim.random_remaining_influence
                        acting_player.perform(action, random_target)
                        victim.remove_suspicion(str(random_target))
                        for spectators in testgame.filter_out_players([acting_player, victim]):
                            spectators.didnt_block_as['spectator'].extend([action])
                        break
                elif action == 'exchange':
                    for doubter in testgame.filter_out_players([acting_player]):
                        if doubter.will_callout(action, acting_player) and \
                            doubter.plays_numbers and \
                            random() > AI_Persona.probability_player_influences(testgame.players, acting_player, 'Ambassador', doubter):
                            if action in acting_player.valid_actions:
                                acting_player.perform(action, testgame.court_deck)
                            raise QuestionInfluence(doubter, acting_player, 'Ambassador', testgame.court_deck, 'exchange')

                    acting_player.perform(action, testgame.court_deck)
                    break
            except IllegalAction:
                pass
            except IllegalTarget:
                pass
            except BlockedAction:
                break
            except RethinkAction:
                pass
            except QuestionInfluence:
                break

@staticmethod
def duel(coup_game):
    duel = Play_Coup(2)
    duel.players[0] = coup_game.players[0].clone()
    duel.players[1] = coup_game.players[1].clone()

    for acting_player in cycle(duel.players):
        try:
            if not acting_player.influence_remaining:
                continue
            elif len(duel) == 1:
                return duel

            opp = [duel.players[0], duel.players[1]][acting_player is duel.players[0]]
            assert(acting_player is not opp)
            action_plan = acting_player.one_on_one_strategy(opp.alpha, True)

            while 1:
                action = action_plan.pop(0)
                if action not in acting_player.valid_actions + ['foreign_aid','income','coup']:
                    pass
                elif action in opp.valid_blocks:
                    break
                else:
                    if action in ['income', 'tax', 'foreign_aid']:
                        acting_player.perform(action)
                    elif action in ['assassinate', 'coup']:
                        position, random_target = opp.random_remaining_influence
                        acting_player.perform(action, random_target)
                    elif action in ['exchange']:
                        acting_player.perform('exchange', duel.players)
                    elif action in ['steal']:
                        acting_player.perform('steal', opp)
                    break
        except IllegalTarget:
            continue