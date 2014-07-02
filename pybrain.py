from pybrain.tools.shortcuts import buildNetwork
from pybrain import LinearLayer, SigmoidLayer, FeedForwardNetwork, FullConnection, BiasUnit, SoftmaxLayer
from pybrain.supervised.trainers.backprop import BackpropTrainer
from pybrain.structure.modules.tanhlayer import TanhLayer
from pybrain.datasets import SupervisedDataSet
from time import time

from coup import *

ds = SupervisedDataSet(25,5 )
net = buildNetwork(25, 5, 5, bias=True, outputbias= True, hiddenclass=SigmoidLayer)
trainer = BackpropTrainer(net, ds, learningrate= 0.1)

for _ in range(200):
    from itertools import cycle
    from random import random

    PLAYERS = 5
    testgame = Play_Coup(PLAYERS)

    for i in cycle(range(PLAYERS)):
        acting_player = testgame.players[i]
        
        if not acting_player.influence_remaining:
            continue
        elif sum(1 for p in range(PLAYERS) if testgame.players[p].influence_remaining) == 1:
            gamestate = (testgame.players[0].influences('Ambassador'),
                        testgame.players[0].influences('Assassin'),
                        testgame.players[0].influences('Captain'),
                        testgame.players[0].influences('Contessa'),
                        testgame.players[0].influences('Duke'),

                        testgame.players[1].influences('Ambassador'),
                        testgame.players[1].influences('Assassin'),
                        testgame.players[1].influences('Captain'),
                        testgame.players[1].influences('Contessa'),
                        testgame.players[1].influences('Duke'),

                        testgame.players[2].influences('Ambassador'),
                        testgame.players[2].influences('Assassin'),
                        testgame.players[2].influences('Captain'),
                        testgame.players[2].influences('Contessa'),
                        testgame.players[2].influences('Duke'),

                        testgame.players[3].influences('Ambassador'),
                        testgame.players[3].influences('Assassin'),
                        testgame.players[3].influences('Captain'),
                        testgame.players[3].influences('Contessa'),
                        testgame.players[3].influences('Duke'),
                        
                        testgame.players[4].influences('Ambassador'),
                        testgame.players[4].influences('Assassin'),
                        testgame.players[4].influences('Captain'),
                        testgame.players[4].influences('Contessa'),
                        testgame.players[4].influences('Duke'))
            
            win_result = (testgame.players[i].influences('Ambassador'),
                        testgame.players[i].influences('Assassin'),
                        testgame.players[i].influences('Captain'),
                        testgame.players[i].influences('Contessa'),
                        testgame.players[i].influences('Duke'))

            ds.addSample(gamestate, win_result)
            break
        
        while 1:
            try:
                action = acting_player.random_naive_priority()

                if action == 'steal':
                    random_player = acting_player.select_opponent(testgame.players)
                    if (action in random_player.probable_blocks and random() > .24) or \
                        action in random_player.valid_blocks:
                        raise RethinkAction(action, acting_player, random_player)

                    for savior in testgame.filter_out_players([acting_player, random_player]):
                        if savior.will_intervene(action, acting_player, random_player):
                            raise BlockedAction(action, acting_player, random_player, savior)
                    else:
                        acting_player.perform(action, random_player)
                elif action == 'assassinate':
                    random_player = acting_player.select_opponent(testgame.players)
                    if (action in random_player.probable_blocks and random() > .24) or \
                        action in random_player.valid_blocks:
                        raise RethinkAction(action, acting_player, random_player)

                    for savior in testgame.filter_out_players([acting_player, random_player]):
                        if savior.will_intervene(action, acting_player, random_player):
                            raise BlockedAction(action, acting_player, random_player, savior)
                    else:
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                        random_player.remove_suspicion(str(random_target))
                elif action == 'foreign_aid':
                    for savior in testgame.filter_out_players([acting_player]):
                        if savior.will_intervene(action, acting_player):
                            raise BlockedAction(action, acting_player, None, savior)
                    else:
                        acting_player.perform(action)
                elif action == 'exchange':
                    acting_player.perform(action, testgame.court_deck)
                elif action == 'coup':
                    random_player = acting_player.select_opponent(testgame.players)
                    position, random_target = random_player.random_remaining_influence
                    acting_player.perform(action, random_target)
                    random_player.remove_suspicion(str(random_target))
                else:
                    acting_player.perform(action)
            except (IllegalTarget, IllegalAction):
                pass
            except BlockedAction:
                break
            except RethinkAction as e:
                pass
            except IndexError:
                break
            else:
                break



t1 = time()
trainer.trainEpochs(3000)
print "Time PyBrain {}".format(time()-t1)

#PRINT RESULTS

print net.activate( (1,1,0,0,0, 1,0,1,0,0, 0,1,1,0,0, 0,0,0,1,1, 0,0,1,0,1) )