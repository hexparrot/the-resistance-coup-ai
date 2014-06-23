class Player(object):
    def __init__(self):
        self.coins = 2
        self.left = None
        self.right = None

    def __str__(self):
        return ' '.join([str(self.left), str(self.right)])

    def income(self):
        self.coins += 1

    def foreign_aid(self):
        self.coins += 2

    def coup(self, inf_target):
        if self.coins >= 7:
            self.coins -= 7
            inf_target.reveal()
        else:
            raise RuntimeError("insufficient currency to coup")

    def perform(self, action, player_target=None):
        for inf in Influence.__subclasses__():
            if hasattr(inf, action):
                if player_target is None:
                    getattr(inf, action)(self)
                else:
                    getattr(inf, action)(self, player_target)
                break
        else:
            raise RuntimeError("no action %s" % action)

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
            raise RuntimeError("player already has no remaining influence")

class Influence(object):
    def __init__(self):
        self.revealed = False

    def reveal(self):
        self.revealed = True

    def __str__(self):
        return str(self.__class__.__name__)

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
            active_player.coins -= 3
            inf_target.reveal()
        else:
            raise RuntimeError("insufficient currency to assassinate")

class Ambassador(Influence):
    ACTIONS = ['exchange']
    BLOCKS = ['steal']
    
    @staticmethod
    def exchange(self):
        pass

class Contessa(Influence):
    ACTIONS = []
    BLOCKS = ['assassinate']

