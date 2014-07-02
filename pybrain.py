from pybrain.tools.shortcuts import buildNetwork
from pybrain import LinearLayer, SigmoidLayer, FeedForwardNetwork, FullConnection, BiasUnit, SoftmaxLayer
from pybrain.supervised.trainers.backprop import BackpropTrainer
from pybrain.structure.modules.tanhlayer import TanhLayer
from pybrain.datasets import SupervisedDataSet
from time import time

from coup import *
from itertools import cycle
from random import random

PLAYERS = 5
INPUT_NEURONS_PER_PLAYER = 5
OUTPUT_NEURONS = 5
HIDDEN_NEURONS = 5

ds = SupervisedDataSet(PLAYERS * INPUT_NEURONS_PER_PLAYER, OUTPUT_NEURONS)
net = buildNetwork(PLAYERS * INPUT_NEURONS_PER_PLAYER, HIDDEN_NEURONS, OUTPUT_NEURONS, bias=True, outputbias= True, hiddenclass=SigmoidLayer)
trainer = BackpropTrainer(net, ds, learningrate= 0.1)

influences = ['Ambassador', 'Assassin', 'Captain', 'Contessa', 'Duke']

for _ in range(200):

    testgame = Play_Coup(PLAYERS)

    for acting_player in cycle(testgame.players):
        if not acting_player.influence_remaining:
            continue
        
        try:
            acting_player.select_opponent(testgame.players)
        except IndexError:
            gamestate = ([i in p for i in influences for p in testgame.players])
            win_result = tuple(i in acting_player for i in influences)

            ds.addSample(gamestate, win_result)
            break
        
        while 1:
            try:
                random_player = acting_player.select_opponent(testgame.players)
                action = acting_player.random_naive_priority()

                if action == 'steal':
                    if (action in random_player.probable_blocks and random() > .24) or \
                        action in random_player.valid_blocks:
                        raise RethinkAction(action, acting_player, random_player)

                    for savior in testgame.filter_out_players([acting_player, random_player]):
                        if savior.will_intervene(action, acting_player, random_player):
                            raise BlockedAction(action, acting_player, random_player, savior)
                    else:
                        acting_player.perform(action, random_player)
                elif action == 'assassinate':
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
                    position, random_target = random_player.random_remaining_influence
                    acting_player.perform(action, random_target)
                    random_player.remove_suspicion(str(random_target))
                else:
                    acting_player.perform(action)
            except (IllegalTarget, IllegalAction):
                pass
            except BlockedAction:
                continue
            except RethinkAction as e:
                pass
            else:
                break



t1 = time()
trainer.trainEpochs(200)
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