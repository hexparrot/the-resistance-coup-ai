"""
Python scripts to simulate the game "The Resistance: Coup designed by Rikki Tahta
The purpose of this project is to model human personalities and predict/score
behaviors and bluffs in order to win the game.

"""
from __future__ import print_function
import numpy
from collections import defaultdict
from coup import *
from simulations import simulations

__author__ = "William Dizon"
__license__ = "GNU GPL v3.0"
__version__ = "0.0.1"
__email__ = "wdchromium@gmail.com"

SAMPLE_COUNT = 5
GAMES_PER_SAMPLE = 500

pairs = ['Ambassador Contessa',
     'Captain Duke',
     'Contessa Duke',
     'Ambassador Assassin',
     'Ambassador Captain',
     'Assassin Contessa',
     'Assassin Captain',
     'Assassin Duke',
     'Ambassador Duke',
     'Captain Contessa',
     'Duke Duke',
     'Ambassador Ambassador',
     'Contessa Contessa',
     'Captain Captain',
     'Assassin Assassin']
     
     
if __name__ == "__main__":
    from scipy.stats import f_oneway
    from statsmodels.stats.multicomp import pairwise_tukeyhsd, MultiComparison
    
    container = defaultdict(list)
    
    for index, sim in enumerate(simulations().available_simulations()):
        print("{0}: {1}".format(str(index).ljust(2), sim))
    
    for i in range(SAMPLE_COUNT):
        for sim in simulations().available_simulations():
            for p, wins in simulations().run(sim, GAMES_PER_SAMPLE).items():
                container[p].append((sim, wins))

    for pair in pairs:
        print('')
        print(pair)
        f, p = f_oneway(*[[i[1] for i in container[pair] if i[0] == sim] for sim in simulations().available_simulations()])
        print('F-stat: {0} at sig {1}: {2}'.format(str(round(f, 3)).ljust(7), 
                                                   str(round(p, 3)).ljust(7),
                                                   ['NULL','REJECT'][p <= .05]))
    
        if p <= .05:
            dta2 = numpy.rec.array(container[pair],  
                                dtype=[('test', '|S100'),
                                       ('wins', int)])
                                       
            print(pairwise_tukeyhsd(dta2['wins'], dta2['test']))

    
    
    
