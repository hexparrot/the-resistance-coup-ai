PERSONALITIES = {
    'obnoxious': {
        'honest_intervention': {
            'foreign_aid': {
                'performer': lambda p: True
                },
            'assassinate': {
                'performer': lambda p: True,
                },
            'steal': {
                'performer': lambda p: p.coins + 2 >= 7,
                'victim': lambda v: v.coins < 3
                },
            'tax': {
                'performer': []
                }
            },
        'calculated_intervention': {
            'foreign_aid': {
                'performer': lambda p: False
                },
            'assassinate': {
                'performer': [],
                'victim': lambda v: v.influence_remaining == 2
                },
            'steal': {
                'performer': [],
                'victim': []
                },
            'tax': {
                'performer': lambda p: p.coins + 3 >= 3
                }
            },
        'outright_doubt': {
            'duke': {
                'action': ['tax'],
                'block': ['foreign_aid']
                },
            'ambassador': {
                'action': ['exchange'],
                'block': ['steal']
                },
            'contessa': {
                'action': [],
                'block': ['assassinate']
                },
            'captain': {
                'action': ['steal'],
                'block': ['steal']
                },
            'assassin': {
                'action': ['assassinate'],
                'block': []
                }
            }
        },
    'passive': {
        'honest_intervention': {},
        'calculated_intervention': {},
        'outright_doubt': {}
        }
    }
