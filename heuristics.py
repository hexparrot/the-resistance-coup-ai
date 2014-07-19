from random import random

PERSONALITIES = {
    'obnoxious': {
        'honest_intervention': {
            'foreign_aid': {
                'performer': lambda p: random() > .5
                },
            'assassinate': {
                'performer': lambda p: random() > .5,
                'victim': lambda v: v.coins < 7
                },
            'steal': {
                'performer': lambda p: random() > .5
                }
            },
        'calculated_intervention': {
            'foreign_aid': {
                'performer': lambda p: random() > .8
                },
            },
        'callout': {
            'threshold': 0,
            'min_actions': 3,
            'min_inactions': 3,
            'plays_numbers': True
            }
        },
    'cautious': {
        'honest_intervention': {
            'foreign_aid': {
                'performer': lambda p: random() > .7
                },
            'assassinate': {
                'performer': lambda p: False
                },
            'steal': {
                'performer': lambda p: random() > .7
                }
            },
        'calculated_intervention': {},
        'callout': {
            'threshold': -3,
            'min_actions': 3,
            'min_inactions': 3,
            'plays_numbers': False
            }
        },
    'passive': {
        'honest_intervention': {},
        'calculated_intervention': {},
        'callout': {}
        }
    }

"""
The following dictionaries indicate what information
is implied or suggested by performing certain actions.

For example, PERFORMED_ACTION: somebody who steals, suggests being a Captain
BLOCKED ACTION: somebody who blocks a foreign aid suggests being a Duke
BETTER_ALTERNATIVE: somebody who incomes is likely not a Duke
"""

IMPLIED_INFORMATION = {
    'perform': {
        'steal': ['Captain'],
        'tax': ['Duke'],
        'assassinate': ['Assassin'],
        },
    'block': {
        'foreign_aid': ['Duke'],
        'steal': ['Ambassador', 'Captain'],
        'assassinate': ['Contessa']
        },
    'suboptimal_move': {
        'foreign_aid': ['Duke'],
        'income': ['Duke'],
        'coup': ['Assassin']
        }
    }
    
"""
The following dictionaries weigh in how much a given action should suggest
a player controls an influence.

For example:
performed_action = 1, if a captain steals, +1 to "is a captain"
blocked_selfishly = 1, if a captain blocks a steal on himself, +1 to 'is a captain/ambassador'
blocked_selflessly = if a captain blocks a steal he is not the target of, +2 to "must really be a captain"

These must be integers
"""

WEIGHTS = {
    'performed_action': 1,
    'blocked_selfishly': 1,
    'blocked_selflessly': 6,
    'suboptimal_move': -3, #income when could have taxed, -x to likelihood of duke
    'didnt_block_selfishly': -10, #eg allowed somebody to steal from him, but was captain/ambass
    'didnt_block_selflessly': -1 #didnt block a foreign aid, for example
    }
    
    
    