import random
import coup
from itertools import combinations, cycle
from collections import Counter


class Play_Coup(object):
    def __init__(self, players=5):
        self.players = {i:coup.Player() for i in xrange(players)}
        
        self.court_deck = [coup.Contessa() for _ in xrange(3)] + \
                          [coup.Ambassador() for _ in xrange(3)] + \
                          [coup.Duke() for _ in xrange(3)] + \
                          [coup.Assassin() for _ in xrange(3)] + \
                          [coup.Captain() for _ in xrange(3)]
        random.shuffle(self.court_deck)

        self.all_combinations = list(' '.join(sorted(x)) for x in combinations([str(a) for a in self.court_deck], 2))

        for p in xrange(players):
            self.players[p].left = self.court_deck.pop()
            self.players[p].right = self.court_deck.pop()

    def player_summary(self, player):
        print "***************"
        print "you are %s" % self.players[player].status
        print "you have %s coins" % self.players[player].coins
        print "you can truthfully perform:", ', '.join(self.players[player].valid_actions)
        print
        print "all available actions:"
        print "income, foreign_aid, coup, steal, tax, assassinate, exchange"
        print

if __name__ == "__main__":
    PLAYERS = 5
    testgame = Play_Coup(PLAYERS)

    for i in cycle(xrange(PLAYERS)):
        if not testgame.players[i].influence_remaining:
            continue
        elif sum(1 for p in xrange(PLAYERS) if testgame.players[p].influence_remaining) == 1:
            break
        
        while 1:
            print 'place in order:', i
            testgame.player_summary(i)
            
            try:
                action = raw_input('what would you like to do? ')
                if action in ['coup', 'assassinate']:
                    player_target = int(raw_input('whom will you target (#0-4)? '))
                    position, random_target = testgame.players[player_target].random_remaining_influence
                    testgame.players[i].perform(action, random_target)
                elif action in ['steal']:
                    player_target = int(raw_input('whom will you target (#0-4)? '))
                    testgame.players[i].perform(action, testgame.players[player_target])
                else:
                    testgame.players[i].perform(action)
                break
            except (coup.IllegalTarget, coup.IllegalAction):
                pass

        print
        print
        
        #print a.players[i].alpha, round(float(Counter(a.all_combinations)[a.players[i].alpha])/float(len(a.all_combinations)) * 100,2)
