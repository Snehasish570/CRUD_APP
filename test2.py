import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_access_cookies
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from dotenv import load_dotenv  
from models import db, Item, User
from flask_caching import Cache


load_dotenv()

app = Flask(__name__)
CORS(app,
    supports_credentials=True,
)



app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_TOKEN_LOCATION']=['cookies']

app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'

app.config['JWT_COOKIE_HTTPONLY'] = True


jwt = JWTManager(app)
db.init_app(app)
cache = Cache(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        hashed_pw=generate_password_hash('1234')
        u = User(username='admin', password=hashed_pw)
        db.session.add(u)
        db.session.commit()



@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    hashed_password=generate_password_hash(password)

    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()


    if user and check_password_hash(user.password, password):
        token = create_access_token(identity=username)
        response=jsonify({"msg":"Login Successful"})
        set_access_cookies(response, token)
        return response, 200
    
    
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/logout', methods=['POST'])

def logout():
    response = jsonify({"msg": "logout successful"})
    unset_access_cookies(response)
    return response, 200



@app.route('/api/items', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60,key_prefix=lambda:f'{get_jwt_identity()}_all_items')
def get_items():
    items = Item.query.all()
    return jsonify([i.to_dict() for i in items])

@app.route('/api/items/<int:item_id>', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60,key_prefix=lambda: f'item_{get_jwt_identity()}_{request.view_args["item_id"]}')
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())

@app.route('/api/items', methods=['POST'])
@jwt_required()
def create_item():
    data = request.get_json()
    name = data.get('name')
    mail = data.get('mail')

    if not name or not mail:
        return jsonify({'error': 'Name and Email are required'}), 400

    new_item = Item(name=name, mail=mail)
    db.session.add(new_item)
    try:
        db.session.commit()
        cache.delete(f'{get_jwt_identity()}_all_items')
        return jsonify(new_item.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 400

@app.route('/api/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json()
    item.name = data.get('name', item.name)
    item.mail = data.get('mail', item.mail)
    
    try:
        db.session.commit()
        cache.delete(f'{get_jwt_identity()}_all_items')
        cache.delete(f'item_{get_jwt_identity()}_{item_id}')
        return jsonify(item.to_dict())
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 400

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    cache.delete(f'{get_jwt_identity()}_all_items')
    cache.delete(f'item_{get_jwt_identity()}_{item_id}')
    return jsonify({'result': True, 'message': 'Item deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)
