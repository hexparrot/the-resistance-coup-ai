from itertools import cycle
from collections import Counter
from coup import *

def player_summary(gamestate, player):
    print "***************"
    print "you are %s" % gamestate.players[player].status
    print "you have %s coins" % gamestate.players[player].coins
    print "you can truthfully perform:", ', '.join(gamestate.players[player].valid_actions)
    print
    print "all available actions:"
    print "income, foreign_aid, coup, steal, tax, assassinate, exchange"
    print

def play_game():
    PLAYERS = 5
    testgame = Play_Coup(PLAYERS)

    for i in cycle(xrange(PLAYERS)):
        if not testgame.players[i].influence_remaining:
            continue
        elif sum(1 for p in xrange(PLAYERS) if testgame.players[p].influence_remaining) == 1:
            break
        
        while 1:
            print 'place in order:', i
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
                print e.message

        print
        print

class simulations(object):
    def test_gameplay_random_actions_random_targets_block_all_no_doubts(self):
        """
        AI PROFILE:
        
        Action          Used        Targets     Blocked     
        income          yes
        foreign_aid     yes         random      any available duke
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

        for i in cycle(xrange(PLAYERS)):
            acting_player = testgame.players[i]
            
            if not acting_player.influence_remaining:
                continue
            elif sum(1 for p in xrange(PLAYERS) if testgame.players[p].influence_remaining) == 1:
                return testgame.players[i].alpha
            
            while 1:
                try:
                    action = choice(Play_Coup.ACTIONS['all'])
                    if action in Play_Coup.ACTIONS['blockable']:
                        for savior in xrange(PLAYERS):
                            if savior != i and action in testgame.players[savior].valid_blocks:
                                raise BlockedAction
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
        
if __name__ == "__main__":
    c = Counter()
    for _ in xrange(5000):
        c.update([simulations().test_gameplay_random_actions_random_targets_block_all_no_doubts(),])
    print c
