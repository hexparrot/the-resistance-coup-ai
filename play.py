import random
from itertools import combinations, cycle
from collections import Counter
from coup import *

class Play_Coup(object):
    def __init__(self, players=5):
        self.players = {i:Player() for i in xrange(players)}
        
        self.court_deck = [Contessa() for _ in xrange(3)] + \
                          [Ambassador() for _ in xrange(3)] + \
                          [Duke() for _ in xrange(3)] + \
                          [Assassin() for _ in xrange(3)] + \
                          [Captain() for _ in xrange(3)]
        random.shuffle(self.court_deck)

        self.all_combinations = list(' '.join(sorted(x)) for x in combinations([str(a) for a in self.court_deck], 2))

        for p in xrange(players):
            self.players[p].left = self.court_deck.pop()
            self.players[p].right = self.court_deck.pop()

    def player_summary(self, player):
        print
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
    a = Play_Coup(PLAYERS)

    for i in cycle(xrange(PLAYERS)):
        print 'place in order:', i
        a.player_summary(i)
        action = raw_input('what would you like to do? ')

        try:
            a.players[i].perform(action)
        except TypeError:
            target = int(raw_input('whom will you target (#0-4)? '))
            a.players[i].perform(action, a.players[target])
        
        #print a.players[i].alpha, round(float(Counter(a.all_combinations)[a.players[i].alpha])/float(len(a.all_combinations)) * 100,2)
