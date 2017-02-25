import csv


def get_config():
    config = {
        'plotPrice': 20,
        'plotMultiplier': 3 ,
        'field_height': 5,
        'field_width': 5,
        'starting_resources': {
            'cash': 10},
        'seeds': {}
    }

    with open('seed_data.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for seed in reader:
            seed['buyCost'] = int(seed['buyCost'])
            seed['sellCost'] = int(seed['sellCost'])
            seed['harvestYield'] = int(seed['harvestYield'])
            seed['harvestTimeSeconds'] = int(seed['harvestTimeSeconds'])
            seed_id = seed.pop('id')
            config['seeds'][seed_id] = seed
    return config
