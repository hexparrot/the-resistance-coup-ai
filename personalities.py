PERSONALITIES = {
    'obnoxious': {
        'honest_intervention': {
            'foreign_aid': {
                'performer': lambda p: True
                },
            'assassinate': {
                'performer': lambda p: True,
                'victim': lambda v: v.coins < 7
                },
            'steal': {
                'performer': lambda p: True
                }
            },
        'calculated_intervention': {},
        },
    'cautious': {
        'honest_intervention': {
            'foreign_aid': {
                'performer': lambda p: True
                },
            'assassinate': {
                'performer': False
                },
            'steal': {
                'performer': lambda p: True
                }
            },
        'calculated_intervention': {}
        },
    'passive': {
        'honest_intervention': {},
        'calculated_intervention': {},
        'outright_doubt': {}
        }
    }
