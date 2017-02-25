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
          
conn = None


def get_conn():
    global conn
    if conn is None:
        urlparse.uses_netloc.append("postgres")
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


def load_state(slug):
    my_conn = get_conn()
    with my_conn:
        with my_conn.cursor() as cursor:
            cursor.execute("SELECT game_state FROM game_states WHERE slug = %s;",
                           [slug])
            row = cursor.fetchone()
            if not row:
                return None
            return row[0]


def initialize_state(game_state):
    for seed_id in GAME_CONFIG['seeds']:
        if game_state['seedCounts'].get(seed_id) is None:
            game_state['seedCounts'][seed_id] = 0
    for resource in GAME_CONFIG['starting_resources']:
        if game_state['resources'].get(resource) is None:
            game_state['resources'][resource] = GAME_CONFIG['starting_resources'][resource]

    for i in range(GAME_CONFIG['field_width']):
        for j in range(GAME_CONFIG['field_height']):
            if game_state.get("plot" + str(i) + "," + str(j)) is None:
                game_state["plot" + str(i) + "," + str(j)] = {'seedType': 0, 'sowTime': 0, 'locked': 1}
    for i in range(2):
        for j in range(2):
            game_state[("plot" + str(i) + "," + str(j))]['locked'] = 0


def save_state(slug, game_state):
    my_conn = get_conn()
    json_game_state = json.dumps(game_state, indent=4)
    with my_conn:
        with my_conn.cursor() as cursor:
            cursor.execute("INSERT INTO game_states (slug, game_state) VALUES (%s, %s) ON CONFLICT (slug) DO UPDATE SET game_state=%s;",
                           [slug, json_game_state, json_game_state])

            
def get_leaderboard_data():
    my_conn = get_conn()
    with my_conn:
        with my_conn.cursor() as cursor:
            cursor.execute("SELECT slug, game_state->'cash' AS cash, game_state->'m' AS m FROM game_states ORDER BY 2 DESC LIMIT 10;")
            return cursor.fetchall()


def get_plot(game_state, x, y):
    return game_state["plot" + str(x) + "," + str(y)]


@app.route('/')
def default():
    return render_template('defaultPage.html', leaderboard=get_leaderboard_data())


@app.route('/game/')
def game():
    return render_template('frontEndLayout.html', seeds = GAME_CONFIG['seeds'], field_width = GAME_CONFIG['field_width'],
                           field_height = GAME_CONFIG['field_height'])


@app.route('/game-config')
def game_config():
    return jsonify(GAME_CONFIG)


@app.route('/game-state/<slug>', methods = ['GET', 'POST'])
def state(slug):
    regex = re.compile("^[a-z]+$")
    x = regex.match(slug)
    if x is False:
        raise Exception("Invalid characters")
    body = request.json
    password = body['password']
    data = load_state(slug)
    if data:
        if body['newOrLoad'] == "new":
            return "Username already taken", 403
        if password == data['password']:
            initialize_state(data)
            return jsonify(data)
        else:
            return "Invalid password", 401
    else:
        game_state = {
            'resources': {},
            'slug': slug,
            'password': password,
            'unlockCount': 0,
            'seedCounts': {}
        }

        initialize_state(game_state)
        save_state(slug, game_state)
        if password == game_state['password']:
            return jsonify(game_state)
        else:
            raise Exception("Invalid password")


@app.route('/action/buy', methods = ['GET', 'POST'])
def buy():
    # requesting buy action data from script (seed, slug)
    buy_data = request.json

    # loading game_state
    game_state = load_state(buy_data['slug'])

    if buy_data['password'] != game_state['password']:
        raise Exception("Invalid password")

    # safety check
    if game_state['resources']['cash'] < GAME_CONFIG['seeds'][buy_data['seed']]['buyCost']:
        raise Exception("Not enough cash.")

    # making changes to game_state
    game_state['seedCounts'][buy_data['seed']] += 1
    game_state['resources']['cash'] -= GAME_CONFIG['seeds'][buy_data['seed']]['buyCost']

    # saving new game_state
    save_state(buy_data['slug'], game_state)

    return jsonify(game_state)


@app.route('/action/sell', methods = ['GET', 'POST'])
def sell():
    # requesting sell action data from script (seed, slug)
    data = request.json

    # loading game_state
    game_state = load_state(data['slug'])

    if data['password'] != game_state['password']:
        raise Exception("Invalid password")

    # safety check
    if game_state['seedCounts'][data['seed']] <= 0:
        raise Exception("No " + GAME_CONFIG['seeds'][data['seed']]['name'] + " seeds to sell.")

    # making changes to game_state
    game_state['seedCounts'][data['seed']] -= 1
    game_state['resources']['cash'] += GAME_CONFIG['seeds'][data['seed']]['sellCost']

    # saving new game_state
    save_state(data['slug'], game_state)

    return jsonify(game_state)


@app.route('/action/sow', methods = ['GET', 'POST'])
def sow():
    # requesting sow action data from script (seed, x, y, slug)
    data = request.json

    # loading game_state
    game_state = load_state(data['slug'])

    if data['password'] != game_state['password']:
        raise Exception("Invalid password")

    # safety check
    if game_state['seedCounts'][data['seed']] <= 0:
        raise Exception("No " + GAME_CONFIG['seeds'][data['seed']]['name'] + " seeds to plant.")

    # making changes to game_state
    game_state['seedCounts'][data['seed']] -= 1
    plot = get_plot(game_state, data['x'], data['y'])
    plot['seedType'] = data['seed']
    plot['sowTime'] = int(round(time.time() * 1000))

    # saving new game_state
    save_state(data['slug'], game_state)

    return jsonify(game_state)


@app.route('/action/harvest', methods = ['GET', 'POST'])
def harvest():
    # requesting harvest action data from script (x, y, slug)
    data = request.json

    # loading game_state
    game_state = load_state(data['slug'])

    if data['password'] != game_state['password']:
        raise Exception("Invalid password")

    # making changes to game_state
    plot = get_plot(game_state, data['x'], data['y'])
    seedType = plot['seedType']

    growing_time = int(round(time.time() -  plot['sowTime'] / 1000))
    if GAME_CONFIG['seeds'][seedType]['harvestTimeSeconds'] > growing_time:
        raise Exception("no cheats >:(")

    game_state['seedCounts'][seedType] += GAME_CONFIG['seeds'][seedType]['harvestYield']
    plot['seedType'] = 0

    # saving new game_state
    save_state(data['slug'], game_state)

    return jsonify(game_state)


@app.route('/action/unlock', methods = ['GET', 'POST'])
def unlock():
    # requesting unlock action data from script (x, y)
    data = request.json

    # loading game_state
    game_state = load_state(data['slug'])

    # safety check
    if data['password'] != game_state['password']:
        raise Exception("Invalid password")
    if game_state['resources']['cash'] < GAME_CONFIG['plotPrice'] * GAME_CONFIG['plotMultiplier'] ** game_state['unlockCount']:
        raise Exception("Not enough cash.")

    # making changes to game_state
    plot = get_plot(game_state, data['x'], data['y'])
    plot['locked'] = 0
    game_state['resources']['cash'] -= GAME_CONFIG['plotPrice'] * GAME_CONFIG['plotMultiplier'] ** game_state['unlockCount']
    game_state['unlockCount'] += 1

    # saving new game_state
    save_state(data['slug'], game_state)

    return jsonify(game_state)

@app.route('/styles.css')
def styles():
    return render_template('styles.css');

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE, port=int(os.environ['PORT']), host='0.0.0.0')
