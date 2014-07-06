"""
Python scripts to simulate the game "The Resistance: Coup designed by Rikki Tahta
The purpose of this project is to model human personalities and predict/score
behaviors and bluffs in order to win the game.

"""

__author__ = "William Dizon"
__license__ = "GNU GPL v3.0"
__version__ = "0.0.1"
__email__ = "wdchromium@gmail.com"

from collections import Counter, defaultdict
from random import choice, random
from coup import *
from simulations import simulations

SAMPLE_COUNT = 3
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
    from scipy.stats import f_oneway, ttest_rel
    
    results = {} 

    for sim in simulations.available_simulations():
        samples = defaultdict(list)
        for _ in range(SAMPLE_COUNT):
            for pair, wins in simulations().run(sim, GAMES_PER_SAMPLE).items():
                samples[pair].append(wins)
        results[sim] = samples

    print('ANOVA')
    for pair in pairs:
        f, p = f_oneway(*[results[sim][pair] for sim in simulations.available_simulations()])
        print('{0}{1} at sig {2}: {3}'.format(pair.ljust(25), 
                                              str(round(f, 3)).ljust(7), 
                                              str(round(p, 3)).ljust(7),
                                              ['NULL','REJECT'][p <= .05]))


    
    
    from itertools import combinations
    
    for sim_one, sim_two in combinations(simulations.available_simulations(), 2):
        print('t-test comparing')
        print sim_one
        print sim_two
        for pair in pairs:
            try:
                t, p = ttest_rel(results[sim_one][pair],
                                 results[sim_two][pair])
                print('{0}{1} at sig {2}: {3}'.format(pair.ljust(25), 
                                                      str(round(t, 3)).ljust(7), 
                                                      str(round(p, 3)).ljust(7),
                                                      ['NULL','REJECT'][p <= .05]))
            except ValueError:
                print('{0}: test failed due to no wins in one or more samples'.format(pair.ljust(25)))
    
