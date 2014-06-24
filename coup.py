class Play_Coup(object):
    def __init__(self, players=5):
        from random import shuffle
        
        self.players = {i:Player() for i in xrange(players)}
        self.court_deck = [Contessa() for _ in xrange(3)] + \
                          [Ambassador() for _ in xrange(3)] + \
                          [Duke() for _ in xrange(3)] + \
                          [Assassin() for _ in xrange(3)] + \
                          [Captain() for _ in xrange(3)]
        
        shuffle(self.court_deck)

        for p in xrange(players):
            self.players[p].left = self.court_deck.pop()
            self.players[p].right = self.court_deck.pop()

class Player(object):
    def __init__(self):
        self.coins = 2
        self.left = None
        self.right = None

    def __str__(self):
        return '{0} {1}'.format(self.left, self.right)

    def perform(self, action, player_target=None):
        from itertools import chain
        
        for inf in chain([Influence,], Influence.__subclasses__()):
            if hasattr(inf, action):
                if player_target is None:
                    getattr(inf, action)(self)
                else:
                    getattr(inf, action)(self, player_target)
                break
        else:
            raise IllegalAction("no action %s" % action)

    @property
    def valid_actions(self):
        actions = set()
        if not self.left.revealed:
            actions.update(self.left.ACTIONS)
        if not self.right.revealed:
            actions.update(self.right.ACTIONS)
        return list(actions)

    @property
    def valid_blocks(self):
        blocks = set()
        if not self.left.revealed:
            blocks.update(self.left.BLOCKS)
        if not self.right.revealed:
            blocks.update(self.right.BLOCKS)
        return list(blocks)

    @property
    def alpha(self):
        return ' '.join(sorted([str(self.left), str(self.right)]))

    @property
    def status(self):
        return ' '.join([str(i) if not i.revealed else '<%s>' % str(i) for i in (self.left, self.right) ])

    @property
    def influence_remaining(self):
        return sum(1 for i in (self.left, self.right) if not i.revealed)

    @property
    def random_remaining_influence(self):
        if self.influence_remaining == 2:
            import random
            choice = random.choice(['left', 'right'])
            return (choice, getattr(self, choice))
        elif self.influence_remaining == 1:
            if self.left.revealed:
                return ('right', self.right)
            return ('left', self.left)
        else:
            raise IllegalTarget("player already has no remaining influence")

class Influence(object):
    def __init__(self):
        self.revealed = False

    def __str__(self):
        return str(self.__class__.__name__)

    def reveal(self):
        self.revealed = True

    @staticmethod
    def income(active_player):
        active_player.coins += 1

    @staticmethod
    def foreign_aid(active_player):
        active_player.coins += 2

    @staticmethod
    def coup(active_player, inf_target):
        if active_player.coins >= 7:
            active_player.coins -= 7
            inf_target.reveal()
        else:
            raise IllegalAction("insufficient currency to coup")

class Captain(Influence):
    ACTIONS = ['steal']
    BLOCKS = ['steal']
    
    @staticmethod
    def steal(active_player, player_target):
        if player_target.coins >= 2:
            player_target.coins -= 2
            active_player.coins += 2
        else:
            available_coins = player_target.coins
            player_target.coins -= available_coins
            active_player.coins += available_coins
        
class Duke(Influence):
    ACTIONS = ['tax']
    BLOCKS = ['foreign_aid']
    
    @staticmethod
    def tax(active_player):
        active_player.coins += 3

class Assassin(Influence):
    ACTIONS = ['assassinate']
    BLOCKS = []
    
    @staticmethod
    def assassinate(active_player, inf_target):
        if active_player.coins >= 3:
            if not inf_target.revealed:
                active_player.coins -= 3
                inf_target.reveal()
            else:
                raise IllegalTarget("influence target already eliminated")
        else:
            raise IllegalAction("insufficient currency to assassinate")

class Ambassador(Influence):
    ACTIONS = ['exchange']
    BLOCKS = ['steal']
    
    @staticmethod
    def exchange(self):
        pass

class Contessa(Influence):
    ACTIONS = []
    BLOCKS = ['assassinate']

class IllegalAction(Exception):
    pass

class IllegalTarget(Exception):
    pass
