from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_cors import CORS
import pyrebase
import json

app = Flask(__name__)
CORS(app, origins="http://127.0.0.1:3000", resources={r'/*': {'origins': '*'}})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/food_results', methods=['POST'])
def food_results():
    config_file = "config.json"
    with open(config_file) as configfile:
        config = json.load(configfile)
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    menu = db.child("menu").get().val()
    foods = list()
    for food_item in menu.keys():
        foods.append(food_item)
        
    return jsonify(success=True, message=foods), 200

@app.route('/search', methods=['POST'])
def food_info():
    food_name = request.json['dish']
    allergy = request.json['allergen'].lower()
    config_file = "config.json"
    with open(config_file) as configfile:
        config = json.load(configfile)
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    menu = db.child("menu").get().val()
    if allergy in menu[food_name][0]:
        return jsonify(success=True, message=f"{food_name.title()} contains {allergy.title()}"), 200
    else:
        return jsonify(success=True, message=f"{food_name.title()} does not contain {allergy.title()}"), 200

@app.route('/ingredients', methods=['POST'])
def ingredients():
    food_name = request.json['dish']
    config_file = "config.json"
    with open(config_file) as configfile:
        config = json.load(configfile)
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    menu = db.child("menu").get().val()
    ingredients = menu[food_name][0]
    return jsonify(success=True, message=ingredients), 200 

if __name__ == "__main__":
    app.run(debug=True, port=3000)
    
