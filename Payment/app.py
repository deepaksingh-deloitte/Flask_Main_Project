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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payment.db'
app.config['SECRET_KEY'] = 'mykey4'


class Payment(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   payment = db.Column(db.Integer)
   user_id = db.Column(db.Integer)
   timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow())
   code = db.Column(db.String(120))

@app.route('/make/payment/<user_id>/<amount>/<code>', methods=['POST'])
def make_payment(user_id, amount,code):
    print(user_id + " " + amount)
    new_payment = Payment(payment=amount, user_id=user_id, code=code)
    db.session.add(new_payment)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/payments/<user_id>', methods=['GET'])
def all_payments(user_id):
    payments = Payment.query.all()
    # make query for a user
    output = [] 
    for p in payments:
        temp = {}
        temp['amount'] = p.payment
        temp['timestamp'] = p.timestamp
        temp['user_id'] = p.user_id
        temp['code'] = p.code

        output.append(temp)
    
    return jsonify({'output':output})
