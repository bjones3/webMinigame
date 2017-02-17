#!usr/bin/env python

from flask import Flask, render_template, request, jsonify
import json, os, re, time

app = Flask(__name__)

GAME_CONFIG = {
    'startingCash': 10,
    'seeds': {
        'chili': {
            'name': "Chili Pepper",
            'imageSmall': "/static/chilipepper_s.png",
            'imageMedium': "/static/chilipepper_m.png",
            'imageLarge': "/static/chilipepper_l.png",
            'buyCost': 3,
            'sellCost': 1,
            'harvestYield': 2,
            'harvestTimeSeconds': 40
        },
        'broc': {
            'name': "Broccoli",
            'imageSmall': "/static/broccoli_s.png",
            'imageMedium': "/static/broccoli_m.png",
            'imageLarge': "/static/broccoli_l.png",
            'buyCost': 5,
            'sellCost': 1,
            'harvestYield': 3,
            'harvestTimeSeconds': 60
        },
        'cauli': {
            'name': "Cauliflower",
            'imageSmall': "/static/cauliflower_s.png",
            'imageMedium': "/static/cauliflower_m.png",
            'imageLarge': "/static/cauliflower_l.png",
            'buyCost': 8,
            'sellCost': 2,
            'harvestYield': 3,
            'harvestTimeSeconds': 90
        },
        'beet': {
            'name': "Beet",
            'imageSmall': "/static/beet_s.png",
            'imageMedium': "/static/beet_m.png",
            'imageLarge': "/static/beet_l.png",
            'buyCost': 13,
            'sellCost': 3,
            'harvestYield': 3,
            'harvestTimeSeconds': 120
        },
        'e': {
            'name': "Eggplant",
            'imageSmall': "/static/eggplant_s.png",
            'imageMedium': "/static/eggplant_m.png",
            'imageLarge': "/static/eggplant_l.png",
            'buyCost': 21,
            'sellCost': 5,
            'harvestYield': 4,
            'harvestTimeSeconds': 180
        },
        'p': {
            'name': "Potato",
            'imageSmall': "/static/potato_s.png",
            'imageMedium': "/static/potato_m.png",
            'imageLarge': "/static/potato_l.png",
            'buyCost': 34,
            'sellCost': 8,
            'harvestYield': 3,
            'harvestTimeSeconds': 300
        },
        'garlic': {
            'name': "Garlic",
            'imageSmall': "/static/garlic_s.png",
            'imageMedium': "/static/garlic_m.png",
            'imageLarge': "/static/garlic_l.png",
            'buyCost': 55,
            'sellCost': 13,
            'harvestYield': 4,
            'harvestTimeSeconds': 450
        },
        'bell': {
            'name': "Bell Pepper",
            'imageSmall': "/static/bellpepper_s.png",
            'imageMedium': "/static/bellpepper_m.png",
            'imageLarge': "/static/bellpepper_l.png",
            'buyCost': 89,
            'sellCost': 21,
            'harvestYield': 4,
            'harvestTimeSeconds': 900
        },
        'carrot': {
            'name': "Carrot",
            'imageSmall': "/static/carrot_s.png",
            'imageMedium': "/static/carrot_m.png",
            'imageLarge': "/static/carrot_l.png",
            'buyCost': 144,
            'sellCost': 34,
            'harvestYield': 4,
            'harvestTimeSeconds': 1800
        },
        'beans': {
            'name': "Beans",
            'imageSmall': "/static/beans_s.png",
            'imageMedium': "/static/beans_m.png",
            'imageLarge': "/static/beans_l.png",
            'buyCost': 233,
            'sellCost': 55,
            'harvestYield': 4,
            'harvestTimeSeconds': 7200
        },
        'turnip': {
            'name': "Turnip",
            'imageSmall': "/static/turnip_s.png",
            'imageMedium': "/static/turnip_m.png",
            'imageLarge': "/static/turnip_l.png",
            'buyCost': 377,
            'sellCost': 89,
            'harvestYield': 3,
            'harvestTimeSeconds': 28800
        },
        'leek': {
            'name': "Leek",
            'imageSmall': "/static/leek_s.png",
            'imageMedium': "/static/leek_m.png",
            'imageLarge': "/static/leek_l.png",
            'buyCost': 610,
            'sellCost': 144,
            'harvestYield': 1,
            'harvestTimeSeconds': 86400
        },
        'tomato': {
            'name': "Tomato",
            'imageSmall': "/static/tomato_s.png",
            'imageMedium': "/static/tomato_m.png",
            'imageLarge': "/static/tomato_l.png",
            'buyCost': 987,
            'sellCost': 233,
            'harvestYield': 0,
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


@app.route('/game-state/<slug>', methods = ['GET', 'POST'])
def state(slug):
    regex = re.compile("^[a-z]+$")
    x = regex.match(slug)
    if x is False:
        raise Exception("Invalid characters")
    body = request.json
    password = body['password']
    if os.path.exists('saves/' + slug + '.json'):
        data = load_state(slug)
        if password == data['password']:
            return jsonify(data)
        else:
            return("Invalid password", 401)
    else:
        game_state = {
            'cash': 10,
            'slug': slug,
            'password': password,
            'chili': 0,
            'broc': 0,
            'cauli': 0,
            'beet': 0,
            'e': 0,
            'p': 0,
            'garlic': 0,
            'bell': 0,
            'carrot': 0,
            'beans': 0,
            'turnip': 0,
            'leek': 0,
            'tomato': 0
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
    app.run(debug=True, port=int(os.environ['PORT']))