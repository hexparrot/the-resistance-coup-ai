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
    def test_gameplay_naive_actions_calculated_targets_selfish_blocks_no_doubts(self):
        """
        AI PROFILE:
        
        Action          Used        Targets     Blocked     
        income          yes
        foreign_aid     yes                     any available duke
        coup            yes
        steal           yes         anybody     victim only
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
                    action = acting_player.random_naive_priority()
                    if action == 'steal':
                        random_player = acting_player.select_opponent(testgame.players)
                        if 'steal' in random_player.valid_blocks:
                            raise BlockedAction("{0} blocks {1}'s ({2}) {3}".format(random_player.alpha,
                                                                                    acting_player.alpha,
                                                                                    i,
                                                                                    action))
                        else:
                            testgame.players[i].perform(action, random_player)
                    elif action == 'assassinate':
                        random_player = acting_player.select_opponent(testgame.players, [1]) or \
                                        acting_player.select_opponent(testgame.players)
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
                        random_player = acting_player.select_opponent(testgame.players, [1]) or \
                                        acting_player.select_opponent(testgame.players)
                        position, random_target = random_player.random_remaining_influence
                        testgame.players[i].perform(action, random_target)
                    else:
                        testgame.players[i].perform(action)
                    break
                except (IllegalTarget, IllegalAction):
                    pass
                except BlockedAction as e:
                    break
                
        
if __name__ == "__main__":
    c = Counter()
    for _ in range(1000):
        c.update([simulations().test_gameplay_naive_actions_calculated_targets_selfish_blocks_no_doubts(),])

    for i,v in c.most_common():
        print('{0}{1}'.format(i.ljust(25), v))
