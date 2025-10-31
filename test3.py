import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from dotenv import load_dotenv
from models import db, Item, User
from flask_caching import Cache

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

# SECRET KEY REQUIRED FOR SESSION
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(hours=1)

# DB CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# REDIS CACHE
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'

db.init_app(app)
cache = Cache(app)

# Initialize DB
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        hashed_pw = generate_password_hash('1234')
        u = User(username='admin', password=hashed_pw)
        db.session.add(u)
        db.session.commit()


def is_logged_in():
    return session.get("logged_in") == True



@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    hashed_pass = generate_password_hash(password)
    new_user = User(username=username, password=hashed_pass)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201



@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        session.permanent = True 
        session["logged_in"] = True
        session["username"] = username
        session["user_id"] = user.id

        return jsonify({'message': 'Login successful'}), 200

    return jsonify({'error': 'Invalid username or password'}), 401



@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200



@app.route('/api/items', methods=['GET'])
def get_items():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    cache_key = f"{session['username']}_all_items"

    @cache.cached(timeout=60, key_prefix=cache_key)
    def fetch_items():
        return [i.to_dict() for i in Item.query.all()]

    return jsonify(fetch_items())


@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    cache_key = f"item_{session['username']}_{item_id}"

    @cache.cached(timeout=60, key_prefix=cache_key)
    def fetch_item():
        item = Item.query.get_or_404(item_id)
        return item.to_dict()

    return jsonify(fetch_item())



@app.route('/api/items', methods=['POST'])
def create_item():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    name = data.get('name')
    mail = data.get('mail')

    if not name or not mail:
        return jsonify({'error': 'Name and Email required'}), 400

    new_item = Item(name=name, mail=mail)
    db.session.add(new_item)

    try:
        db.session.commit()
        cache.delete(f"{session['username']}_all_items")
        return jsonify(new_item.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 400



@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    item = Item.query.get_or_404(item_id)
    data = request.get_json()

    item.name = data.get('name', item.name)
    item.mail = data.get('mail', item.mail)

    try:
        db.session.commit()
        cache.delete(f"{session['username']}_all_items")
        cache.delete(f"item_{session['username']}_{item_id}")
        return jsonify(item.to_dict())
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 400



@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()

    cache.delete(f"{session['username']}_all_items")
    cache.delete(f"item_{session['username']}_{item_id}")

    return jsonify({'result': True, 'message': 'Item deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)
