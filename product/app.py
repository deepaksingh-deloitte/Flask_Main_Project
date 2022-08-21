from crypt import methods
from flask import Flask, request, jsonify, make_response, Response
from flask_sqlalchemy import SQLAlchemy
import datetime
import uuid
import requests


app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product.db'
app.config['SECRET_KEY'] = 'mykey2'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(120), index=True)
    category = db.Column(db.String(120), index=True)
    price = db.Column(db.Integer, index=True)
    seller = db.Column(db.String(120), index=True)
    quantity = db.Column(db.Integer, index=True)
    rating = db.Column(db.Integer, index=True)

@app.route('/products', methods=['GET'])
def get_allproduct():
    products = Product.query.all()
    output = []

    for product in products:
        prod = {}
        prod['public_id'] = product.public_id
        prod['name'] = product.name
        prod['seller'] = product.seller
        prod['category'] = product.category
        prod['quantity'] = product.quantity
        prod['amount'] = product.price
        prod['rating']=product.rating
        output.append(prod)

    response = jsonify({'product' : output})
    return response

@app.route('/products/rating', methods=['GET'])
def sort_product_by_rating():
    sorted_product = Product.query.order_by(Product.rating.desc()).all()

    output = []

    for product in sorted_product:
        prod = {}
        prod['public_id'] = product.public_id
        prod['name'] = product.name
        prod['seller'] = product.seller
        prod['category'] = product.category
        prod['quantity'] = product.quantity
        prod['amount'] = product.price
        prod['rating']=product.rating
        output.append(prod)

    response = jsonify({'product' : output})
    return response

@app.route('/products/price', methods=['GET'])
def sort_product_by_price():
    sorted_product = Product.query.order_by(Product.price.desc()).all()

    output = []

    for product in sorted_product:
        prod = {}
        prod['public_id'] = product.public_id
        prod['name'] = product.name
        prod['seller'] = product.seller
        prod['category'] = product.category
        prod['quantity'] = product.quantity
        prod['amount'] = product.price
        prod['rating']=product.rating
        output.append(prod)

    response = jsonify({'product' : output})
    return response

@app.route('/product/filter', methods=['GET'])
def filter_product():
    args = request.args
    products = Product.query.filter(Product.category.ilike(args['by']))
    
    output = []

    for product in products:
        prod = {}
        prod['public_id'] = product.public_id
        prod['name'] = product.name
        prod['seller'] = product.seller
        prod['category'] = product.category
        prod['quantity'] = product.quantity
        prod['amount'] = product.price
        prod['rating']=product.rating
        output.append(prod)

    response = jsonify({'product' : output})
    return response

@app.route('/add', methods=['POST'])
def add_product():
    data = request.get_json()

    new_product = Product(public_id=str(uuid.uuid4()), name=data['name'],category = data['category'],price = data['price'],seller = data['seller'],quantity = data['quantity'],rating=data['rating'])
    
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message' : "Product added!"}), 201

@app.route('/price/<product_id>', methods=['GET'])
def get_price(product_id):
    product = Product.query.filter_by(public_id=product_id).first()
    return jsonify({'message' : product.price})

