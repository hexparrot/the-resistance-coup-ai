from pybrain.tools.shortcuts import buildNetwork
from pybrain import LinearLayer, SigmoidLayer, FeedForwardNetwork, FullConnection, BiasUnit, SoftmaxLayer
from pybrain.supervised.trainers.backprop import BackpropTrainer
from pybrain.structure.modules.tanhlayer import TanhLayer
from pybrain.datasets import SupervisedDataSet
from time import time

from coup import *

PLAYERS = 5

ds = SupervisedDataSet(PLAYERS * 5, 5)
net = buildNetwork(PLAYERS * 5, 10, 5, bias=True, outputbias= True, hiddenclass=SigmoidLayer)
trainer = BackpropTrainer(net, ds, learningrate= 0.1)

influences = ['Ambassador', 'Assassin', 'Captain', 'Contessa', 'Duke']



for _ in range(20):
    from itertools import cycle
    from random import random

    testgame = Play_Coup(PLAYERS)

    for i in cycle(range(PLAYERS)):
        acting_player = testgame.players[i]
        
        if not acting_player.influence_remaining:
            continue
        elif sum(1 for p in range(PLAYERS) if testgame.players[p].influence_remaining) == 1:
            gamestate = ([i in testgame.players[p] for i in influences for p in range(PLAYERS)])
            
            win_result = ('Ambassador' in acting_player,
                        'Assassin' in acting_player,
                        'Captain' in acting_player,
                        'Contessa' in acting_player,
                        'Duke' in acting_player)

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
trainer.trainEpochs(300)
print "Time PyBrain {}".format(time()-t1)

#PRINT RESULTS

def highest_positions(lst):
    highest = [i for i,v in enumerate(lst) if v == max(lst)][0]
    second = -float('infinity')
    for i in lst:
        if i > second and i != lst[highest]:
            second = i
    return highest, [i for i,v in enumerate(lst) if v == second][0]

made_up_game = {
    3: (1,0,1,0,0, 0,1,1,0,0, 0,0,1,0,1),
    4: (1,0,1,0,0, 0,1,1,0,0, 0,0,0,1,1, 0,0,1,0,1),
    5: (1,1,0,0,0, 1,0,1,0,0, 0,1,1,0,0, 0,0,0,1,1, 0,0,1,0,1),
    6: (1,1,0,0,0, 1,0,1,0,0, 0,1,1,0,0, 0,0,0,1,1, 0,0,1,0,1, 0,1,0,0,1)
    }

simulated_game = net.activate(made_up_game[PLAYERS])
highest = highest_positions(simulated_game)
print influences[highest[0]], influences[highest[1]] 
print simulated_game