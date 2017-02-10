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
            'harvestYield': 3,
            'harvestTimeSeconds': 40
        },
        'b': {
            'name': "Broccoli",
            'imageSmall': "/static/broccoli_s.jpg",
            'imageMedium': "/static/broccoli_m.jpg",
            'imageLarge': "/static/broccoli_l.jpg",
            'buyCost': 6,
            'sellCost': 2,
            'harvestYield': 6,
            'harvestTimeSeconds': 120
        },
        'c': {
            'name': "Cabbage",
            'imageSmall': "/static/cabbage_s.jpg",
            'imageMedium': "/static/cabbage_m.jpg",
            'imageLarge': "/static/cabbage_l.jpg",
            'buyCost': 12,
            'sellCost': 3,
            'harvestYield': 15,
            'harvestTimeSeconds': 360
        }
    }
}


@app.route('/')
def default():
    return render_template('defaultPage.html')


@app.route('/game/')
def game():
    return render_template('frontEndLayout.html')


@app.route('/game-config')
def game_config():
    return jsonify(GAME_CONFIG)


@app.route('/game-state/<slug>')
def game_state(slug):
    regex = re.compile("^[a-z]+$")
    x = regex.match(slug)
    if x is False:
        raise Exception("Invalid characters")

    if os.path.exists('saves/' + slug + '.json'):
        with open('saves/' + slug + '.json', 'r') as file:
            data = json.load(file)
        return jsonify(data)
    else:
        game_state = {
            'cash': 10,
            'slug' : slug,
            'a': 0,
            'b': 0,
            'c': 0,
        }
        for i in range(3):
            for j in range(3):
                game_state[("plot" + str(i) + str(j))] = {'seedType': 0, 'sowTime': 0}

    with open('saves/' + slug + '.json', 'w') as file:
        json.dump(game_state, file, indent = 4)
    return jsonify(game_state)


@app.route('/save/<slug>', methods = ['GET', 'POST'])
def save_game_state(slug):
    regEx = re.compile("^[a-z]+$")
    x = regEx.match(slug)
    if x is False:
        raise Exception("Invalid characters")

    game_state = request.json
    with open('saves/' + slug + '.json', 'w') as file:
        json.dump(game_state, file, indent = 4)
    return jsonify({})


@app.route('/action/buy', methods = ['GET', 'POST'])
def buy():
    # requesting buy action data from script (seed, slug)
    buy_data = request.json

    # loading game_state
    with open('saves/' + buy_data['slug'] + '.json', 'r') as file:
        game_state = json.load(file)

    # making changes to game_state
    game_state[buy_data['seed']] += 1
    game_state['cash'] -= GAME_CONFIG['seeds'][buy_data['seed']]['buyCost']

    # saving new game_state
    with open('saves/' + buy_data['slug'] + '.json', 'w') as file:
        json.dump(game_state, file, indent=4)

    return jsonify(game_state)


@app.route('/action/sell', methods = ['GET', 'POST'])
def sell():
    # requesting sell action data from script (seed, slug)
    sell_data = request.json

    # loading game_state
    with open('saves/' + sell_data['slug'] + '.json', 'r') as file:
        game_state = json.load(file)

    # making changes to game_state
    game_state[sell_data['seed']] -= 1
    game_state['cash'] += GAME_CONFIG['seeds'][sell_data['seed']]['sellCost']

    # saving new game_state
    with open('saves/' + sell_data['slug'] + '.json', 'w') as file:
        json.dump(game_state, file, indent=4)

    return jsonify(game_state)


@app.route('/action/sow', methods = ['GET', 'POST'])
def sow():
    # requesting sow action data from script (seed, x, y, slug)
    sow_data = request.json

    # loading game_state
    with open('saves/' + sow_data['slug'] + '.json', 'r') as file:
        game_state = json.load(file)

    # making changes to game_state
    game_state[sow_data['seed']] -= 1
    game_state["plot" + str(sow_data['x']) + str(sow_data['y'])]['seedType'] = sow_data['seed']
    game_state["plot" + str(sow_data['x']) + str(sow_data['y'])]['sowTime'] = int(round(time.time() * 1000))

    # saving new game_state
    with open('saves/' + sow_data['slug'] + '.json', 'w') as file:
        json.dump(game_state, file, indent = 4)

    return jsonify(game_state)


@app.route('/action/harvest', methods = ['GET', 'POST'])
def harvest():
    # requesting harvest action data from script (x, y, slug)
    harvest_data = request.json

    # loading game_state
    with open('saves/' + harvest_data['slug'] + '.json', 'r') as file:
        game_state = json.load(file)

    # making changes to game_state
    seed = game_state["plot" + str(harvest_data['x']) + str(harvest_data['y'])]['seedType']
    game_state[seed] += GAME_CONFIG['seeds'][seed]['harvestYield']
    game_state["plot" + str(harvest_data['x']) + str(harvest_data['y'])]['seedType'] = 0

    # saving new game_state
    with open('saves/' + harvest_data['slug'] + '.json', 'w') as file:
        json.dump(game_state, file, indent = 4)

    return jsonify(game_state)

app.run(debug=True,port=8000)