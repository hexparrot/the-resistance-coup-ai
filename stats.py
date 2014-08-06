"""
Python scripts to simulate the game "The Resistance: Coup designed by Rikki Tahta
The purpose of this project is to model human personalities and predict/score
behaviors and bluffs in order to win the game.

"""
from __future__ import print_function
import numpy
import simulations

__author__ = "William Dizon"
__license__ = "GNU GPL v3.0"
__version__ = "0.0.1"
__email__ = "wdchromium@gmail.com"

PLAYERS = 5
GAMES_PER_SAMPLE = 100
SIMULATION_TIMEOUT = 25

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

def f(sim):
    return (sim.__name__, simulations.run(sim, PLAYERS, GAMES_PER_SAMPLE))
    
if __name__ == "__main__":
    import sys
    import inspect
    from scipy.stats import f_oneway
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    from collections import defaultdict, Counter
    from multiprocessing.pool import Pool
    from itertools import cycle

    completed = []
    container = defaultdict(list)   
    pool = Pool()

    sim_list = [func for name,func in inspect.getmembers(simulations, inspect.isfunction) if name.startswith('sim_')]

    try:
        print('press CTRL-c to stop generating samples')
        it = pool.imap_unordered(f, cycle(sim_list))
        
        while 1:
            sim, result = it.next(timeout=SIMULATION_TIMEOUT)
            completed.append(sim)
            sys.stdout.write('.')
            for p, wins in result.items():
                container[p].append( (sim, wins) )
            
    except KeyboardInterrupt:
        pool.close()
        print('stopping all simulations...')
    finally:
        pool.terminate()
        pool.join()

    c = dict(Counter(completed).most_common())
    for idx, sim in enumerate([s.__name__ for s in sim_list]):
        print('Test: {0}, Iterations {1}, Heuristic: {2}'.format(idx, c[sim], sim))
        
    for pair in pairs:
        print('')
        print(pair)
        f, p = f_oneway(*[[i[1] for i in container[pair] if i[0] == sim] for sim in [s.__name__ for s in sim_list]])
        print('F-stat: {0} at sig {1}: {2}'.format(str(round(f, 3)).ljust(7), 
                                                   str(round(p, 3)).ljust(7),
                                                   ['NULL','REJECT'][p <= .05]))
    
        if p <= .05:
            dta2 = numpy.rec.array(container[pair],  
                                dtype=[('test', '|S100'),
                                       ('wins', int)])
                                       
            print(pairwise_tukeyhsd(dta2['wins'], dta2['test']))

    

    
