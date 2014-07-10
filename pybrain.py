from pybrain.tools.shortcuts import buildNetwork
from pybrain import LinearLayer, SigmoidLayer, FeedForwardNetwork, FullConnection, BiasUnit, SoftmaxLayer
from pybrain.supervised.trainers.backprop import BackpropTrainer
from pybrain.structure.modules.tanhlayer import TanhLayer
from pybrain.datasets import SupervisedDataSet
from time import time

from coup import *
from itertools import cycle
from random import random
from heuristics import PERSONALITIES

PLAYERS = 5
GAMES = 500
INPUT_NEURONS_PER_PLAYER = 5
OUTPUT_NEURONS = 5
HIDDEN_NEURONS = 5

ds = SupervisedDataSet(PLAYERS * INPUT_NEURONS_PER_PLAYER, OUTPUT_NEURONS)
net = buildNetwork(PLAYERS * INPUT_NEURONS_PER_PLAYER, HIDDEN_NEURONS, OUTPUT_NEURONS, bias=True, outputbias= True, hiddenclass=SigmoidLayer)
trainer = BackpropTrainer(net, ds, learningrate= 0.1)

influences = ['Ambassador', 'Assassin', 'Captain', 'Contessa', 'Duke']

for _ in range(GAMES):

    testgame = Play_Coup(PLAYERS, PERSONALITIES.keys())

    for acting_player in cycle(testgame.players):
        if not acting_player.influence_remaining:
            continue
        elif len(testgame) == 1:
            ds.addSample(testgame.playerstate_binary, acting_player.influence_binary)
            break
            
        action_plan = []
        remaining_opponent = None
        
        if len(testgame) == 2:
            remaining_opponent = acting_player.select_opponent(testgame.players)
            action_plan = acting_player.one_on_one_strategy(remaining_opponent.best_guess, True)
        
        while 1:
            try:
                if action_plan:
                    action = action_plan.pop(0)
                else:
                    action = acting_player.random_naive_priority()
                #print '{0} performing {1} (coins={2})'.format(acting_player.status, action, acting_player.coins)

                if action == 'income':
                    acting_player.perform(action)
                    break
                if action == 'tax':
                    acting_player.perform(action)
                    break
                elif action == 'coup':
                    random_player = acting_player.select_opponent(testgame.players) if not remaining_opponent else remaining_opponent
                    position, random_target = random_player.random_remaining_influence
                    acting_player.perform(action, random_target)
                    random_player.remove_suspicion(str(random_target))
                    break
                elif action == 'foreign_aid':
                    for savior in testgame.filter_out_players([acting_player]):
                        if savior.will_intervene(action, acting_player):
                            for spectators in testgame.filter_out_players([acting_player, savior]):
                                spectators.didnt_block_as['spectator'].extend([action])
                            raise BlockedAction(action, acting_player, None, savior)
                    else:
                        acting_player.perform(action)
                        break
                elif action == 'steal':
                    random_player = acting_player.select_opponent(testgame.players) if not remaining_opponent else remaining_opponent
                    if action in random_player.calculate('probable', 'blocks'):
                        raise RethinkAction(action, acting_player, random_player)
                    elif action in random_player.valid_blocks:
                        raise BlockedAction(action, acting_player, random_player, None)
                    else:
                        for savior in testgame.filter_out_players([acting_player, random_player]):
                            if savior.will_intervene(action, acting_player, random_player):
                                raise BlockedAction(action, acting_player, random_player, savior)
                                
                        for doubter in testgame.filter_out_players([acting_player]):
                            if doubter.will_callout(action, acting_player):
                                if action in acting_player.valid_blocks:
                                    acting_player.perform(action, random_player)
                                raise QuestionInfluence(action, acting_player, doubter)
                    
                        acting_player.perform(action, random_player)
                        for spectators in testgame.filter_out_players([acting_player, savior]):
                            spectators.didnt_block_as['spectator'].extend([action])
                        break
                elif action == 'assassinate':
                    random_player = acting_player.select_opponent(testgame.players) if not remaining_opponent else remaining_opponent
                    if action in random_player.calculate('probable', 'blocks'):
                        raise RethinkAction(action, acting_player, random_player)
                    elif action in random_player.valid_blocks:
                        raise BlockedAction(action, acting_player, random_player, None)
                    else:
                        for savior in testgame.filter_out_players([acting_player, random_player]):
                            if savior.will_intervene(action, acting_player, random_player):
                                raise BlockedAction(action, acting_player, random_player, savior)
                                
                        for doubter in testgame.filter_out_players([acting_player]):
                            if doubter.will_callout(action, acting_player):
                                if action in acting_player.valid_actions:
                                    position, random_target = random_player.random_remaining_influence
                                    acting_player.perform(action, random_target)
                                    random_player.remove_suspicion(str(random_target))
                                raise QuestionInfluence(action, acting_player, doubter)
                        position, random_target = random_player.random_remaining_influence
                        acting_player.perform(action, random_target)
                        random_player.remove_suspicion(str(random_target))
                        for spectators in testgame.filter_out_players([acting_player, random_player]):
                            spectators.didnt_block_as['spectator'].extend([action])
                        break
                elif action == 'exchange':
                    for doubter in testgame.filter_out_players([acting_player]):
                        if doubter.will_callout(action, acting_player):
                            if action in acting_player.valid_actions:
                                acting_player.perform(action, testgame.court_deck)
                            raise QuestionInfluence(action, acting_player, doubter)
                    break
            except IllegalAction as e:
                pass
            except IllegalTarget as e:
                pass
            except BlockedAction as e:
                break
            except RethinkAction as e:
                pass
            except QuestionInfluence as e:
                if e.performer_is_honest:
                    #will need refinement for captain/ambassador on blocked steal
                    if action in acting_player.left.ACTIONS and not acting_player.left.revealed:
                        acting_player.restore('left', testgame.court_deck)
                    elif action in acting_player.right.ACTIONS and not acting_player.right.revealed:
                        acting_player.restore('right', testgame.court_deck)
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