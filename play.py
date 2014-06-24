import coup
from itertools import cycle
from collections import Counter

def player_summary(gamestate, player):
    print "***************"
    print "you are %s" % gamestate.players[player].status
    print "you have %s coins" % gamestate.players[player].coins
    print "you can truthfully perform:", ', '.join(gamestate.players[player].valid_actions)
    print
    print "all available actions:"
    print "income, foreign_aid, coup, steal, tax, assassinate, exchange"
    print

if __name__ == "__main__":
    PLAYERS = 5
    testgame = coup.Play_Coup(PLAYERS)

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
                if action in coup.Play_Coup.ACTIONS['targets_influence']:
                    player_target = int(raw_input('whom will you target (#0-4)? '))
                    position, random_target = testgame.players[player_target].random_remaining_influence
                    testgame.players[i].perform(action, random_target)
                elif action in coup.Play_Coup.ACTIONS['targets_player']:
                    player_target = int(raw_input('whom will you target (#0-4)? '))
                    testgame.players[i].perform(action, testgame.players[player_target])
                else:
                    testgame.players[i].perform(action)
                break
            except (coup.IllegalTarget, coup.IllegalAction) as e:
                print e.message

        print
        print
        
