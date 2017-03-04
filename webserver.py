#!usr/bin/env python

from flask import Flask, render_template, request, jsonify
import json, os, re, time
import psycopg2
import urlparse

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


# fetch game_state from postgres db
def load_state(slug):
    my_conn = get_conn()
    with my_conn:
        with my_conn.cursor() as cursor:
            cursor.execute('SELECT game_state FROM game_states WHERE slug = %s;',
                [slug])
            row = cursor.fetchone()
            if not row:
                return None
            game_state = row[0]
            return initialize_state(game_state)


def get_plot(game_state, x, y):
    return game_state['plot' + str(x) + "_" + str(y)]


# add missing seed counts, resources, and plots to game_state
# unlock first four plots
# check to never run out of money
def initialize_state(game_state):
    total_seed_count = 0
    total_crops_planted = 0
    for seed_id in GAME_CONFIG['seeds']:
        if game_state['seedCounts'].get(seed_id) is None:
            game_state['seedCounts'][seed_id] = 0
        total_seed_count += game_state['seedCounts'][seed_id]
    for resource in GAME_CONFIG['starting_resources']:
        if game_state['resources'].get(resource) is None:
            game_state['resources'][resource] = GAME_CONFIG['starting_resources'][resource]
    for i in range(GAME_CONFIG['field_width']):
        for j in range(GAME_CONFIG['field_height']):
            if game_state.get('plot' + str(i) + '_' + str(j)) is None:
                game_state['plot' + str(i) + '_' + str(j)] = {'seedType': 0, 'sowTime': 0, 'locked': 1}
            if get_plot(game_state, i, j)['seedType'] != 0:
                total_crops_planted += 1
    for i in range(2):
        for j in range(2):
            get_plot(game_state, i, j)['locked'] = 0
    if total_seed_count == 0 and total_crops_planted == 0:
        if game_state['resources']['cash'] < GAME_CONFIG['starting_resources']['cash']:
            game_state['resources']['cash'] = GAME_CONFIG['starting_resources']['cash']
    if game_state.get('recipes') is None:
        game_state['recipes'] = []
    return game_state


def save_state(slug, game_state):
    my_conn = get_conn()
    json_game_state = json.dumps(game_state, indent=4)
    with my_conn:
        with my_conn.cursor() as cursor:
            cursor.execute('INSERT INTO game_states (slug, game_state) VALUES (%s, %s) '
                           'ON CONFLICT (slug) DO UPDATE SET game_state=%s;',
                           [slug, json_game_state, json_game_state])

            
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
        'state': game_state
    }
    if message is not None:
        response['message'] = message
    if recipes is not None:
        response['recipes'] = recipes
    return jsonify(response)


@app.route('/')
def default():
    return render_template('defaultPage.html', leaderboard=get_leaderboard_data())


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
    return render_template('admin.html', data=get_admin_data())


@app.route('/game-config')
def game_config():
    return jsonify(GAME_CONFIG)


@app.route('/game-state/<slug>', methods=['GET', 'POST'])
def state(slug):
    regex = re.compile('^[a-z]+$')
    x = regex.match(slug)
    if x is False:
        raise Exception("Invalid characters")
    body = request.json
    password = body['password']
    game_state = load_state(slug)
    if game_state:
        if body['newOrLoad'] == 'new':
            return "Username already taken", 403
        if password == game_state['password']:
            return make_response(game_state)
        else:
            return "Invalid password", 401
    else:
        game_state = {
            'resources': {},
            'slug': slug,
            'password': password,
            'unlockCount': 0,
            'seedCounts': {},
            'recipes': ['a']
        }
        game_state = initialize_state(game_state)
        save_state(slug, game_state)
        return make_response(game_state)


