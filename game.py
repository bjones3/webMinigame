import copy
import os
import random
import time
from werkzeug.exceptions import Forbidden, Unauthorized

import game_config
import db

if os.environ.get('DEBUG_MODE') == '1':
    DEBUG_MODE = True
else:
    DEBUG_MODE = False

GAME_CONFIG = game_config.get_config(DEBUG_MODE)
RECIPE_CONFIG = game_config.get_recipes()


class GameState(object):
    def __init__(self, json_data):
        self.data = json_data

    def get_client_data(self):
        c = copy.deepcopy(self.data)
        del c['password']
        return c

    @staticmethod
    def new(slug, password):
        game_state = GameState.load(slug, password)
        if game_state:
            raise Forbidden("Username already taken")
        else:
            game_state = GameState({
                'resources': {},
                'slug': slug,
                'password': password,
                'seedCounts': {GAME_CONFIG['firstSeed']: 0},
                'recipes': [GAME_CONFIG['firstSeed']],
                'plots': {}
            })
        return game_state.initialize()

    @classmethod
    def load(cls, slug, password):
        data = db.load(slug)
        if data is None:
            return
        game_state = GameState(data)
        game_state.check_password(password)
        return game_state.initialize()

    def initialize(self):
        for resource in GAME_CONFIG['starting_resources']:
            if self.data['resources'].get(resource) is None:
                self.data['resources'][resource] = GAME_CONFIG['starting_resources'][resource]
        # temp code for data migration of previous game_states
        if self.data.get('plots') is None:
            self.data['plots'] = {}
        if self.data.get('recipes') is None:
            self.data['recipes'] = []
        if 'unlockCount' in self.data:
            del self.data['unlockCount']
        for i in range(GAME_CONFIG['field_width']):
            for j in range(GAME_CONFIG['field_height']):
                if 'plot' + str(i) + '_' + str(j) in self.data:
                    if self.data['plot' + str(i) + '_' + str(j)]['locked'] == 0:
                        self.data['plots'][str(i) + '_' + str(j)] = {}
                        self.data['plots'][str(i) + '_' + str(j)]['seedType'] = self.data['plot' + str(i) + '_' + str(j)]['seedType']
                        self.data['plots'][str(i) + '_' + str(j)]['sowTime'] = self.data['plot' + str(i) + '_' + str(j)]['sowTime']
                    del self.data['plot' + str(i) + '_' + str(j)]
        # end temp
        for i in range(GAME_CONFIG['starting_field_width']):
            for j in range(GAME_CONFIG['starting_field_height']):
                if self.data['plots'].get(str(i) + '_' + str(j)) is None:
                    self.data['plots'][str(i) + '_' + str(j)] = {'seedType': 0, 'sowTime': 0}
        return self

    def check_cash(self):
        for seed_id in self.data['seedCounts']:
            if self.get_seed_count(seed_id) > 0:
                return
        for i in range(GAME_CONFIG['field_width']):
            for j in range(GAME_CONFIG['field_height']):
                if str(i) + '_' + str(j) in self.data['plots']:
                    if self.has_planted_crop(i, j):
                        return
        if self.data['resources']['cash'] < RECIPE_CONFIG['recipes'][GAME_CONFIG['firstSeed']]['cashCost']:
            self.data['resources']['cash'] = RECIPE_CONFIG['recipes'][GAME_CONFIG['firstSeed']]['cashCost']

    def has_planted_crop(self, x, y):
        if self.get_plot(x, y) is None:
            return False
        if self.get_plot(x, y)['seedType'] != 0:
            return True
        else:
            return False

    def get_plot(self, x, y):
        if str(x) + "_" + str(y) in self.data['plots']:
            return self.data['plots'][str(x) + "_" + str(y)]
        else:
            return None

    def get_seed_count(self, seed_id):
        if seed_id in self.data['seedCounts']:
            return self.data['seedCounts'][seed_id]
        else:
            return 0

    def check_password(self, password):
        if password != self.data['password']:
            raise Unauthorized("Invalid password")

    def buy(self, recipe_id):
        recipe_data = RECIPE_CONFIG['recipes'][recipe_id]
        for resource in self.data['resources']:
            if self.data['resources'][resource] < recipe_data[resource + 'Cost']:
                message = "Not enough " + resource + " to buy a %s seed." % recipe_data['name']
                return message
            if self.data['seedCounts'][recipe_id] >= GAME_CONFIG['max_seed_count']:
                message = "Can't buy any more %s seeds." % recipe_data['name']
                return message
            self.data['resources'][resource] -= recipe_data[resource + 'Cost']
        self.data['seedCounts'][recipe_id] += 1
        message = "Bought a %s seed." % recipe_data['name']
        return message

    def sell(self, seed_id):
        if self.get_seed_count(seed_id) <= 0:
            raise Forbidden("Failed to sell seed.")
        self.data['seedCounts'][seed_id] -= 1
        self.data['resources']['cash'] += GAME_CONFIG['seeds'][seed_id]['sellCost']
        message = "Sold a %s seed." % GAME_CONFIG['seeds'][seed_id]['name']
        return message

    def sow(self, seed, x, y):
        if self.get_seed_count(seed) <= 0:
            raise Forbidden("Failed to sow seed.")
        plot = self.get_plot(x, y)
        if plot is None:
            raise Forbidden("Failed to sow seed.")
        if self.has_planted_crop(x, y):
            raise Forbidden("Failed to sow seed.")
        self.data['seedCounts'][seed] -= 1
        plot['seedType'] = seed
        plot['sowTime'] = int(round(time.time() * 1000))
        message = "Planted a %s seed." % GAME_CONFIG['seeds'][seed]['name']
        return message

    def add_recipes(self):
        recipe_list = []
        for recipe_id in RECIPE_CONFIG['recipes']:
            recipe_list.append(recipe_id)
        for resource in ['cash', 'fertilizer', 'grass', 'carrots']:
            if resource not in self.data['resources'] or self.data['resources'][resource] == 0:
                for recipe_id in RECIPE_CONFIG['recipes']:
                    if RECIPE_CONFIG['recipes'][recipe_id][resource + 'Cost'] > 0:
                        recipe_list.remove(recipe_id)
        for recipe_id in recipe_list:
            if recipe_id not in self.data['recipes']:
                self.data['recipes'].append(recipe_id)
            seed_id = RECIPE_CONFIG['recipes'][recipe_id]['seed_id']
            if seed_id not in self.data['seedCounts']:
                self.data['seedCounts'][seed_id] = 0

    def is_known_recipe(self, recipe_id):
        if recipe_id in self.data['recipes']:
            return True
        else:
            return False

    def harvest(self, x, y):
        plot = self.get_plot(x, y)
        if plot is None:
            raise Forbidden("Failed to harvest plot.")
        seed_type = plot['seedType']
        growing_time = int(round(time.time() - plot['sowTime'] / 1000))
        seed_data = GAME_CONFIG['seeds'].get(seed_type)
        if seed_data is None:
            raise Forbidden("Failed to harvest plot.")
        if seed_data['harvestTimeSeconds'] > growing_time:
            raise Forbidden("Failed to harvest plot.")

        # Initialize resources user may be earning for the first time
        for yield_type, yield_count in seed_data['yield'].items():
            if yield_type != 'seed':
                if yield_count > 0:
                    if self.data['resources'].get(yield_type) is None:
                        self.data['resources'][yield_type] = 0

        seed_count = self.get_seed_count(seed_type)
        bonus = bonus_yield(seed_type)
        seed_count += seed_data['yield']['seed'] + bonus
        for resource in self.data['resources']:
            self.data['resources'][resource] += seed_data['yield'][resource]
        if seed_count > GAME_CONFIG['max_seed_count']:
            overflow = seed_count - GAME_CONFIG['max_seed_count']
            seed_count = GAME_CONFIG['max_seed_count']
            self.data['resources']['cash'] += seed_data['sellCost'] * overflow

        self.data['seedCounts'][seed_type] = seed_count
        plot['seedType'] = 0
        message = "Harvested a %s." % GAME_CONFIG['seeds'][seed_type]['name']
        if bonus == 1:
            message += ' Got 1 bonus seed!'
        if bonus > 1:
            message += ' Got %s bonus seeds!' % bonus
        return message

    def unlock(self, x, y):
        plot_price = GAME_CONFIG['plotPrice'] * GAME_CONFIG['plotMultiplier'] ** \
            (len(self.data['plots']) - GAME_CONFIG['starting_field_width'] * GAME_CONFIG['starting_field_height'])
        if self.data['resources']['cash'] < plot_price:
            message = "Not enough cash to unlock plot."
            return message
        self.data['plots'][str(x) + '_' + str(y)] = {'seedType': 0, 'sowTime': 0}
        self.data['resources']['cash'] -= plot_price
        message = "Unlocked plot for $%s." % plot_price
        return message


def generate(seed_id):
    x = random.random()
    if x < GAME_CONFIG['seeds'][seed_id]['probability']:
        return 1
    else:
        return 0


def bonus_yield(seed_id):
    bonus = 0
    while generate(seed_id) == 1:
        bonus += 1
    return bonus
