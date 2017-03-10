#!usr/bin/env python

from flask import Flask, render_template, request, jsonify
import json
import os
import re
import time
import psycopg2
import urlparse
import random
import copy
from werkzeug.exceptions import Forbidden, Unauthorized, BadRequest

import game_config


app = Flask(__name__)

if os.environ.get('DEBUG_MODE') == '1':
    DEBUG_MODE = True
else:
    DEBUG_MODE = False

GAME_CONFIG = game_config.get_config(DEBUG_MODE)
RECIPE_CONFIG = game_config.get_recipes()

conn = None


def get_conn():
    global conn
    if conn is None:
        urlparse.uses_netloc.append('postgres')
        db_url = os.environ['DATABASE_URL']
        url = urlparse.urlparse(db_url)
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
    return conn


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
                'unlockCount': 0,
                'seedCounts': {},
                'recipes': ['a']
            })
        return game_state.initialize()

    @classmethod
    def load(cls, slug, password):
        my_conn = get_conn()
        with my_conn:
            with my_conn.cursor() as cursor:
                cursor.execute('SELECT game_state FROM game_states WHERE slug = %s;', [slug])
                row = cursor.fetchone()
                if not row:
                    return None
                game_state = GameState(row[0])
                game_state.check_password(password)
                return game_state.initialize()

    def save(self, slug):
        my_conn = get_conn()
        json_game_state = json.dumps(self.data, indent=4)
        with my_conn:
            with my_conn.cursor() as cursor:
                cursor.execute('INSERT INTO game_states (slug, game_state) VALUES (%s, %s) '
                               'ON CONFLICT (slug) DO UPDATE SET game_state=%s;',
                               [slug, json_game_state, json_game_state])

    def initialize(self):
        for seed_id in GAME_CONFIG['seeds']:
            if self.data['seedCounts'].get(seed_id) is None:
                self.data['seedCounts'][seed_id] = 0
        for resource in GAME_CONFIG['starting_resources']:
            if self.data['resources'].get(resource) is None:
                self.data['resources'][resource] = GAME_CONFIG['starting_resources'][resource]
        for i in range(GAME_CONFIG['field_width']):
            for j in range(GAME_CONFIG['field_height']):
                if self.data.get('plot' + str(i) + '_' + str(j)) is None:
                    self.data['plot' + str(i) + '_' + str(j)] = {'seedType': 0, 'sowTime': 0, 'locked': 1}
        for i in range(2):
            for j in range(2):
                self.get_plot(i, j)['locked'] = 0
        return self

    def check_cash(self):
        total_seed_count = 0
        total_crops_planted = 0
        for seed_id in GAME_CONFIG['seeds']:
            total_seed_count += self.data['seedCounts'][seed_id]
        for i in range(GAME_CONFIG['field_width']):
            for j in range(GAME_CONFIG['field_height']):
                if self.has_planted_crop(i, j):
                    total_crops_planted += 1
        if total_seed_count == 0 and total_crops_planted == 0:
            if self.data['resources']['cash'] < RECIPE_CONFIG['recipes'][GAME_CONFIG['firstSeed']]['cashCost']:
                self.data['resources']['cash'] = RECIPE_CONFIG['recipes'][GAME_CONFIG['firstSeed']]['cashCost']

    def has_planted_crop(self, x, y):
        if self.get_plot(x, y)['seedType'] != 0:
            return True
        else:
            return False

    def get_plot(self, x, y):
        return self.data['plot' + str(x) + "_" + str(y)]

    def check_password(self, password):
        if password != self.data['password']:
            raise Unauthorized("Invalid password")

    def buy(self, recipe_id):
        recipe_data = RECIPE_CONFIG['recipes'][recipe_id]
        for resource in self.data['resources']:
            if self.data['resources'][resource] < recipe_data[resource + 'Cost']:
                message = "Not enough " + resource + " to buy a %s seed." % recipe_data['name']
                return message
            if self.data['seedCounts'][recipe_id] == GAME_CONFIG['max_seed_count']:
                message = "Can't buy any more %s seeds." % recipe_data['name']
                return message
            self.data['resources'][resource] -= recipe_data[resource + 'Cost']
        self.data['seedCounts'][recipe_id] += 1
        message = "Bought a %s seed." % recipe_data['name']
        return message

    def sell(self, seed_id):
        if self.data['seedCounts'][seed_id] <= 0:
            message = "No %s seeds to sell." % GAME_CONFIG['seeds'][seed_id]['name']
            return message
        self.data['seedCounts'][seed_id] -= 1
        self.data['resources']['cash'] += GAME_CONFIG['seeds'][seed_id]['sellCost']
        message = "Sold a %s seed." % GAME_CONFIG['seeds'][seed_id]['name']
        return message

    def sow(self, seed, x, y):
        if self.data['seedCounts'][seed] <= 0:
            message = "No %s seeds to plant." % GAME_CONFIG['seeds'][seed]['name']
            return message
        plot = self.get_plot(x, y)
        if self.has_planted_crop(x, y):
            message = "A %s seed is already planted here." % GAME_CONFIG['seeds'][seed]['name']
            return message
        self.data['seedCounts'][seed] -= 1
        plot['seedType'] = seed
        plot['sowTime'] = int(round(time.time() * 1000))
        message = "Planted a %s seed." % GAME_CONFIG['seeds'][seed]['name']
        return message

    def add_recipes(self):
        recipe_list = []
        for recipe_id in RECIPE_CONFIG['recipes']:
            recipe_list.append(recipe_id)
        for resource in GAME_CONFIG['starting_resources']:
            if self.data['resources'][resource] == 0:
                for recipe_id in RECIPE_CONFIG['recipes']:
                    if RECIPE_CONFIG['recipes'][recipe_id][resource + 'Cost'] > 0:
                        recipe_list.remove(recipe_id)
        for recipe_id in recipe_list:
            if recipe_id not in self.data['recipes']:
                self.data['recipes'].append(recipe_id)

    def is_known_recipe(self, recipe_id):
        if recipe_id in self.data['recipes']:
            return True
        else:
            return False

    def harvest(self, x, y):
        plot = self.get_plot(x, y)
        seed_type = plot['seedType']
        growing_time = int(round(time.time() - plot['sowTime'] / 1000))
        seed_data = GAME_CONFIG['seeds'].get(seed_type)
        if seed_data is None:
            raise Forbidden("Failed to harvest plot.")
        if seed_data['harvestTimeSeconds'] > growing_time:
            raise Forbidden("Failed to harvest plot.")

        seed_count = self.data['seedCounts'][seed_type]
        bonus = bonus_yield(seed_type)
        seed_count += seed_data['yield']['seedYield'] + bonus
        for resource in self.data['resources']:
            self.data['resources'][resource] += seed_data['yield'][resource + 'Yield']
        if seed_count > GAME_CONFIG['max_seed_count']:
            overflow = seed_count - GAME_CONFIG['max_seed_count']
            seed_count = GAME_CONFIG['max_seed_count']
            self.data['resources']['cash'] += seed_data['yield']['cashYield'] * overflow
        self.data['seedCounts'][seed_type] = seed_count
        plot['seedType'] = 0

        message = "Harvested a %s." % GAME_CONFIG['seeds'][seed_type]['name']
        if bonus == 1:
            message += ' Got 1 bonus seed!'
        if bonus > 1:
            message += ' Got %s bonus seeds!' % bonus
        return message

    def unlock(self, x, y):
        plot_price = GAME_CONFIG['plotPrice'] * GAME_CONFIG['plotMultiplier'] ** self.data['unlockCount']
        if self.data['resources']['cash'] < plot_price:
            message = "Not enough cash to unlock plot."
            return message
        plot = self.get_plot(x, y)
        plot['locked'] = 0
        self.data['resources']['cash'] -= plot_price
        self.data['unlockCount'] += 1
        message = "Unlocked plot for $%s." % plot_price
        return message


