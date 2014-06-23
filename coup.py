class Player(object):
    def __init__(self):
        self.coins = 2
        self.left = None
        self.right = None

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
    def influence_remaining(self):
        return sum(1 for i in (self.left, self.right) if not i.revealed)

class Influence(object):
    def __init__(self):
        self.revealed = False

    def reveal(self):
        self.revealed = True

class Captain(Influence):
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
    @staticmethod
    def tax(active_player):
        active_player.coins += 3

class Assassin(Influence):
    @staticmethod
    def assassinate(active_player, player_target):
        if active_player.coins >= 3:
            active_player.coins -= 3
            player_target.left.reveal()
        else:
            raise RuntimeError("insufficient currency to assassinate")

class Ambassador(Influence):
    @staticmethod
    def exchange(self):
        pass

class Contessa(Influence):
    pass
