#!usr/bin/env python

from flask import Flask, render_template, request, jsonify
import json, os, re, time
import psycopg2
import urlparse

import game_config

app = Flask(__name__)

GAME_CONFIG = game_config.get_config()

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

def load_state(slug):
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT game_state FROM game_states WHERE slug = %s;",
                           [slug])
            row = cursor.fetchone()
            if not row:
                return None
            return row[0]

def save_state(slug, game_state):
    json_game_state = json.dumps(game_state, indent=4)
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO game_states (slug, game_state) VALUES (%s, %s) ON CONFLICT (slug) DO UPDATE SET game_state=%s;",
                           [slug, json_game_state, json_game_state])



def get_plot(game_state, x, y):
    return game_state["plot" + str(x) + str(y)]


@app.route('/')
def default():
    return render_template('defaultPage.html')


@app.route('/game/')
def game():
    return render_template('frontEndLayout.html', seeds = GAME_CONFIG['seeds'])


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
        if password == data['password']:
            return jsonify(data)
        else:
            return("Invalid password", 401)
    else:
        game_state = {
            'cash': GAME_CONFIG['starting_cash'],
            'slug': slug,
            'password': password,
            'a': 0,
            'b': 0,
            'c': 0,
            'd': 0,
            'e': 0,
            'f': 0,
            'g': 0,
            'h': 0,
            'i': 0,
            'j': 0,
            'k': 0,
            'l': 0,
            'm': 0
        }
        for i in range(3):
            for j in range(3):
                game_state[("plot" + str(i) + str(j))] = {'seedType': 0, 'sowTime': 0}

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
    if game_state['cash'] < GAME_CONFIG['seeds'][buy_data['seed']]['buyCost']:
        raise Exception("Not enough cash.")

    # making changes to game_state
    game_state[buy_data['seed']] += 1
    game_state['cash'] -= GAME_CONFIG['seeds'][buy_data['seed']]['buyCost']

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
    if game_state[data['seed']] <= 0:
        raise Exception("No " + GAME_CONFIG['seeds'][data['seed']]['name'] + " seeds to sell.")

    # making changes to game_state
    game_state[data['seed']] -= 1
    game_state['cash'] += GAME_CONFIG['seeds'][data['seed']]['sellCost']

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
    if game_state[data['seed']] <= 0:
        raise Exception("No " + GAME_CONFIG['seeds'][data['seed']]['name'] + " seeds to plant.")

    # making changes to game_state
    game_state[data['seed']] -= 1
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
    game_state[seedType] += GAME_CONFIG['seeds'][seedType]['harvestYield']
    plot['seedType'] = 0

    # saving new game_state
    save_state(data['slug'], game_state)

    return jsonify(game_state)


@app.route('/styles.css')
def styles():
    return render_template('styles.css');

if __name__ == "__main__":
    if os.environ.get('DEBUG_MODE') == '1':
        debug = True
    else:
        debug = False
    app.run(debug=debug, port=int(os.environ['PORT']), host='0.0.0.0')