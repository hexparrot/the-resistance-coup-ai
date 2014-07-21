from pybrain.tools.shortcuts import buildNetwork
from pybrain import SigmoidLayer
from pybrain.supervised.trainers.backprop import BackpropTrainer
from pybrain.datasets import SupervisedDataSet
from time import time

import pickle
from coup import *
from heuristics import PERSONALITIES
from collections import Counter
from simulations import simulations

PLAYERS = 5
GAMES = 500
INPUT_NEURONS_PER_PLAYER = 5
OUTPUT_NEURONS = 5
HIDDEN_NEURONS = 15
TRAINING_EPOCHS = 200

ACTIVITY = 'train'

if ACTIVITY == 'train':
    ds = SupervisedDataSet(PLAYERS * INPUT_NEURONS_PER_PLAYER, OUTPUT_NEURONS)
    net = buildNetwork(PLAYERS * INPUT_NEURONS_PER_PLAYER, HIDDEN_NEURONS, OUTPUT_NEURONS, bias=True, outputbias=True, hiddenclass=SigmoidLayer)
    trainer = BackpropTrainer(net, ds, learningrate= 0.1)
    
    TRAINING_SET = []
    
    for _ in range(GAMES):
        testgame = simulations().sim_a_full_on_yomi()
        TRAINING_SET.append((testgame.playerstate_binary, testgame.winner))
        ds.addSample(testgame.playerstate_binary, testgame.winner.influence_binary)

    t1 = time()
    trainer.trainEpochs(TRAINING_EPOCHS)
    print "Time PyBrain {}".format(time()-t1)
    
    with open('nndump', 'w') as neunet:
        pickle.dump(net, neunet)
        
    normal_ai = []
    nn_ai = []
    
    for game_setup, winner in TRAINING_SET:
        normal_ai.append(winner.alpha)
        nn_ai.append(game_winner(net.activate(game_setup)))
    
    norm = dict(Counter(normal_ai).most_common())
    nn = dict(Counter(nn_ai).most_common())
    
    print ''.ljust(25), 'normal', 'nn'
    for pair in set(norm.keys() + nn.keys()):
        print pair.ljust(25), str(norm.get(pair,0)).ljust(6), str(nn.get(pair,0)).ljust(6)
    
elif ACTIVITY == 'sim':
    TRAINING_SET = []
    
    for _ in range(GAMES):
        testgame = Play_Coup(PLAYERS, PERSONALITIES.keys())
        TRAINING_SET.append(testgame.playerstate_binary)

    with open('nndump', 'r') as neunet:
        net = pickle.load(neunet)
        
    nn_ai = []
        
    for game_setup in TRAINING_SET:
        nn_ai.append(game_winner(net.activate(game_setup)))
        
    nn = dict(Counter(nn_ai).most_common())
    
    print ''.ljust(25), 'nn'
    for pair in nn.keys():
        print pair.ljust(25), str(nn.get(pair,0)).ljust(6)

