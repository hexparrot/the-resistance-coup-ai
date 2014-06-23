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
    a = Play_Coup(PLAYERS)

    for i in cycle(xrange(PLAYERS)):

        if not a.players[i].influence_remaining:
            continue
        
        print 'place in order:', i
        a.player_summary(i)

        while 1:
            action = raw_input('what would you like to do? ')

            try:
                a.players[i].perform(action)
            except TypeError:
                try:
                    while 1:
                        try:
                            target = int(raw_input('whom will you target (#0-4)? '))
                            if action in ['assassinate', 'coup']:
                                position, influence = a.players[target].random_remaining_influence
                                a.players[i].perform(action, influence)
                            else:
                                a.players[i].perform(action, a.players[target])
                        except coup.IllegalTarget as e:
                            raise
                        else:
                            break
                except (coup.IllegalAction, coup.IllegalTarget) as e:
                    print e.message
                
                else:
                    break
            else:
                break
                    

        print
        print
        
        #print a.players[i].alpha, round(float(Counter(a.all_combinations)[a.players[i].alpha])/float(len(a.all_combinations)) * 100,2)