@app.route('/action/buy', methods=['GET', 'POST'])
def buy():
    data = request.json  # data={slug,seed,password}
    game_state = load_state(data['slug'])

    # safety checks
    if data['password'] != game_state['password']:
        return "Invalid password", 401
    if game_state['resources']['cash'] < RECIPE_CONFIG['recipes'][data['seed']]['cashCost']:
        message = "Not enough cash to buy a %s seed." % GAME_CONFIG['seeds'][data['seed']]['name']
        return make_response(game_state, message)
    if game_state['resources']['carrots'] < RECIPE_CONFIG['recipes'][data['seed']]['carrotsCost']:
        message = "Not enough carrots to buy a %s seed." % GAME_CONFIG['seeds'][data['seed']]['name']
        return make_response(game_state, message)
    if game_state['resources']['grass'] < RECIPE_CONFIG['recipes'][data['seed']]['grassCost']:
        message = "Not enough grass to buy a %s seed." % GAME_CONFIG['seeds'][data['seed']]['name']
        return make_response(game_state, message)
    if game_state['resources']['fertilizer'] < RECIPE_CONFIG['recipes'][data['seed']]['fertilizerCost']:
        message = "Not enough fertilizer to buy a %s seed." % GAME_CONFIG['seeds'][data['seed']]['name']
        return make_response(game_state, message)
    if game_state['seedCounts'][data['seed']] == GAME_CONFIG['max_seed_count']:
        message = "Can't buy any more %s seeds." % GAME_CONFIG['seeds'][data['seed']]['name']
        return make_response(game_state, message)

    # update game_state
    game_state['seedCounts'][data['seed']] += 1
    game_state['resources']['cash'] -= RECIPE_CONFIG['recipes'][data['seed']]['cashCost']
    game_state['resources']['carrots'] -= RECIPE_CONFIG['recipes'][data['seed']]['carrotsCost']
    game_state['resources']['grass'] -= RECIPE_CONFIG['recipes'][data['seed']]['grassCost']
    game_state['resources']['fertilizer'] -= RECIPE_CONFIG['recipes'][data['seed']]['fertilizerCost']

    save_state(data['slug'], game_state)

    message = "Bought a %s seed." % GAME_CONFIG['seeds'][data['seed']]['name']
    return make_response(game_state, message)


@app.route('/action/sell', methods = ['GET', 'POST'])
def sell():
    data = request.json  # data={slug,seed,password}
    game_state = load_state(data['slug'])

    # safety checks
    if data['password'] != game_state['password']:
        return "Invalid password", 401
    if game_state['seedCounts'][data['seed']] <= 0:
        message = "No %s seeds to sell." % GAME_CONFIG['seeds'][data['seed']]['name']
        return make_response(game_state, message)

    # update game_state
    game_state['seedCounts'][data['seed']] -= 1
    game_state['resources']['cash'] += GAME_CONFIG['seeds'][data['seed']]['sellCost']

    initialize_state(game_state)  # no money check

    save_state(data['slug'], game_state)

    message = "Sold a %s seed." % GAME_CONFIG['seeds'][data['seed']]['name']
    return make_response(game_state, message)


@app.route('/action/sow', methods = ['GET', 'POST'])
def sow():
    data = request.json  # data={slug,seed,x,y,password}
    game_state = load_state(data['slug'])

    # safety checks
    if data['password'] != game_state['password']:
        return "Invalid password", 401
    if game_state['seedCounts'][data['seed']] <= 0:
        message = "No %s seeds to plant." % GAME_CONFIG['seeds'][data['seed']]['name']
        return make_response(game_state, message)
    plot = get_plot(game_state, data['x'], data['y'])
    if plot['seedType'] != 0:
        message = "A %s seed is already planted here." % GAME_CONFIG['seeds'][plot['seedType']]['name']
        return make_response(game_state, message)

    # update game_state
    game_state['seedCounts'][data['seed']] -= 1
    plot['seedType'] = data['seed']
    plot['sowTime'] = int(round(time.time() * 1000))

    save_state(data['slug'], game_state)

    message = "Planted a %s seed." % GAME_CONFIG['seeds'][data['seed']]['name']
    return make_response(game_state, message)


