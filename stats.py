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

SAMPLE_COUNT = 5
GAMES_PER_SAMPLE = 100

    
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


    

    container = defaultdict(list)
    
    for i in range(SAMPLE_COUNT):
        for p, wins in simulations().run('sim_random_actions_random_targets_no_blocking', GAMES_PER_SAMPLE).items():
            container[p].append(('random_all', wins))
        for p, wins in simulations().run('sim_random_actions_random_targets_selfish_blocks_no_doubts', GAMES_PER_SAMPLE).items():
            container[p].append(('random_selfish', wins))
        for p, wins in simulations().run('sim_naive_actions_calculated_targets_selfish_blocks_no_doubts', GAMES_PER_SAMPLE).items():
            container[p].append(('naive', wins))
        for p, wins in simulations().run('sim_naive_actions_calculated_targets_calculated_blocks_no_doubts', GAMES_PER_SAMPLE).items():
            container[p].append(('naive_calc', wins))
        for p, wins in simulations().run('sim_calculated_actions_calculated_targets_more_calculated_blocks_no_doubts', GAMES_PER_SAMPLE).items():
            container[p].append(('calc', wins))
    
    dta2 = np.rec.array(container['Contessa Duke'],  
                        dtype=[('test', '|S20'),
                               ('wins', int)])
                               
    

    res2 = pairwise_tukeyhsd(dta2['wins'], dta2['test'])
    print res2

    mod = MultiComparison(dta2['wins'], dta2['test'])
    print mod.tukeyhsd()

    
    
    
