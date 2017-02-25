import csv
import math


def get_config(debug_mode=False):
    config = {
        'plotPrice': 20,
        'plotMultiplier': 3 ,
        'field_height': 15,
        'field_width': 15,
        'starting_resources': {
            'cash': 10
        },
        'seeds': {}
    }
    
    if debug_mode:
        config['starting_resources']['cash'] *= 100

    with open('seed_data.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for seed in reader:
            seed['buyCost'] = int(seed['buyCost'])
            seed['sellCost'] = int(seed['sellCost'])
            seed['harvestYield'] = int(seed['harvestYield'])
            if debug_mode:
                seed['harvestTimeSeconds'] = math.ceil(int(seed['harvestTimeSeconds']) / 10.0)
            else:
                seed['harvestTimeSeconds'] = int(seed['harvestTimeSeconds'])
            seed_id = seed.pop('id')
            config['seeds'][seed_id] = seed
    return config