@app.route('/action/harvest', methods = ['GET', 'POST'])
def harvest():
    data = request.json  # data={slug,x,y,password}
    game_state = load_state(data['slug'])

    # safety checks
    if data['password'] != game_state['password']:
        return "Invalid password", 401
    plot = get_plot(game_state, data['x'], data['y'])
    seed_type = plot['seedType']
    growing_time = int(round(time.time() - plot['sowTime'] / 1000))
    seed_data = GAME_CONFIG['seeds'].get(seed_type)
    if seed_data is None:
        return "Failed to harvest plot.", 403
    if seed_data['harvestTimeSeconds'] > growing_time:
        return make_response(game_state, "no cheats >:(")

    # update game_state
    seed_count = game_state['seedCounts'][seed_type]
    seed_count += seed_data['seedYield']
    game_state['resources']['cash'] += seed_data['cashYield']
    game_state['resources']['carrots'] += seed_data['carrotYield']
    game_state['resources']['grass'] += seed_data['grassYield']
    game_state['resources']['fertilizer'] += seed_data['fertilizerYield']
    if seed_count > GAME_CONFIG['max_seed_count']:
        overflow = seed_count - GAME_CONFIG['max_seed_count']
        seed_count = GAME_CONFIG['max_seed_count']
        game_state['resources']['cash'] += seed_data['cashYield'] * overflow
    game_state['seedCounts'][seed_type] = seed_count
    plot['seedType'] = 0

    recipe_list = []
    for recipe_id in RECIPE_CONFIG['recipes']:
        recipe_list.append(recipe_id)
    for resource in GAME_CONFIG['starting_resources']:
        if game_state['resources'][resource] == 0:
            for recipe_id in RECIPE_CONFIG['recipes']:
                if RECIPE_CONFIG['recipes'][recipe_id][resource + 'Cost'] > 0:
                    recipe_list.remove(recipe_id)
    for recipe_id in recipe_list:
        if recipe_id not in game_state['recipes']:
            game_state['recipes'].append(recipe_id)

    save_state(data['slug'], game_state)

    message = "Harvested a %s." % GAME_CONFIG['seeds'][seed_type]['name']
    return make_response(game_state, message)


@app.route('/action/unlock', methods = ['GET', 'POST'])
def unlock():
    data = request.json  # data={slug,x,y,password}
    game_state = load_state(data['slug'])

    # safety checks
    if data['password'] != game_state['password']:
        return "Invalid password", 401
    plot_price = GAME_CONFIG['plotPrice'] * GAME_CONFIG['plotMultiplier'] ** game_state['unlockCount']
    if game_state['resources']['cash'] < plot_price:
        return make_response(game_state, "Not enough cash to unlock plot.")

    # making changes to game_state
    plot = get_plot(game_state, data['x'], data['y'])
    plot['locked'] = 0
    game_state['resources']['cash'] -= plot_price
    game_state['unlockCount'] += 1

    initialize_state(game_state)  # no money check

    save_state(data['slug'], game_state)

    message = "Unlocked plot for $%s." % plot_price
    return make_response(game_state, message)


@app.route('/recipe', methods = ['POST'])
def recipe():
    data = request.json  # data={slug}
    game_state = load_state(data['slug'])

    known_recipes = {}
    for recipe_id in RECIPE_CONFIG['recipes']:
        if recipe_id in game_state['recipes']:
            known_recipes[recipe_id] = RECIPE_CONFIG['recipes'][recipe_id]

    return make_response(game_state,recipes=known_recipes)


@app.route('/styles.css')
def styles():
    return render_template('styles.css')


if __name__ == "__main__":
    app.run(debug=DEBUG_MODE, port=int(os.environ['PORT']), host='0.0.0.0')