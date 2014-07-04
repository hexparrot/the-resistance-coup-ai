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
    
    SAMPLE_COUNT = 3
    GAMES_PER_SAMPLE = 200

    sims = [method for method in dir(simulations) if callable(getattr(simulations, method)) and not method.startswith('_')]

    from scipy.stats import f_oneway, ttest_rel
    
    results = {} 

    for sim in sims:
        samples = defaultdict(list)
        for _ in range(SAMPLE_COUNT):
            for pair, wins in simulations()._run_simulation(sim, GAMES_PER_SAMPLE).items():
                samples[pair].append(wins)
        results[sim] = samples

    print('ANOVA')
    for pair in pairs:
        f, p = f_oneway(*[results[sim][pair] for sim in sims])
        print('{0}{1} at sig {2}: {3}'.format(pair.ljust(25), 
                                              str(round(f, 3)).ljust(7), 
                                              str(round(p, 3)).ljust(7),
                                              ['NULL','REJECT'][p <= .05]))

    print('\n')
    print('t-test')
    for pair in pairs:
        try:
            t, p = ttest_rel(results['random_actions_random_targets_no_blocking'][pair],
                             results['random_actions_random_targets_selfish_blocks_no_doubts'][pair])
            print('{0}{1} at sig {2}: {3}'.format(pair.ljust(25), 
                                                  str(round(t, 3)).ljust(7), 
                                                  str(round(p, 3)).ljust(7),
                                                  ['NULL','REJECT'][p <= .05]))
        except ValueError:
            print('{0}: test failed due to no wins in {1} samples'.format(pair.ljust(25), SAMPLE_COUNT))
                         
