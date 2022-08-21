from crypt import methods
from itertools import product
import json
from math import prod
from flask import Flask, request, jsonify, make_response, Response
from flask_sqlalchemy import SQLAlchemy
import datetime
import requests
import uuid

from config import DISCOUNT

app = Flask(__name__)
# app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cart.db'
app.config['SECRET_KEY'] = 'mykey3'


class Cart(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   product_id = db.Column(db.String(50))
   quantity = db.Column(db.Integer)
   user_id = db.Column(db.Integer)

@app.route('/cart/user/<user_id>', methods=['GET'])
def get_all_cart_item(user_id):
    carts = Cart.query.filter_by(user_id=user_id).all()
    if not carts:
        return jsonify({'message': 'cart is empty'})
    
    output = []

    for card in carts:
        card_data = {}
        card_data['id'] = card.id
        card_data['productId'] = card.product_id
        card_data['userId'] = card.user_id
        card_data['qunatity'] = card.quantity
        output.append(card_data)

    response = jsonify({'cart' : output})
    return response

@app.route('/cart/product/<user_id>/<product_id>/<quantity>', methods=['POST'])
def add_product(user_id, product_id, quantity):
    print(user_id + " "  + product_id)
    new_cart = Cart(product_id=product_id, quantity=int(quantity), user_id=int(user_id))
    db.session.add(new_cart)
    db.session.commit()

    return "product added"

@app.route('/cart/total/<user_id>', methods=['GET'])
def get_total_payments(user_id):
    carts = Cart.query.filter_by(user_id=user_id).all()
    sum = 0
    for cart in carts:
        cart.product_id
        price = requests.get('http://192.168.1.8:5001/price/' + str(cart.product_id))
        temp = (int(price.json()['message'])*(cart.quantity))
        discount = DISCOUNT*(cart.quantity//50)
        temp = temp - (temp*discount)//100
        sum = sum + temp
        
    
    return jsonify({'total' : sum})


@app.route('/cart/<user_id>', methods=['DELETE'])
def delete_cart(user_id):
    carts = Cart.query.filter_by(user_id=user_id).all()

    if not carts:
        app.logger.error('No Cart Found')
        return jsonify({'message':'No cart found'}), 404
    for cart in carts:
        db.session.delete(cart)
        db.session.commit()

    return jsonify({'message': 'cart deleted successfully'})
