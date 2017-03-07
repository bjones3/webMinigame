import csv
import math


def get_config(debug_mode=False):
    config = {
        'plotPrice': 20,
        'plotMultiplier': 3,
        'field_height': 15,
        'field_width': 15,
        'max_seed_count': 20,
        'starting_resources': {
            'cash': 10,
            'fertilizer': 0,
            'grass': 0,
            'carrots': 0
        },
        'seeds': {},
        'firstSeed': 'a',
    }

    if debug_mode:
        config['starting_resources']['cash'] *= 1000

    with open('seed_data.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for seed in reader:
            seed['sellCost'] = int(seed['sellCost'])
            seed['seedYield'] = int(seed['seedYield'])
            seed['cashYield'] = int(seed['cashYield'])
            seed['carrotYield'] = int(seed['carrotYield'])
            seed['grassYield'] = int(seed['grassYield'])
            seed['fertilizerYield'] = int(seed['fertilizerYield'])
            seed['probability'] = float(seed['probability'])
            if debug_mode:
                seed['harvestTimeSeconds'] = math.ceil(int(seed['harvestTimeSeconds']) / 10.0)
            else:
                seed['harvestTimeSeconds'] = int(seed['harvestTimeSeconds'])
            seed_id = seed.pop('id')
            y = {}
            y.update({'seedYield': seed.pop('seedYield'), 'cashYield': seed.pop('cashYield'),
                      'carrotYield': seed.pop('carrotYield'), 'grassYield': seed.pop('grassYield'),
                      'fertilizerYield': seed.pop('fertilizerYield')})
            config['seeds'][seed_id] = seed
            config['seeds'][seed_id]['yield'] = y
    return config


def get_recipes():
    config = {'recipes': {}}

    with open('recipe_data.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for recipe in reader:
            recipe['cashCost'] = int(recipe['cashCost'])
            recipe['carrotsCost'] = int(recipe['carrotsCost'])
            recipe['grassCost'] = int(recipe['grassCost'])
            recipe['fertilizerCost'] = int(recipe['fertilizerCost'])
            recipe_id = recipe.pop('id')
            config['recipes'][recipe_id] = recipe
    return config
