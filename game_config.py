import csv
import math


def get_config(debug_mode=False):
    config = {
        'plotPrice': 20,
        'plotMultiplier': 3,
        'field_width': 15,
        'field_height': 15,
        'starting_field_width': 2,
        'starting_field_height': 2,
        'max_seed_count': 20,
        'starting_resources': {
            'cash': 10,
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
            seed['seed'] = int(seed['seed'])
            seed['cash'] = int(seed['cash'])
            seed['carrots'] = int(seed['carrots'])
            seed['grass'] = int(seed['grass'])
            seed['fertilizer'] = int(seed['fertilizer'])
            seed['probability'] = float(seed['probability'])
            if debug_mode:
                seed['harvestTimeSeconds'] = math.ceil(int(seed['harvestTimeSeconds']) / 10.0)
            else:
                seed['harvestTimeSeconds'] = int(seed['harvestTimeSeconds'])
            seed_id = seed.pop('id')
            y = {}
            y.update({'seed': seed.pop('seed'), 'cash': seed.pop('cash'),
                      'carrots': seed.pop('carrots'), 'grass': seed.pop('grass'),
                      'fertilizer': seed.pop('fertilizer')})
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
