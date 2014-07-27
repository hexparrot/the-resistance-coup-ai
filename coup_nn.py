"""
Python scripts to simulate the game "The Resistance: Coup designed by Rikki Tahta
The purpose of this project is to model human personalities and predict/score
behaviors and bluffs in order to win the game.

"""

from __future__ import print_function
from coup import *
import pickle

__author__ = "William Dizon"
__license__ = "GNU GPL v3.0"
__version__ = "0.0.1"
__email__ = "wdchromium@gmail.com"

class Coup_NN(object):
    NETS = {}

    def game_winner(self, binary_input):
        influences = ['Ambassador', 'Assassin', 'Captain', 'Contessa', 'Duke']
        p = sorted(zip(binary_input, influences), reverse=True, key=lambda a: a[0])
        return ' '.join(sorted(inf for i,inf in p[0:2]))
      
    def train(self, players=2, games=300, epochs=50, print_fitness=False):
        """
        nn = Coup_NN()
        nn.train(2, print_fitness=True)
        """
        from pybrain.tools.shortcuts import buildNetwork
        from pybrain import SigmoidLayer
        from pybrain.supervised.trainers.backprop import BackpropTrainer
        from pybrain.datasets import SupervisedDataSet
        from simulations import simulations
        from collections import Counter
        
        INPUT_NEURONS_PER_PLAYER = 5
        OUTPUT_NEURONS = 5
        HIDDEN_NEURONS = 10
    
        ds = SupervisedDataSet(players * INPUT_NEURONS_PER_PLAYER, OUTPUT_NEURONS)
        self.NETS[players] = buildNetwork(players * INPUT_NEURONS_PER_PLAYER, HIDDEN_NEURONS, OUTPUT_NEURONS, bias=True, outputbias= True, hiddenclass=SigmoidLayer)
        trainer = BackpropTrainer(self.NETS[players], ds, learningrate= 0.1)
        WINS = []
        POSITIONS = []
    
        for _ in range(games):
            game_result = simulations.duel(Play_Coup(2))
            WINS.append(game_result.winner.alpha)
            POSITIONS.append(game_result.influence_binary)
            ds.addSample(game_result.influence_binary, game_result.winner.influence_binary)        
    
        trainer.trainEpochs(epochs)

        if print_fitness:
            norm_results = dict(Counter(WINS).most_common())
            nn_results = dict(Counter(self.game_winner(self.NETS[players].activate(p)) for p in POSITIONS).most_common())
    
            print(''.ljust(25), 'normal', 'nn')
            for pair in set(nn_results.keys() + norm_results.keys()):
                print(pair.ljust(25), str(norm_results.get(pair,0)).ljust(6), str(nn_results.get(pair,0)).ljust(6))
            
        with open('coup_nn-{0}'.format(players), 'w') as neunet:
            pickle.dump(self.NETS[players], neunet)
    
    def predict_duel(self, first_to_act, second_to_act):
        game_setup = Play_Coup(2)
        game_setup.players[0] = first_to_act
        game_setup.players[1] = second_to_act
        
        try:
            if not self.NETS[2]:
                with open('coup_nn-2', 'r') as neunet:
                    self.NETS[2] = pickle.load(neunet)
        except (IOError, KeyError):
            self.train(2)
        
        return self.game_winner(self.NETS[2].activate(game_setup.influence_binary))
