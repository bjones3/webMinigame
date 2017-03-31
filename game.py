import copy
import os
import random
import time
from werkzeug.exceptions import Forbidden, Unauthorized

import rules
import db

if os.environ.get('DEBUG_MODE') == '1':
    DEBUG_MODE = True
else:
    DEBUG_MODE = False

CONFIG = rules.Config(DEBUG_MODE)


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
            first_recipe_id = CONFIG.general['firstRecipe']
            first_recipe_seed_id = CONFIG.recipes[first_recipe_id]['seedId']
            game_state = GameState({
                'resources': {},
                'slug': slug,
                'password': password,
                'seedCounts': {first_recipe_seed_id: 0},
                'recipes': [first_recipe_id],
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
        for resource in CONFIG.general['starting_resources']:
            if resource not in self.data['resources']:
                self.data['resources'][resource] = CONFIG.general['starting_resources'][resource]
        # temp code for data migration of previous game_states
        if self.data.get('plots') is None:
            self.data['plots'] = {}
        if self.data.get('recipes') is None:
            self.data['recipes'] = []
        if 'unlockCount' in self.data:
            del self.data['unlockCount']
        for i in range(CONFIG.general['field_width']):
            for j in range(CONFIG.general['field_height']):
                if 'plot' + str(i) + '_' + str(j) in self.data:
                    if self.data['plot' + str(i) + '_' + str(j)]['locked'] == 0:
                        self.data['plots'][str(i) + '_' + str(j)] = {}
                        self.data['plots'][str(i) + '_' + str(j)]['seedType'] = self.data['plot' + str(i) + '_' + str(j)]['seedType']
                        self.data['plots'][str(i) + '_' + str(j)]['sowTime'] = self.data['plot' + str(i) + '_' + str(j)]['sowTime']
                    del self.data['plot' + str(i) + '_' + str(j)]
                if self.data['plots'].get(str(i) + '_' + str(j)):
                    seed_type = self.data['plots'][str(i) + '_' + str(j)]['seedType']
                    if seed_type and seed_type not in CONFIG.seeds:
                        if len(seed_type) == 1:
                            new_seed = 'seed' + str(ord(seed_type) - ord('a'))
                            if new_seed in CONFIG.seeds:
                                self.data['plots'][str(i) + '_' + str(j)]['seedType'] = new_seed

        for seed_id in self.data['seedCounts']:
            if seed_id not in CONFIG.seeds and len(seed_id) == 1:
                new_seed = 'seed' + str(ord(seed_id) - ord('a'))
                if new_seed in CONFIG.seeds:
                    self.data['seedCounts'][new_seed] = self.data['seedCounts'].pop(seed_id)
        # end temp
        for i in range(CONFIG.general['starting_field_width']):
            for j in range(CONFIG.general['starting_field_height']):
                if self.data['plots'].get(str(i) + '_' + str(j)) is None:
                    self.data['plots'][str(i) + '_' + str(j)] = {'seedType': 0, 'sowTime': 0}
        return self

    def check_cash(self):
        for seed_id in self.data['seedCounts']:
            if self.get_seed_count(seed_id) > 0:
                return
        for i in range(CONFIG.general['field_width']):
            for j in range(CONFIG.general['field_height']):
                if str(i) + '_' + str(j) in self.data['plots']:
                    if self.has_planted_crop(i, j):
                        return

        first_recipe = CONFIG.recipes[CONFIG.general['firstRecipe']]
        for resource_id in first_recipe['cost']:
            if self.data['resources'].get(resource_id, 0) < first_recipe['cost'][resource_id]:
                self.data['resources'][resource_id] = first_recipe['cost'][resource_id]

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

    def get_resource_count(self, resource_id):
        if resource_id in self.data['resources']:
            return self.data['resources'][resource_id]
        else:
            return 0

    def get_seed_count(self, seed_id):
        if seed_id in self.data['seedCounts']:
            return self.data['seedCounts'][seed_id]
        else:
            return 0

    def check_password(self, password):
        if password != self.data['password']:
            raise Unauthorized("Invalid password")

    def buy(self, recipe_id):
        recipe_data = CONFIG.recipes[recipe_id]
        seed_id = recipe_data['seedId']
        for resource in recipe_data['cost']:
            if self.get_resource_count(resource) < recipe_data['cost'][resource]:
                resource_name = CONFIG.resources[resource]['name']
                message = "Not enough " + resource_name + " to buy a %s seed." % recipe_data['name']
                return message
            if self.get_seed_count(seed_id) >= CONFIG.general['max_seed_count']:
                message = "Can't buy any more %s seeds." % recipe_data['name']
                return message
            self.data['resources'][resource] -= recipe_data['cost'][resource]
        self.data['seedCounts'][seed_id] += 1
        message = "Bought a %s seed." % recipe_data['name']
        return message

    def sell(self, seed_id):
        if self.get_seed_count(seed_id) <= 0:
            raise Forbidden("Failed to sell seed.")
        self.data['seedCounts'][seed_id] -= 1
        self.data['resources'][CONFIG.CASH_RESOURCE] += CONFIG.seeds[seed_id]['sellCost']
        message = "Sold a %s seed." % CONFIG.seeds[seed_id]['name']
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
        message = "Planted a %s seed." % CONFIG.seeds[seed]['name']
        return message

    def add_recipes(self):
        recipe_list = []
        for recipe_id in CONFIG.recipes:
            recipe_list.append(recipe_id)
        for resource in CONFIG.resources:
            if self.get_resource_count(resource) == 0:
                for recipe_id in CONFIG.recipes:
                    if CONFIG.recipes[recipe_id]['cost'].get(resource, 0) > 0:
                        if recipe_id in recipe_list:
                            recipe_list.remove(recipe_id)
        for recipe_id in recipe_list:
            if recipe_id not in self.data['recipes']:
                self.data['recipes'].append(recipe_id)
            seed_id = CONFIG.recipes[recipe_id]['seedId']
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
        seed_data = CONFIG.seeds.get(seed_type)
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
        seed_count += seed_data['seed'] + bonus
        for resource in seed_data['yield']:
            self.data['resources'][resource] = self.get_resource_count(resource) + seed_data['yield'][resource]
        if seed_count > CONFIG.general['max_seed_count']:
            overflow = seed_count - CONFIG.general['max_seed_count']
            seed_count = CONFIG.general['max_seed_count']
            self.data['resources'][CONFIG.CASH_RESOURCE] += seed_data['sellCost'] * overflow

        self.data['seedCounts'][seed_type] = seed_count
        plot['seedType'] = 0
        message = "Harvested a %s." % CONFIG.seeds[seed_type]['name']
        if bonus == -1:
            message += ' Item was destroyed.'
        if bonus == 1:
            message += ' Got 1 bonus seed!'
        if bonus > 1:
            message += ' Got %s bonus seeds!' % bonus
        return message

    def unlock(self, x, y):
        plot_price = CONFIG.general['plotPrice'] * CONFIG.general['plotMultiplier'] ** \
            (len(self.data['plots']) - CONFIG.general['starting_field_width'] * CONFIG.general['starting_field_height'])
        if self.data['resources'][CONFIG.CASH_RESOURCE] < plot_price:
            message = "Not enough cash to unlock plot."
            return message
        self.data['plots'][str(x) + '_' + str(y)] = {'seedType': 0, 'sowTime': 0}
        self.data['resources'][CONFIG.CASH_RESOURCE] -= plot_price
        message = "Unlocked plot for $%s." % plot_price
        return message


def generate(seed_id):
    x = random.random()
    if x < CONFIG.seeds[seed_id]['probability']:
        return 1
    else:
        return 0


def bonus_yield(seed_id):
    # detrimental yield for certain seeds
    if CONFIG.seeds[seed_id]['name'] == 'Shovel' or CONFIG.seeds[seed_id]['name'] == 'Well':
        detriment = 0
        if generate(seed_id) == 1:
            detriment = -1
        return detriment
    bonus = 0
    while generate(seed_id) == 1:
        bonus += 1
    return bonus
