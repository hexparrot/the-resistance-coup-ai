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
from collections import Counter
from coup import *
from random import choice

def player_summary(gamestate, player):
    print("***************")
    print("you are %s" % gamestate.players[player].status)
    print("you have %s coins" % gamestate.players[player].coins)
    print("you can truthfully perform:", ', '.join(gamestate.players[player].valid_actions))
    print()
    print("all available actions:")
    print("income, foreign_aid, coup, steal, tax, assassinate, exchange")
    print()

def play_game():
    PLAYERS = 5
    testgame = Play_Coup(PLAYERS)

    for i in cycle(range(PLAYERS)):
        if not testgame.players[i].influence_remaining:
            continue
        elif sum(1 for p in range(PLAYERS) if testgame.players[p].influence_remaining) == 1:
            break
        
        while 1:
            print('place in order:', i)
            player_summary(testgame, i)
            
            try:
                action = raw_input('what would you like to do? ')
                if action in Play_Coup.ACTIONS['targets_influence']:
                    player_target = int(raw_input('whom will you target (#0-4)? '))
                    position, random_target = testgame.players[player_target].random_remaining_influence
                    testgame.players[i].perform(action, random_target)
                elif action in Play_Coup.ACTIONS['targets_player']:
                    player_target = int(raw_input('whom will you target (#0-4)? '))
                    testgame.players[i].perform(action, testgame.players[player_target])
                else:
                    testgame.players[i].perform(action)
                break
            except (IllegalTarget, IllegalAction) as e:
                print(e.message)

        print()
        print()

class simulations(object):
    PLAYERS = 5
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
                    doubter = choice(list(testgame.filter_out_players([acting_player])))

                    if action in acting_player.improbable_actions and random() > .74:
                        try:
                            raise QuestionInfluence(action, acting_player, doubter)
                        except QuestionInfluence as e:
                            if e.performer_is_honest:
                                performer_will_restore = True
                                if action == 'steal':
                                    acting_player.perform(action, random_player)
                                if not random_player.influence_remaining and \
                                    random_player is doubter:
                                    action = None
                            else:
                                action = None
                            
                    if action == 'steal':
                        if (action in random_player.probable_blocks and random() > .24):
                            raise RethinkAction(action, acting_player, random_player)
                        if action in random_player.valid_blocks:
                            raise BlockedAction(action, acting_player, random_player, None)

                        for savior in testgame.filter_out_players([acting_player, random_player]):
                            if savior.will_intervene(action, acting_player, random_player):
                                raise BlockedAction(action, acting_player, random_player, savior)
                        acting_player.perform(action, random_player)
                    elif action == 'assassinate':
                        if (action in random_player.probable_blocks and random() > .24):
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
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                        random_player.remove_suspicion(str(random_target))
                    elif not action:
                        pass
                    else:
                        acting_player.perform(action)
                except (IllegalTarget, IllegalAction):
                    pass
                except BlockedAction:
                    break
                except RethinkAction:
                    pass
                else:
                    if performer_will_restore:
                        if action in e.performer.left.ACTIONS:
                            acting_player.restore('left', testgame.court_deck)
                        else:
                            acting_player.restore('right', testgame.court_deck)
                        break
                    break
                    
                
        
if __name__ == "__main__":
    c = Counter()
    for _ in range(1000):
        c.update([simulations().sim_calculated_actions_calculated_targets_more_calculated_blocks_random_doubts(),])

    for i,v in c.most_common():
        print('{0}{1}'.format(i.ljust(25), v))
