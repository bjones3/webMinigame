#!usr/bin/env python

from flask import Flask, render_template, request, jsonify
import json, os, re, time

app = Flask(__name__)

GAME_CONFIG = {
    'startingCash': 10,
    'seeds': {
        'a': {
            'name': "Alfalfa Sprouts",
            'imageSmall': "/static/alfalfa_s.jpg",
            'imageMedium': "/static/alfalfa_m.jpg",
            'imageLarge': "/static/alfalfa_l.jpg",
            'buyCost': 3,
            'sellCost': 1,
            'harvestYield': 2,
            'harvestTimeSeconds': 40
        },
        'b': {
            'name': "Broccoli",
            'imageSmall': "/static/broccoli_s.jpg",
            'imageMedium': "/static/broccoli_m.jpg",
            'imageLarge': "/static/broccoli_l.jpg",
            'buyCost': 5,
            'sellCost': 1,
            'harvestYield': 3,
            'harvestTimeSeconds': 60
        },
        'c': {
            'name': "Cabbage",
            'imageSmall': "/static/cabbage_s.jpg",
            'imageMedium': "/static/cabbage_m.jpg",
            'imageLarge': "/static/cabbage_l.jpg",
            'buyCost': 8,
            'sellCost': 2,
            'harvestYield': 3,
            'harvestTimeSeconds': 90
        },
        'd': {
            'name': "Daikon",
            'imageSmall': "/static/daikon_s.jpg",
            'imageMedium': "/static/daikon_m.jpg",
            'imageLarge': "/static/daikon_l.jpg",
            'buyCost': 13,
            'sellCost': 3,
            'harvestYield': 3,
            'harvestTimeSeconds': 120
        },
        'e': {
            'name': "Eggplant",
            'imageSmall': "/static/eggplant_s.jpg",
            'imageMedium': "/static/eggplant_m.jpg",
            'imageLarge': "/static/eggplant_l.jpg",
            'buyCost': 21,
            'sellCost': 5,
            'harvestYield': 4,
            'harvestTimeSeconds': 180
        },
        'f': {
            'name': "Fennel",
            'imageSmall': "/static/fennel_s.jpg",
            'imageMedium': "/static/fennel_m.jpg",
            'imageLarge': "/static/fennel_l.jpg",
            'buyCost': 34,
            'sellCost': 8,
            'harvestYield': 3,
            'harvestTimeSeconds': 300
        },
        'g': {
            'name': "Garlic",
            'imageSmall': "/static/garlic_s.jpg",
            'imageMedium': "/static/garlic_m.jpg",
            'imageLarge': "/static/garlic_l.jpg",
            'buyCost': 55,
            'sellCost': 13,
            'harvestYield': 4,
            'harvestTimeSeconds': 450
        },
        'h': {
            'name': "Horseradish",
            'imageSmall': "/static/horseraddish_s.jpg",
            'imageMedium': "/static/horseraddish_m.jpg",
            'imageLarge': "/static/horseradish_l.jpg",
            'buyCost': 89,
            'sellCost': 21,
            'harvestYield': 4,
            'harvestTimeSeconds': 900
        },
        'i': {
            'name': "Iceberg Lettuce",
            'imageSmall': "/static/iceberglettuce_s.jpg",
            'imageMedium': "/static/iceberglettuce_m.jpg",
            'imageLarge': "/static/iceberglettuce_l.jpg",
            'buyCost': 144,
            'sellCost': 34,
            'harvestYield': 4,
            'harvestTimeSeconds': 1800
        },
        'j': {
            'name': "Jicama",
            'imageSmall': "/static/jicama_s.jpg",
            'imageMedium': "/static/jicama_m.jpg",
            'imageLarge': "/static/jicama_l.jpg",
            'buyCost': 233,
            'sellCost': 55,
            'harvestYield': 4,
            'harvestTimeSeconds': 7200
        },
        'k': {
            'name': "Kale",
            'imageSmall': "/static/kale_s.jpg",
            'imageMedium': "/static/kale_m.jpg",
            'imageLarge': "/static/kale_l.jpg",
            'buyCost': 377,
            'sellCost': 89,
            'harvestYield': 3,
            'harvestTimeSeconds': 28800
        },
        'l': {
            'name': "Lemongrass",
            'imageSmall': "/static/lemongrass_s.jpg",
            'imageMedium': "/static/lemongrass_m.jpg",
            'imageLarge': "/static/lemongrass_l.jpg",
            'buyCost': 610,
            'sellCost': 144,
            'harvestYield': 2,
            'harvestTimeSeconds': 86400
        },
        'm': {
            'name': "Mustard Greens",
            'imageSmall': "/static/mustardgreens_s.jpg",
            'imageMedium': "/static/mustardgreens_m.jpg",
            'imageLarge': "/static/mustardgreens_l.jpg",
            'buyCost': 987,
            'sellCost': 233,
            'harvestYield': 2,
            'harvestTimeSeconds': 259200
        }
    }
}


def load_state(slug):
    with open('saves/' + slug + '.json', 'r') as file:
        return json.load(file)


def save_state(slug, game_state):
    with open('saves/' + slug + '.json', 'w') as file:
        json.dump(game_state, file, indent=4)


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


@app.route('/game-state/<slug>')
def state(slug):
    regex = re.compile("^[a-z]+$")
    x = regex.match(slug)
    if x is False:
        raise Exception("Invalid characters")

    if os.path.exists('saves/' + slug + '.json'):
        data = load_state(slug)
        return jsonify(data)
    else:
        game_state = {
            'cash': 10,
            'slug' : slug,
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
    return jsonify(game_state)


@app.route('/action/buy', methods = ['GET', 'POST'])
def buy():
    # requesting buy action data from script (seed, slug)
    buy_data = request.json

    # loading game_state
    game_state = load_state(buy_data['slug'])

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
    app.run(debug=True,port=8000)