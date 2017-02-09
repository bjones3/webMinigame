#!usr/bin/env python

from flask import Flask, render_template, request, jsonify
import json, os, re

app = Flask(__name__)

@app.route('/game/')
def default():
    return render_template('frontEndLayout.html')



@app.route('/game-config')
def game_config():
    return jsonify({
            'startingCash': 10,
            'seeds': {
                'a': {
                    'name': "Alfalfa Sprouts",
                    'imageSmall': "/static/alfalfa_s.jpg",
                    'imageMedium': "/static/alfalfa_m.jpg",
                    'imageLarge': "/static/alfalfa_l.jpg",
                    'buyCost': 3,
                    'sellCost': 1,
                    'harvestYield': 4,
                    'harvestTimeSeconds': 40
                },
                'b': {
                    'name': "Broccoli",
                    'imageSmall': "/static/broccoli_s.jpg",
                    'imageMedium': "/static/broccoli_m.jpg",
                    'imageLarge': "/static/broccoli_l.jpg",
                    'buyCost': 6,
                    'sellCost': 1,
                    'harvestYield': 9,
                    'harvestTimeSeconds': 120
                },
                'c': {
                    'name': "Cabbage",
                    'imageSmall': "/static/cabbage_s.jpg",
                    'imageMedium': "/static/cabbage_m.jpg",
                    'imageLarge': "/static/cabbage_l.jpg",
                    'buyCost': 12,
                    'sellCost': 2,
                    'harvestYield': 10,
                    'harvestTimeSeconds': 10000
                }
            }
        })

@app.route('/game-state/<slug>')
def game_state(slug):
    regEx = re.compile("^[a-z]+$")
    x = regEx.match(slug)
    if x is False:
        raise Exception("Invalid characters")


    if os.path.exists('saves/' + slug + '.json'):
        with open('saves/' + slug + '.json', 'r') as file:
            data = json.load(file)
        return jsonify(data)
    else:

        game_state = {'cash': 10,
            'slug' : slug,
            'a': 0,
            'b': 0,
            'c': 0, }

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

app.run(debug=True,port=8000)