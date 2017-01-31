#!usr/bin/env python

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/game')
def default():
    return render_template('frontEndLayout.html')

app.run(debug=True,port=8000)