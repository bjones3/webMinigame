#!usr/bin/env python

from flask import Flask, render_template, request, jsonify
import os
import re
from werkzeug.exceptions import Unauthorized, BadRequest

import rules
from game import GameState
import db

app = Flask(__name__)

if os.environ.get('DEBUG_MODE') == '1':
    DEBUG_MODE = True
else:
    DEBUG_MODE = False

CONFIG = rules.Config(DEBUG_MODE)


def make_response(game_state, message=None, recipes=None):
    response = {
        'state': game_state.get_client_data()
    }
    if message is not None:
        response['message'] = message
    if recipes is not None:
        response['recipes'] = recipes
    return jsonify(response)


def valid_chars(slug):
    regex = re.compile('^[a-z]+$')
    x = regex.match(slug)
    if x is False:
        raise BadRequest("Invalid characters")


@app.route('/')
def default():
    leaderboard_data = db.get_leaderboard_data()
    return render_template('defaultPage.html', leaderboard=leaderboard_data)


@app.route('/game/')
def game():
    return render_template('frontEndLayout.html', seeds=CONFIG.seeds, resources=CONFIG.resources,
                           field_width=CONFIG.general['field_width'], field_height=CONFIG.general['field_height'])


@app.route('/admin/', methods=['GET'])
def admin_get():
    return render_template('admin_login.html')


@app.route('/admin/', methods=['POST'])
def admin_post():
    data = db.get_admin_data()
    if request.form['password'] != data['password']:
        raise Unauthorized("Invalid password")
    return render_template('admin.html', data=data, recipes=CONFIG.recipes, seeds=CONFIG.seeds)


@app.route('/game-config')
def game_config():
    collapsed_config = {}
    collapsed_config.update(CONFIG.general)
    collapsed_config['seeds'] = CONFIG.seeds
    collapsed_config['resources'] = CONFIG.resources
    return jsonify(collapsed_config)


@app.route('/game-state/<slug>', methods=['GET', 'POST'])
def state(slug):
    valid_chars(slug)
    body = request.json
    if body['newOrLoad'] == 'new':
        game_state = GameState.new(slug, body['password'])
    if body['newOrLoad'] == 'load':
        game_state = GameState.load(slug, body['password'])
    db.save(slug, game_state.data)
    return make_response(game_state)


@app.route('/action/buy', methods=['GET', 'POST'])
def buy():
    data = request.json  # data={slug,recipe_id,password}
    game_state = GameState.load(data['slug'], data['password'])
    message = game_state.buy(data['recipe_id'])
    db.save(data['slug'], game_state.data)
    return make_response(game_state, message)


@app.route('/action/sell', methods=['GET', 'POST'])
def sell():
    data = request.json  # data={slug,seed,password}
    game_state = GameState.load(data['slug'], data['password'])
    message = game_state.sell(data['seed'])
    game_state.check_cash()
    db.save(data['slug'], game_state.data)
    return make_response(game_state, message)


@app.route('/action/sow', methods=['GET', 'POST'])
def sow():
    data = request.json  # data={slug,seed,x,y,password}
    game_state = GameState.load(data['slug'], data['password'])
    message = game_state.sow(data['seed'], data['x'], data['y'])
    db.save(data['slug'], game_state.data)
    return make_response(game_state, message)


@app.route('/action/harvest', methods=['GET', 'POST'])
def harvest():
    data = request.json  # data={slug,x,y,password}
    game_state = GameState.load(data['slug'], data['password'])
    message = game_state.harvest(data['x'], data['y'])
    game_state.add_recipes()
    db.save(data['slug'], game_state.data)
    return make_response(game_state, message)


@app.route('/action/unlock', methods=['GET', 'POST'])
def unlock():
    data = request.json  # data={slug,x,y,password}
    game_state = GameState.load(data['slug'], data['password'])
    message = game_state.unlock(data['x'], data['y'])
    game_state.check_cash()
    db.save(data['slug'], game_state.data)
    return make_response(game_state, message)


@app.route('/recipe', methods=['POST'])
def recipe():
    data = request.json  # data={slug,password}
    game_state = GameState.load(data['slug'], data['password'])

    known_recipes = {}
    for recipe_id in CONFIG.recipes:
        if game_state.is_known_recipe(recipe_id):
            known_recipes[recipe_id] = CONFIG.recipes[recipe_id]
    return make_response(game_state, recipes=known_recipes)


@app.route('/styles.css')
def styles():
    return render_template('styles.css')


if __name__ == "__main__":
    app.run(debug=DEBUG_MODE, port=int(os.environ['PORT']), host='0.0.0.0')
