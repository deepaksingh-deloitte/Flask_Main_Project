from crypt import methods
from itertools import product
from math import prod
from flask import Flask, request, jsonify, make_response, Response
from flask_sqlalchemy import SQLAlchemy
import datetime
import requests
import uuid


app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coupon.db'
app.config['SECRET_KEY'] = 'mykey5'


class Coupon(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   code = db.Column(db.String(120), index=True, unique=True)
   discount = db.Column(db.Integer)

@app.route('/')
def home():
    return "h"

@app.route('/add/coupon', methods=['POST'])
def add_coupon():
    data = request.get_json()
    code = data['code']
    discount = data['discount']

    new_coupon = Coupon(code = code, discount=discount)
    db.session.add(new_coupon)
    db.session.commit()

    response  = jsonify({'message' : 'New Coupon Created!'}), 201
    return response

@app.route('/coupons', methods=['GET'])
def get_all_coupon():
    coupons = Coupon.query.all()

    output = []

    for coupon in coupons:
        coupon_data = {}
        coupon_data['id'] = coupon.id
        coupon_data['code'] = coupon.code
        # print(coupon.discount)
        coupon_data['discount'] = coupon.discount
        output.append(coupon_data)

    response = jsonify({'coupon' : output})
    return response

@app.route('/discount/<total>', methods=['GET'])
def get_discounted_price(total):
    coupons = Coupon.query.all()
    coupon_data = {}

    for coupon in coupons:
        coupon_data['id'] = coupon.id
        coupon_data['code'] = coupon.code
        coupon_data['discount'] = coupon.discount
        break
    total = int(total)
    final_price = total - (total*int(coupon.discount))/100
    res = {}
    res['code'] = coupon_data['code']
    res['total'] = final_price

    response = jsonify({'coupon' : res})
    return response

