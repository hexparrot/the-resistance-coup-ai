from pybrain.tools.shortcuts import buildNetwork
from pybrain import SigmoidLayer
from pybrain.supervised.trainers.backprop import BackpropTrainer
from pybrain.datasets import SupervisedDataSet
from time import time

from coup import *
from itertools import cycle
from heuristics import PERSONALITIES
from collections import Counter

PLAYERS = 5
GAMES = 200
INPUT_NEURONS_PER_PLAYER = 5
OUTPUT_NEURONS = 5
HIDDEN_NEURONS = 10
TRAINING_EPOCHS = 300

ds = SupervisedDataSet(PLAYERS * INPUT_NEURONS_PER_PLAYER, OUTPUT_NEURONS)
net = buildNetwork(PLAYERS * INPUT_NEURONS_PER_PLAYER, HIDDEN_NEURONS, OUTPUT_NEURONS, bias=True, outputbias=True, hiddenclass=SigmoidLayer)
trainer = BackpropTrainer(net, ds, learningrate= 0.1)

TRAINING_SET = []

for _ in range(GAMES):

    testgame = Play_Coup(PLAYERS, PERSONALITIES.keys())

    for acting_player in cycle(testgame.players):
        if not acting_player.influence_remaining:
            continue
        elif len(testgame) == 1:
            TRAINING_SET.append((testgame.playerstate_binary, acting_player.influence_binary))
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

for game_setup, winner in TRAINING_SET:
    ds.addSample(game_setup, winner)

t1 = time()
trainer.trainEpochs(TRAINING_EPOCHS)
print "Time PyBrain {}".format(time()-t1)

#PRINT RESULTS

def game_winner(binary_input):
    influences = ['Ambassador', 'Assassin', 'Captain', 'Contessa', 'Duke']
    
    p = sorted(zip(binary_input, influences), reverse=True, key=lambda a: a[0])
    return ' '.join(sorted(inf for i,inf in p[0:2]))

normal_ai = []
nn_ai = []

for game_setup, winner in TRAINING_SET:
    normal_ai.append(game_winner(winner))
    nn_ai.append(game_winner(net.activate(game_setup)))

norm = dict(Counter(normal_ai).most_common())
nn = dict(Counter(nn_ai).most_common())

print ''.ljust(25), 'normal', 'nn'
for pair in set(norm.keys() + nn.keys()):
    print pair.ljust(25), str(norm.get(pair,0)).ljust(6), str(nn.get(pair,0)).ljust(6)

