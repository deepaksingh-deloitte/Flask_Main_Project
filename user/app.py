from crypt import methods
from flask import Flask, request, jsonify, make_response, Response
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'mykey'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(120), index=True, unique=True)
    # email = db.Column(db.String(120), index=True, unique=True)
    # name = db.Column(db.String(50))
    password = db.Column(db.String(80))

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            app.logger.error('Token is missing!')
            return jsonify({'message' : 'Token is missing!'}), 401
        data = jwt.decode(token, 'mykey', algorithms=['HS256'])
        print(data)
        try: 
            data = jwt.decode(token, 'mykey', algorithms=['HS256'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            app.logger.error('Token is invalid!')
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/users', methods=['GET'])
@token_required
def get_all_users(current_user):

    app.logger.info('get_all_users')

    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['username'] = user.username
        user_data['password'] = user.password
        output.append(user_data)

    response = jsonify({'users' : output})
    return response

@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):

    app.logger.info('get_one_user')
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'}), 401

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'}), 404

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({'user' : user_data})

@app.route('/register', methods=['POST'])
def register_user():

    app.logger.info('register_user')
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(public_id=str(uuid.uuid4()), username=data['username'],password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    response  = jsonify({'message' : 'New user created!'}), 201
    return response


@app.route('/currentuser', methods=['GET'])
@token_required
def get_user(current_user):
    
    app.logger.info('get_user')
    user_data = {}
    user_data['id'] = current_user.id
    user_data['public_id'] = current_user.public_id
    user_data['username'] = current_user.username
    response = jsonify(user_data)
    return response


@app.route('/login', methods=['POST'])
def login():

    app.logger.info('login')
    data = request.get_json()
    username = data['username']
    password = data['password']
    print(username + " " + password)
    response = "None"
    if not username or not password:
        app.logger.error('Could not verify, Incorrect username or password')
        response = make_response('Could not verify, Incorrect username or password', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user = User.query.filter_by(username=username).first()
    

    if not user:
        app.logger.error('Could not verify')
        response = jsonify({'message': 'User not found'}), 404
        return response
       
    if user.password == password:
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=120)}, app.config['SECRET_KEY'])
        # response = jsonify({'token' : token.decode('UTF-8')})
        return jsonify({'tok': token})

    return "user not found", 404


@app.route('/add', methods=['POST'])
@token_required
def add_product(current_user):
    app.logger.info('current_user')
    res = requests.post('http://192.168.1.8:5001/add', json=request.get_json())
    return res.json(), 201

@app.route('/products', methods=['GET'])
@token_required
def get_all_product(current_user):
    res = requests.get('http://192.168.1.8:5001/products')
    return res.json()

@app.route('/products/rating', methods=['GET'])
@token_required
def product_by_rating(current_user):
    res = requests.get('http://192.168.1.8:5001/products/rating')
    return res.json()

@app.route('/products/price', methods=['GET'])
@token_required
def product_by_price(current_user):
    res = requests.get('http://192.168.1.8:5001/products/price')
    return res.json()


@app.route('/product/filter', methods=['GET'])
@token_required
def filter_product():
    res = requests.get('http://192.168.1.8:5001/products/filter')
    return res.json()

@app.route('/cart/data', methods=['GET'])
@token_required
def all_cart(current_user):
    res = requests.get('http://192.168.1.8:5002/cart/user/' + str(current_user.id))
    return res.json()

@app.route('/product/to/cart', methods=['POST'])
@token_required
def add_to_cart(current_user):
    data = request.get_json()
    product_id = data['product_id']
    quantity = data['quantity']
    res = requests.post('http://192.168.1.8:5002/cart/product/' + str(current_user.id)+"/" + str(product_id)+"/" + str(quantity))
    return "product added to cart"
    
@app.route('/checkout', methods=['POST', 'GET'])
@token_required
def checkout(current_user):
    res = requests.get('http://192.168.1.8:5002/cart/total/' + str(current_user.id))
    if res.json()['total'] == 0:
        return jsonify({'message': 'cart is empty'})
    discounted_total = requests.get('http://192.168.1.8:5005/discount/' + str(res.json()['total']))
    # make payment
    result = requests.post('http://192.168.1.8:5003/make/payment/' + str(current_user)+"/"+str(discounted_total.json()['coupon']['total'])+"/"+str(discounted_total.json()['coupon']['code']))
    if result.json()['status'] == 'success':
        # delete cart
        result = requests.delete('http://192.168.1.8:5002/cart/'+str(current_user.id))
        return jsonify({'message': 'payment successfull'}) 
    return discounted_total.json()

@app.route('/payments', methods=['GET'])
@token_required
def get_all_payments(current_user):
    res = requests.get('http://192.168.1.8:5003/payments/' + str(current_user.id))
    return res.json()




