import csv

def get_config():
    config = {}
    config['starting_cash'] = 10
    config['field_size'] = (3, 3)
    config['seeds'] = {}
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
