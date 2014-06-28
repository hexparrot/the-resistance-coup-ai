from itertools import cycle
from collections import Counter
from coup import *

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
    def test_gameplay_calculated_actions_calculated_targets_calculated_blocks_no_doubts(self):
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
                    action = acting_player.random_naive_priority()

                    if action in Play_Coup.ACTIONS['blockable']:
                        if action == 'steal':
                            random_player = acting_player.select_opponent(testgame.players)
                            if set(random_player.best_guesses).intersection(set([str(a()) for a in Influence.__subclasses__() if action in a.BLOCKS])):
                                raise RethinkAction(action, acting_player, random_player)
                            if 'steal' in random_player.valid_blocks:
                                raise BlockedAction(action, acting_player, random_player, None)
                            else:
                                for savior in range(PLAYERS):
                                    if savior != i and \
                                       random_player is not testgame.players[savior] and \
                                       testgame.players[savior].will_intervene(action, acting_player, random_player):
                                        raise BlockedAction(action, acting_player, random_player, testgame.players[savior])
                                else:
                                    testgame.players[i].perform(action, random_player)
                        elif action == 'assassinate':
                            random_player = acting_player.select_opponent(testgame.players)
                            if set(random_player.best_guesses).intersection(set([str(a()) for a in Influence.__subclasses__() if action in a.BLOCKS])):
                                raise RethinkAction(action, acting_player, random_player)
                            if 'assassinate' in random_player.valid_blocks:
                                raise BlockedAction(action, acting_player, random_player, None)
                            else:
                                for savior in range(PLAYERS):
                                    if savior != i and \
                                       random_player is not testgame.players[savior] and \
                                       testgame.players[savior].will_intervene(action, acting_player, random_player):
                                        raise BlockedAction(action, acting_player, random_player, testgame.players[savior])
                                else:
                                    position, random_target = random_player.random_remaining_influence
                                    testgame.players[i].perform(action, random_target)
                                    random_player.remove_suspicion(str(random_target))
                        elif action == 'foreign_aid':
                            for savior in range(PLAYERS):
                                if savior != i and testgame.players[savior].will_intervene(action, acting_player):
                                    raise BlockedAction(action, acting_player, None, testgame.players[savior])
                            else:
                                testgame.players[i].perform(action)
                    else:
                        if action == 'exchange':
                            testgame.players[i].perform(action, testgame.court_deck)
                        elif action == 'coup':
                            random_player = acting_player.select_opponent(testgame.players)
                            position, random_target = random_player.random_remaining_influence
                            testgame.players[i].perform(action, random_target)
                            random_player.remove_suspicion(str(random_target))
                        else:
                            testgame.players[i].perform(action)
                except (IllegalTarget, IllegalAction):
                    pass
                except BlockedAction:
                    break
                except RethinkAction as e:
                    print e.message
                else:
                    break
                    
                
        
if __name__ == "__main__":
    c = Counter()
    for _ in range(1000):
        c.update([simulations().test_gameplay_calculated_actions_calculated_targets_calculated_blocks_no_doubts(),])

    for i,v in c.most_common():
        print('{0}{1}'.format(i.ljust(25), v))
