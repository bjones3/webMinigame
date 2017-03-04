import csv
import math


def get_config(debug_mode=False):
    config = {
        'plotPrice': 20,
        'plotMultiplier': 3,
        'field_height': 15,
        'field_width': 15,
        'max_seed_count': 99,
        'starting_resources': {
            'cash': 10,
            'fertilizer': 0,
            'grass': 0,
            'carrots': 0
        },
        'seeds': {}
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
            if debug_mode:
                seed['harvestTimeSeconds'] = math.ceil(int(seed['harvestTimeSeconds']) / 10.0)
            else:
                seed['harvestTimeSeconds'] = int(seed['harvestTimeSeconds'])
            seed_id = seed.pop('id')
            config['seeds'][seed_id] = seed
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