def get_leaderboard_data():
    my_conn = get_conn()
    with my_conn:
        with my_conn.cursor() as cursor:
            cursor.execute("SELECT slug, game_state->'resources'->'cash' AS cash, "
                           "game_state->'seedCounts'->'m' AS m FROM game_states "
                           "WHERE game_state->'resources'->'cash' IS NOT NULL "
                           "ORDER BY 2 DESC LIMIT 10;")
            result = cursor.fetchall()
            return result


def get_admin_data():
    data = {}
    my_conn = get_conn()
    with my_conn:
        with my_conn.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM game_states;')
            result = cursor.fetchone()
            data['game_count'] = result[0]

            cursor.execute('SELECT password FROM admin;')
            result = cursor.fetchone()
            data['password'] = result[0]
        return data


def make_response(game_state, message=None, recipes=None):
    response = {
        'state': game_state.get_client_data()
    }
    if message is not None:
        response['message'] = message
    if recipes is not None:
        response['recipes'] = recipes
    return jsonify(response)


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


def valid_chars(slug):
    regex = re.compile('^[a-z]+$')
    x = regex.match(slug)
    if x is False:
        raise BadRequest("Invalid characters")


@app.route('/')
def default():
    leaderboard_data = get_leaderboard_data()
    return render_template('defaultPage.html', leaderboard=leaderboard_data)


