"""
Python scripts to simulate the game "The Resistance: Coup designed by Rikki Tahta
The purpose of this project is to model human personalities and predict/score
behaviors and bluffs in order to win the game.

"""

__author__ = "William Dizon"
__license__ = "GNU GPL v3.0"
__version__ = "0.0.1"
__email__ = "wdchromium@gmail.com"

from coup import *
import pickle

class Coup_NN(object):
    DUEL_NETDUMP = None

    @staticmethod
    def game_winner(binary_input):
        influences = ['Ambassador', 'Assassin', 'Captain', 'Contessa', 'Duke']
        p = sorted(zip(binary_input, influences), reverse=True, key=lambda a: a[0])
        return ' '.join(sorted(inf for i,inf in p[0:2]))
      
    @staticmethod
    def train():
        from pybrain.tools.shortcuts import buildNetwork
        from pybrain import SigmoidLayer
        from pybrain.supervised.trainers.backprop import BackpropTrainer
        from pybrain.datasets import SupervisedDataSet
        from simulations import simulations
        '''from time import time
        #from collections import Counter'''
        
        PLAYERS = 2
        INPUT_NEURONS_PER_PLAYER = 5
        OUTPUT_NEURONS = 5
        HIDDEN_NEURONS = 5
    
        ds = SupervisedDataSet(PLAYERS * INPUT_NEURONS_PER_PLAYER, OUTPUT_NEURONS)
        net = buildNetwork(PLAYERS * INPUT_NEURONS_PER_PLAYER, HIDDEN_NEURONS, OUTPUT_NEURONS, bias=True, outputbias= True, hiddenclass=SigmoidLayer)
        trainer = BackpropTrainer(net, ds, learningrate= 0.1)
        WINS = []
        POSITIONS = []
        '''t0 = time()'''
    
        for _ in range(200):
            game_result = simulations.duel()
            WINS.append(game_result.winner.alpha)
            POSITIONS.append(game_result.influence_binary)
            ds.addSample(game_result.influence_binary, game_result.winner.influence_binary)        
    
        '''print "Time sampling {}".format(time()-t0)    
        
        #t1 = time()'''
        trainer.trainEpochs(50)
        '''print "Time training {}".format(time()-t1)
        
        norm_results = dict(Counter(WINS).most_common())
        nn_results = dict(Counter(game_winner(net.activate(p)) for p in POSITIONS).most_common())
    
        print ''.ljust(25), 'normal', 'nn'
        for pair in set(nn_results.keys() + norm_results.keys()):
            print pair.ljust(25), str(norm_results.get(pair,0)).ljust(6), str(nn_results.get(pair,0)).ljust(6)
        '''
            
        with open('nndump', 'w') as neunet:
            pickle.dump(net, neunet)
    
    @classmethod
    def predict_duel(cls, first_to_act, second_to_act):
        game_setup = Play_Coup(2)
        game_setup.players[0] = first_to_act
        game_setup.players[1] = second_to_act
        
        if not cls.DUEL_NETDUMP:
            with open('nndump', 'r') as neunet:
                cls.DUEL_NETDUMP = pickle.load(neunet)
        
        return game_winner(cls.DUEL_NETDUMP.activate(game_setup.influence_binary))