@app.route('/game/')
def game():
    return render_template('frontEndLayout.html', seeds=GAME_CONFIG['seeds'],
                           field_width=GAME_CONFIG['field_width'], field_height=GAME_CONFIG['field_height'])


@app.route('/admin/', methods=['GET'])
def admin_get():
    return render_template('admin_login.html')


@app.route('/admin/', methods=['POST'])
def admin_post():
    data = get_admin_data()
    if request.form['password'] != data['password']:
        return "Wrong password", 401
    return render_template('admin.html', data=get_admin_data(), recipes=RECIPE_CONFIG['recipes'], seeds=GAME_CONFIG['seeds'])


@app.route('/game-config')
def game_config():
    return jsonify(GAME_CONFIG)


@app.route('/game-state/<slug>', methods=['GET', 'POST'])
def state(slug):
    valid_chars(slug)
    body = request.json
    if body['newOrLoad'] == 'new':
        game_state = GameState.new(slug, body['password'])
    if body['newOrLoad'] == 'load':
        game_state = GameState.load(slug, body['password'])
    game_state.save(slug)
    return make_response(game_state)


@app.route('/action/buy', methods=['GET', 'POST'])
def buy():
    data = request.json  # data={slug,recipe_id,password}
    game_state = GameState.load(data['slug'], data['password'])
    message = game_state.buy(data['recipe_id'])
    game_state.save(data['slug'])
    return make_response(game_state, message)


@app.route('/action/sell', methods=['GET', 'POST'])
def sell():
    data = request.json  # data={slug,seed,password}
    game_state = GameState.load(data['slug'], data['password'])
    message = game_state.sell(data['seed'])
    game_state.check_cash()
    game_state.save(data['slug'])
    return make_response(game_state, message)


@app.route('/action/sow', methods=['GET', 'POST'])
def sow():
    data = request.json  # data={slug,seed,x,y,password}
    game_state = GameState.load(data['slug'], data['password'])
    message = game_state.sow(data['seed'], data['x'], data['y'])
    game_state.save(data['slug'])
    return make_response(game_state, message)


@app.route('/action/harvest', methods=['GET', 'POST'])
def harvest():
    data = request.json  # data={slug,x,y,password}
    game_state = GameState.load(data['slug'], data['password'])
    message = game_state.harvest(data['x'], data['y'])
    game_state.add_recipes()
    game_state.save(data['slug'])
    return make_response(game_state, message)


@app.route('/action/unlock', methods=['GET', 'POST'])
def unlock():
    data = request.json  # data={slug,x,y,password}
    game_state = GameState.load(data['slug'], data['password'])
    message = game_state.unlock(data['x'], data['y'])
    game_state.check_cash()
    game_state.save(data['slug'])
    return make_response(game_state, message)


@app.route('/recipe', methods=['POST'])
def recipe():
    data = request.json  # data={slug,password}
    game_state = GameState.load(data['slug'], data['password'])

    known_recipes = {}
    for recipe_id in RECIPE_CONFIG['recipes']:
        if game_state.is_known_recipe(recipe_id):
            known_recipes[recipe_id] = RECIPE_CONFIG['recipes'][recipe_id]
    return make_response(game_state, recipes=known_recipes)


@app.route('/styles.css')
def styles():
    return render_template('styles.css')


if __name__ == "__main__":
    app.run(debug=DEBUG_MODE, port=int(os.environ['PORT']), host='0.0.0.0')
